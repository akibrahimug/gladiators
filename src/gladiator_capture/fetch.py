"""Retrieval with the recovery rules RC-01 to RC-03 (capture-and-recovery §3).

The transport is injected. This module ships **no network transport** (DEC-058): tests and
the validation runner pass a fake one. A later, authorised task supplies a real transport.
"""

from __future__ import annotations

import tempfile
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Optional, Protocol

from .analysis import GapInterval
from .rawstore import JournalEntry, RawStore

RETRY_DELAYS_S = (30, 120, 600)  # TH-3 (DEC-056)
RETRY_AFTER_MAX_S = 600  # TH-3b (DEC-056)


@dataclass
class Response:
    status: int
    body: bytes = b""
    headers: dict = field(default_factory=dict)


class Transport(Protocol):
    def get(self, request: str) -> Response: ...


@dataclass
class FetchResult:
    raw: Optional[object]
    gap: Optional[GapInterval]
    attempts: int


def fetch(request: str, transport: Transport, store: RawStore, *, source_id: str, source_approval_id: str,
          published_checksum: Optional[str] = None, sleep: Callable[[float], None] = time.sleep,
          interval_ns: tuple = (0, 0)) -> FetchResult:
    """One retrieval, with:
    - RC-01: up to len(RETRY_DELAYS_S) retries on 5xx, timeouts or resets;
    - RC-02: 401 or 403 stop at once, with no retry by any route (DEC-050, DEC-051); 429 waits for
      Retry-After if it is <= TH-3b, then retries once, else stops;
    - RC-03: a body shorter than Content-Length is discarded and retried;
    - RC-04: a checksum mismatch is retried, and after the retries the source is unavailable."""
    attempts = 0
    retried_429 = False
    reason = None
    while True:
        attempts += 1
        now = store.clock()
        try:
            resp = transport.get(request)
        except (TimeoutError, ConnectionError) as exc:
            resp, reason = None, type(exc).__name__
        if resp is not None:
            store.journal(JournalEntry(now, request, "attempt", None, resp.status, len(resp.body)))
            if resp.status in (401, 403) or 300 <= resp.status < 400:  # refusals and unfollowed redirects are terminal
                reason = f"http_{resp.status}"
                break
            if resp.status == 429:
                ra = resp.headers.get("Retry-After")
                if not retried_429 and ra is not None and ra.isdigit() and int(ra) <= RETRY_AFTER_MAX_S:
                    retried_429 = True
                    attempts -= 1  # the single 429 retry does not use up a TH-3 retry
                    sleep(int(ra))
                    continue
                reason = "http_429"
                break
            if 200 <= resp.status < 300:
                cl = resp.headers.get("Content-Length")
                if cl is not None and int(cl) != len(resp.body):
                    reason = "truncated"
                else:
                    with tempfile.NamedTemporaryFile(delete=False) as tmp:
                        tmp.write(resp.body)
                    obj = None
                    try:
                        obj = store.ingest_file(Path(tmp.name), source_id=source_id,
                                                source_approval_id=source_approval_id, request=request,
                                                published_checksum=published_checksum,
                                                server_last_modified=resp.headers.get("Last-Modified"),
                                                http_status=resp.status)
                    except OSError as exc:  # RC-06: write failure; stop, do not retry into a full disk
                        for part in store.root.glob("objects/*/*.part"):
                            part.unlink()
                        reason = f"write_failed:{type(exc).__name__}"
                        break
                    finally:
                        Path(tmp.name).unlink(missing_ok=True)
                    if not obj.quarantined:
                        return FetchResult(obj, None, attempts)
                    reason = "checksum_mismatch"
            else:
                reason = f"http_{resp.status}"
        if attempts > len(RETRY_DELAYS_S):
            break
        sleep(RETRY_DELAYS_S[attempts - 1])
    store.journal(JournalEntry(store.clock(), request, "failed", None, None, None, reason))
    gap = GapInterval(source_id, request, "n/a", interval_ns[0], interval_ns[1], "data_gap", reason, store.clock())
    return FetchResult(None, gap, attempts)
