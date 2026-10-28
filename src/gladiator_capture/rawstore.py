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
from dataclasses import asdict, dataclass, field
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
    outcome: str  # stored | duplicate | quarantined | failed
    raw_id: Optional[str] = None
    http_status: Optional[int] = None
    byte_length: Optional[int] = None
    detail: Optional[str] = None


class RawStore:
    """Content-addressed, append-only store rooted outside the repository."""

    def __init__(self, root: Path, clock=time.time_ns):
        self.root = Path(root)
        self.clock = clock
        (self.root / "objects").mkdir(parents=True, exist_ok=True)
        self._index_path = self.root / "index.jsonl"
        self._journal_path = self.root / "journal.jsonl"
        self.objects: dict[str, RawObject] = {}  # first-seen object per raw_id
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
    ) -> RawObject:
        """Store a held file. Idempotent for identical bytes (S-02a); a
        different hash at the same request is a new version (S-09)."""
        now = self.clock()
        raw_id = sha256_file(path)
        size = Path(path).stat().st_size
        prev = self.latest_by_request.get(request)
        if prev == raw_id:
            self.journal(JournalEntry(now, request, "duplicate", raw_id, None, size))
            return self.object_for_request[request]
        status = "none_published"
        quarantined = False
        reason = None
        if published_checksum is not None:
            if published_checksum.lower() == raw_id:
                status = "verified"
            else:
                status = "mismatch"
                quarantined = True
                reason = "checksum_mismatch"
        obj = RawObject(
            raw_id=raw_id,
            source_id=source_id,
            source_approval_id=source_approval_id,
            request=request,
            retrieved_at_ns=retrieved_at_ns if retrieved_at_ns is not None else now,
            byte_length=size,
            server_last_modified=server_last_modified,
            published_checksum=published_checksum,
            checksum_status=status,
            supersedes_raw_id=prev if prev and prev != raw_id else None,
            quarantined=quarantined,
            reason=reason,
        )
        dest = self.object_path(raw_id)
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(".part")
            shutil.copyfile(path, tmp)
            if sha256_file(tmp) != raw_id:
                tmp.unlink()
                self.journal(JournalEntry(now, request, "failed", None, None, size, "copy_hash_mismatch"))
                raise IOError("copy hash mismatch")
            tmp.rename(dest)
        self.objects.setdefault(raw_id, obj)
        self._index(obj)
        if not quarantined:
            self.latest_by_request[request] = raw_id
            self.object_for_request[request] = obj
        self.journal(JournalEntry(now, request, "quarantined" if quarantined else "stored", raw_id, None, size, reason))
        return obj

    def members(self, container: RawObject) -> list[RawObject]:
        """Register each ZIP member as its own raw object (§2 rule 4)."""
        out = []
        with zipfile.ZipFile(self.object_path(container.raw_id)) as zf:
            for info in zf.infolist():
                if info.is_dir() or info.filename.startswith("__MACOSX/"):
                    continue
                data = zf.read(info)
                rid = sha256_bytes(data)
                dest = self.object_path(rid)
                if not dest.exists():
                    dest.parent.mkdir(parents=True, exist_ok=True)
                    dest.write_bytes(data)
                obj = RawObject(
                    raw_id=rid,
                    source_id=container.source_id,
                    source_approval_id=container.source_approval_id,
                    request=container.request + "#" + info.filename,
                    retrieved_at_ns=container.retrieved_at_ns,
                    byte_length=len(data),
                    server_last_modified=container.server_last_modified,
                    container_raw_id=container.raw_id,
                    member_path=info.filename,
                )
                if rid not in self.objects:
                    self.objects[rid] = obj
                    self._index(obj)
                out.append(obj)
        return out

    def read(self, raw_id: str) -> bytes:
        return self.object_path(raw_id).read_bytes()
