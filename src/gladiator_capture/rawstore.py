"""Append-only raw object store and retrieval journal (event contract §2).

The store copies files that are already held into a content-addressed layout.
It performs no network access (DEC-058).
"""

from __future__ import annotations

import hashlib
import json
import shutil
import time
import zipfile
from dataclasses import asdict, dataclass
from pathlib import Path
from typing import Optional


def sha256_file(path: Path) -> str:
    h = hashlib.sha256()
    with open(path, "rb") as fh:
        for chunk in iter(lambda: fh.read(1 << 20), b""):
            h.update(chunk)
    return h.hexdigest()


def sha256_bytes(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


@dataclass
class RawObject:
    raw_id: str
    source_id: str
    source_approval_id: str
    request: str
    retrieved_at_ns: int
    byte_length: int
    media_type: str = "application/octet-stream"
    http_status: Optional[int] = None
    server_last_modified: Optional[str] = None
    server_etag: Optional[str] = None
    published_checksum: Optional[str] = None
    checksum_status: str = "none_published"  # verified | mismatch | none_published
    container_raw_id: Optional[str] = None
    member_path: Optional[str] = None
    supersedes_raw_id: Optional[str] = None
    quarantined: bool = False
    reason: Optional[str] = None


@dataclass
class JournalEntry:
    at_ns: int
    request: str
    outcome: str  # stored | duplicate | quarantined | failed | started | completed
    raw_id: Optional[str] = None
    http_status: Optional[int] = None
    byte_length: Optional[int] = None
    detail: Optional[str] = None


class RawStore:
    """Content-addressed, append-only store rooted outside the repository.

    `objects` holds the first record seen for each raw_id; `object_for_request` holds the
    current record for each request, so the same bytes under two requests keep separate
    retrieval records."""

    def __init__(self, root: Path, clock=time.time_ns):
        self.root = Path(root)
        self.clock = clock
        (self.root / "objects").mkdir(parents=True, exist_ok=True)
        self._index_path = self.root / "index.jsonl"
        self._journal_path = self.root / "journal.jsonl"
        self.objects: dict[str, RawObject] = {}
        self.latest_by_request: dict[str, str] = {}
        self.object_for_request: dict[str, RawObject] = {}
        if self._index_path.exists():
            for line in self._index_path.read_text().splitlines():
                obj = RawObject(**json.loads(line))
                self.objects.setdefault(obj.raw_id, obj)
                if obj.member_path is None and not obj.quarantined:
                    self.latest_by_request[obj.request] = obj.raw_id
                    self.object_for_request[obj.request] = obj

    def object_path(self, raw_id: str) -> Path:
        return self.root / "objects" / raw_id[:2] / raw_id

    def journal(self, entry: JournalEntry) -> None:
        with open(self._journal_path, "a") as fh:
            fh.write(json.dumps(asdict(entry), sort_keys=True) + "\n")

    def journal_entries(self) -> list:
        if not self._journal_path.exists():
            return []
        return [JournalEntry(**json.loads(x)) for x in self._journal_path.read_text().splitlines()]

    def _index(self, obj: RawObject) -> None:
        with open(self._index_path, "a") as fh:
            fh.write(json.dumps(asdict(obj), sort_keys=True) + "\n")

    def ingest_file(
        self,
        path: Path,
        *,
        source_id: str,
        source_approval_id: str,
        request: str,
        published_checksum: Optional[str] = None,
        server_last_modified: Optional[str] = None,
        retrieved_at_ns: Optional[int] = None,
        http_status: Optional[int] = None,
    ) -> RawObject:
        """Store a held or retrieved file. Identical bytes at the same request are idempotent
        (S-02a); different bytes at the same request are a new version (S-09). A published
        checksum is always verified, including on a repeat (S-01)."""
        now = self.clock()
        raw_id = sha256_file(path)
        size = Path(path).stat().st_size
        prev = self.latest_by_request.get(request)
        checksum_ok = published_checksum is None or published_checksum.lower() == raw_id
        if prev == raw_id and checksum_ok:
            self.journal(JournalEntry(now, request, "duplicate", raw_id, http_status, size))
            return self.object_for_request[request]
        if published_checksum is None:
            status = "none_published"
        else:
            status = "verified" if checksum_ok else "mismatch"
        quarantined = not checksum_ok
        obj = RawObject(
            raw_id=raw_id, source_id=source_id, source_approval_id=source_approval_id, request=request,
            retrieved_at_ns=retrieved_at_ns if retrieved_at_ns is not None else now, byte_length=size,
            http_status=http_status, server_last_modified=server_last_modified,
            published_checksum=published_checksum, checksum_status=status,
            supersedes_raw_id=prev if prev and prev != raw_id and not quarantined else None,
            quarantined=quarantined, reason="checksum_mismatch" if quarantined else None,
        )
        dest = self.object_path(raw_id)
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(".part")
            shutil.copyfile(path, tmp)
            if sha256_file(tmp) != raw_id:
                tmp.unlink()
                self.journal(JournalEntry(now, request, "failed", None, http_status, size, "copy_hash_mismatch"))
                raise IOError("copy hash mismatch")
            tmp.rename(dest)
        self.objects.setdefault(raw_id, obj)
        self._index(obj)
        if not quarantined:
            self.latest_by_request[request] = raw_id
            self.object_for_request[request] = obj
        self.journal(JournalEntry(now, request, "quarantined" if quarantined else "stored", raw_id, http_status, size,
                                  obj.reason))
        return obj

    def _member_obj(self, container: RawObject, name: str, data: bytes) -> RawObject:
        rid = sha256_bytes(data)
        dest = self.object_path(rid)
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            dest.write_bytes(data)
        obj = RawObject(
            raw_id=rid, source_id=container.source_id, source_approval_id=container.source_approval_id,
            request=container.request + "#" + name, retrieved_at_ns=container.retrieved_at_ns, byte_length=len(data),
            server_last_modified=container.server_last_modified, checksum_status=container.checksum_status,
            container_raw_id=container.raw_id, member_path=name, supersedes_raw_id=container.supersedes_raw_id,
        )
        if rid not in self.objects:
            self.objects[rid] = obj
            self._index(obj)
        return obj

    def member(self, container: RawObject, name: str) -> RawObject:
        """Register one ZIP member as its own raw object (§2 rule 4) without extracting the rest.
        The member inherits the container's retrieval record, including any supersession."""
        with zipfile.ZipFile(self.object_path(container.raw_id)) as zf:
            return self._member_obj(container, name, zf.read(name))

    def members(self, container: RawObject) -> list[RawObject]:
        with zipfile.ZipFile(self.object_path(container.raw_id)) as zf:
            return [self._member_obj(container, i.filename, zf.read(i)) for i in zf.infolist()
                    if not i.is_dir() and not i.filename.startswith("__MACOSX/")]

    def read(self, raw_id: str) -> bytes:
        return self.object_path(raw_id).read_bytes()
