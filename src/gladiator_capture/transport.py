"""HTTPS transport for fetch(), plus robots.txt checks and HEAD captures (DEC-044, DEC-057, DEC-062).

Standard library only. Only keyless public endpoints named in DEC-057 are called.
"""

from __future__ import annotations

import http.client
import socket
import time
import urllib.error
import urllib.parse
import urllib.request
import urllib.robotparser
from typing import Optional

from .fetch import Response
from .rawstore import JournalEntry, RawStore, sha256_bytes

USER_AGENT = "gladiator-capture/p02 (personal non-commercial research)"
TIMEOUT_S = 60


class _NoRedirect(urllib.request.HTTPRedirectHandler):
    """Redirects are not followed: a 3xx comes back as a Response, so a redirect can never leave
    HTTPS, leave the robots-checked host, or turn a HEAD into a GET."""

    def redirect_request(self, req, fp, code, msg, headers, newurl):
        return None


_OPENER = urllib.request.build_opener(_NoRedirect)


class HttpsTransport:
    """GET or HEAD over HTTPS with TLS verification (the default context). HTTP errors and
    redirects become Responses, so fetch() applies the RC rules; timeouts, resets and truncated
    reads raise TimeoutError or ConnectionError."""

    def __init__(self, method: str = "GET", timeout: float = TIMEOUT_S):
        self.method = method
        self.timeout = timeout

    def get(self, request: str) -> Response:
        if not request.startswith("https://"):
            raise ValueError("HTTPS only")
        req = urllib.request.Request(request, method=self.method, headers={"User-Agent": USER_AGENT})
        try:
            with _OPENER.open(req, timeout=self.timeout) as r:
                body = b"" if self.method == "HEAD" else r.read()
                return Response(r.status, body, dict(r.headers.items()))
        except urllib.error.HTTPError as e:  # includes the unfollowed 3xx
            return Response(e.code, b"", dict(e.headers.items()) if e.headers else {})
        except (urllib.error.URLError, OSError, http.client.HTTPException) as e:
            reason = getattr(e, "reason", None)
            if isinstance(e, (TimeoutError, socket.timeout)) or isinstance(reason, (TimeoutError, socket.timeout)):
                raise TimeoutError(str(e))
            raise ConnectionError(f"{type(e).__name__}: {e}")


class Robots:
    """Checks robots.txt once per host before the first pull (DEC-044). A 404 or 410 means no
    exclusion is published; any other failure means the host is not pulled."""

    def __init__(self, store: RawStore, transport_factory=HttpsTransport):
        self.store = store
        self.transport_factory = transport_factory
        self.cache: dict = {}

    def allowed(self, url: str) -> tuple:
        parts = urllib.parse.urlsplit(url)
        host = f"{parts.scheme}://{parts.netloc}"
        if host not in self.cache:
            try:
                resp = self.transport_factory("GET").get(host + "/robots.txt")
            except (TimeoutError, ConnectionError) as e:
                self.store.journal(JournalEntry(self.store.clock(), host + "/robots.txt", "robots", None, None, None,
                                                f"robots_unreachable:{e}"[:200]))
                self.cache[host] = (False, "robots_unreachable")
                return False, "robots_unreachable"
            if resp.status in (404, 410):
                parser, note = None, f"robots_{resp.status}_no_exclusion"
            elif 200 <= resp.status < 300 and b"<html" not in resp.body[:200].lower():
                parser = urllib.robotparser.RobotFileParser()
                parser.parse(resp.body.decode(errors="replace").splitlines())
                note = "robots_parsed"
            elif 200 <= resp.status < 300:
                parser, note = None, "robots_html_not_robots_file"
            else:
                parser, note = False, f"robots_http_{resp.status}"
            self.store.journal(JournalEntry(self.store.clock(), host + "/robots.txt", "robots", sha256_bytes(resp.body),
                                            resp.status, len(resp.body), note))
            self.cache[host] = (parser, note)
        parser, note = self.cache[host]
        if parser is False:
            return False, note
        if parser is None:
            return True, note
        return parser.can_fetch(USER_AGENT, url), note


def head_capture(url: str, store: RawStore, *, source_id: str, source_approval_id: str,
                 transport: Optional[HttpsTransport] = None) -> dict:
    """One HEAD request; the header block is stored as its own raw object (DEC-057)."""
    t = transport or HttpsTransport("HEAD")
    resp = t.get(url)
    block = "\n".join([f"HTTP {resp.status}"] + [f"{k}: {v}" for k, v in sorted(resp.headers.items())]).encode()
    import tempfile
    from pathlib import Path
    with tempfile.NamedTemporaryFile(delete=False) as tmp:
        tmp.write(block)
    try:
        obj = store.ingest_file(Path(tmp.name), source_id=source_id, source_approval_id=source_approval_id,
                                request="HEAD " + url, http_status=resp.status)
    finally:
        Path(tmp.name).unlink(missing_ok=True)
    return {"url": url, "status": resp.status, "last_modified": resp.headers.get("Last-Modified"),
            "etag": resp.headers.get("ETag"), "content_length": resp.headers.get("Content-Length"), "raw_id": obj.raw_id}


def polite_pause(seconds: float = 0.5) -> None:
    """Reasonable load between successive requests to one host (DEC-044)."""
    time.sleep(seconds)
