"""Append-only raw object store and retrieval journal (event contract §2).

The store copies files that are already held into a content-addressed layout.
It performs no network access (DEC-058).
"""

from __future__ import annotations

import fcntl
import hashlib
import json
import os
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


class CopyHashMismatch(OSError):
    """The stored copy's hash differs from the source's."""


class RawStore:
    """Content-addressed, append-only store rooted outside the repository.

    `objects` holds the first record seen for each raw_id; `object_for_request` holds the
    current record for each request, so the same bytes under two requests keep separate
    retrieval records."""

    def __init__(self, root: Path, clock=time.time_ns, auto_recover: bool = True, read_only: bool = False):
        """A writer (the default) takes an exclusive lock on `.writer.lock` until close(), repairs a
        cut-off final journal or index line, and runs recover() (RC-05). Both are safe because no
        other writer can be mid-ingest.

        `read_only=True` takes no lock and changes nothing. Use it for analysis, including any
        store that a process without the lock may be writing (the 7-day capture, DEC-064)."""
        self.root = Path(root)
        self.clock = clock
        self.read_only = read_only
        self._lock_fd = None
        self._index_path = self.root / "index.jsonl"
        self._journal_path = self.root / "journal.jsonl"
        self.repaired: list = []
        if not read_only:
            (self.root / "objects").mkdir(parents=True, exist_ok=True)
            self._lock_fd = os.open(self.root / ".writer.lock", os.O_RDWR | os.O_CREAT, 0o644)
            try:
                fcntl.flock(self._lock_fd, fcntl.LOCK_EX | fcntl.LOCK_NB)
            except OSError:
                os.close(self._lock_fd)
                self._lock_fd = None
                raise RuntimeError(f"raw store {self.root} is held by another writer")
            for p in (self._journal_path, self._index_path):
                self._repair_tail(p)
        self.objects: dict[str, RawObject] = {}
        self.latest_by_request: dict[str, str] = {}
        self.object_for_request: dict[str, RawObject] = {}
        self.indexed: set = set()
        self.truncated_lines: list = []  # set only for read-only opens; writers repair the tail
        for d in self._read_lines(self._index_path):
            obj = RawObject(**d)
            self.objects.setdefault(obj.raw_id, obj)
            self.indexed.add((obj.request, obj.raw_id))
            if obj.member_path is None and not obj.quarantined:
                self.latest_by_request[obj.request] = obj.raw_id
                self.object_for_request[obj.request] = obj
        self.last_recovery = self.recover() if auto_recover and not read_only else None

    def _repair_tail(self, path: Path) -> None:
        """Cut a file back to its last newline, so that a fragment left by a failed write cannot
        merge with the next line (RC-06). The cut bytes are kept beside the file."""
        if not path.exists():
            return
        data = path.read_bytes()
        if not data or data.endswith(b"\n"):
            return
        keep = data.rfind(b"\n") + 1
        frag = path.with_name(path.name + f".cut-{self.clock()}")
        frag.write_bytes(data[keep:])
        with open(path, "r+b") as fh:
            fh.truncate(keep)
        self.repaired.append({"file": path.name, "bytes_cut": len(data) - keep, "kept_as": frag.name})

    def close(self) -> None:
        if getattr(self, "_lock_fd", None) is not None:
            fcntl.flock(self._lock_fd, fcntl.LOCK_UN)
            os.close(self._lock_fd)
            self._lock_fd = None

    def __del__(self):
        try:
            self.close()
        except Exception:
            pass

    def _read_lines(self, path: Path) -> list:
        """Parsed JSON lines. A truncated final line (a write cut off by a full disk) is skipped
        and recorded rather than failing the store."""
        if not path.exists():
            return []
        lines = path.read_bytes().split(b"\n")
        out = []
        for i, line in enumerate(lines):
            if not line.strip():
                continue
            try:
                out.append(json.loads(line))
            except ValueError:
                if i >= len(lines) - 2:
                    self.truncated_lines.append(path.name)
                    continue
                raise
        return out

    @staticmethod
    def _append(path: Path, record: dict) -> None:
        """One complete line per write; a short write is an error (RC-06)."""
        data = (json.dumps(record, sort_keys=True) + "\n").encode()
        fd = os.open(path, os.O_WRONLY | os.O_APPEND | os.O_CREAT, 0o644)
        try:
            if os.write(fd, data) != len(data):
                raise OSError("short write")
        finally:
            os.close(fd)

    def object_path(self, raw_id: str) -> Path:
        return self.root / "objects" / raw_id[:2] / raw_id

    def _writable(self) -> None:
        if self.read_only:
            raise PermissionError("raw store opened read-only")

    def journal(self, entry: JournalEntry) -> None:
        self._writable()
        self._append(self._journal_path, asdict(entry))

    def journal_entries(self) -> list:
        return [JournalEntry(**d) for d in self._read_lines(self._journal_path)]

    def _index(self, obj: RawObject) -> None:
        self._writable()
        self._append(self._index_path, asdict(obj))
        self.indexed.add((obj.request, obj.raw_id))

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
        self._writable()
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
        self.journal(JournalEntry(now, request, "started", raw_id, http_status, size))  # RC-05 marker
        if not dest.exists():
            dest.parent.mkdir(parents=True, exist_ok=True)
            tmp = dest.with_suffix(".part")
            try:
                self._copy(path, tmp)
                if sha256_file(tmp) != raw_id:
                    raise CopyHashMismatch(raw_id)
                tmp.rename(dest)
            except OSError as exc:  # RC-06: write failure or bad copy; nothing partial is kept
                tmp.unlink(missing_ok=True)
                reason = "copy_hash_mismatch" if isinstance(exc, CopyHashMismatch) else f"write_failed:{type(exc).__name__}"
                self.journal(JournalEntry(self.clock(), request, "failed", raw_id, http_status, size, reason))
                raise
        self.objects.setdefault(raw_id, obj)
        self._index(obj)
        if not quarantined:
            self.latest_by_request[request] = raw_id
            self.object_for_request[request] = obj
        self.journal(JournalEntry(now, request, "quarantined" if quarantined else "stored", raw_id, http_status, size,
                                  obj.reason))
        return obj

    _copy = staticmethod(shutil.copyfile)  # replaceable in fault-injection tests (RC-06)

    def recover(self) -> dict:
        """RC-05: after a crash, find ingests journalled as `started` with no completion entry,
        remove their partial files, and journal each as `recovered_incomplete`. Completed objects
        are untouched; re-running the same ingest is idempotent (S-02a)."""
        done_outcomes = {"stored", "quarantined", "duplicate", "failed", "recovered_incomplete", "recovered_complete"}
        open_: dict = {}
        for e in self.journal_entries():
            key = (e.request, e.raw_id)
            if e.outcome == "started":
                open_[key] = e
            elif e.outcome in done_outcomes:
                open_.pop(key, None)
        removed = []
        for p in self.root.glob("objects/*/*.part"):
            p.unlink()
            removed.append(p.name)
        incomplete, complete = [], []
        for (request, raw_id), e in open_.items():
            if (request, raw_id) in self.indexed and self.object_path(raw_id).exists():
                complete.append({"request": request, "raw_id": raw_id})  # crashed after indexing
                outcome, detail = "recovered_complete", "indexed before the crash"
            else:
                incomplete.append({"request": request, "raw_id": raw_id})
                outcome, detail = "recovered_incomplete", "no completion marker"
            self.journal(JournalEntry(self.clock(), request, outcome, raw_id, e.http_status, e.byte_length, detail))
        return {"incomplete": incomplete, "completed_before_crash": complete, "partials_removed": removed,
                "tail_repairs": list(self.repaired)}

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
