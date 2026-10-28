"""Minimal RFC 6455 WebSocket client over TLS (standard library only). Text frames only."""

from __future__ import annotations

import base64
import hashlib
import os
import socket
import ssl
import struct
import urllib.parse

GUID = "258EAFA5-E914-47DA-95CA-C5AB0DC85B11"
MAX_FRAME = 16 * 1024 * 1024
MAX_HANDSHAKE = 64 * 1024


class WebSocketClosed(ConnectionError):
    pass


def encode_frame(payload: bytes, opcode: int = 0x1, mask: bool = True) -> bytes:
    head = bytes([0x80 | opcode])
    n = len(payload)
    mbit = 0x80 if mask else 0
    if n < 126:
        head += bytes([mbit | n])
    elif n < 1 << 16:
        head += bytes([mbit | 126]) + struct.pack("!H", n)
    else:
        head += bytes([mbit | 127]) + struct.pack("!Q", n)
    if not mask:
        return head + payload
    key = os.urandom(4)
    return head + key + bytes(b ^ key[i % 4] for i, b in enumerate(payload))


class FrameReader:
    """Parses frames from a byte stream; handles fragmentation, ping and close."""

    def __init__(self, recv, allow_masked: bool = False):
        self.recv = recv
        self.buf = b""
        self.allow_masked = allow_masked

    def _need(self, n: int) -> bytes:
        while len(self.buf) < n:
            chunk = self.recv(65536)
            if not chunk:
                raise WebSocketClosed("socket closed")
            self.buf += chunk
        out, self.buf = self.buf[:n], self.buf[n:]
        return out

    def frame(self) -> tuple:
        b1, b2 = self._need(2)
        fin, opcode = b1 & 0x80, b1 & 0x0F
        if b1 & 0x70:
            raise WebSocketClosed("reserved bits set")
        if b2 & 0x80 and not self.allow_masked:
            raise WebSocketClosed("masked frame from server")
        n = b2 & 0x7F
        if n == 126:
            n = struct.unpack("!H", self._need(2))[0]
        elif n == 127:
            n = struct.unpack("!Q", self._need(8))[0]
        if n > MAX_FRAME:
            raise WebSocketClosed("frame too large")
        key = self._need(4) if b2 & 0x80 else None
        data = self._need(n)
        if key:
            data = bytes(b ^ key[i % 4] for i, b in enumerate(data))
        return bool(fin), opcode, data


class WebSocket:
    def __init__(self, url: str, timeout: float = 30.0):
        u = urllib.parse.urlsplit(url)
        if u.scheme != "wss":
            raise ValueError("wss only")
        self.host, self.path = u.hostname, (u.path or "/") + (("?" + u.query) if u.query else "")
        raw = socket.create_connection((self.host, u.port or 443), timeout=timeout)
        self.sock = ssl.create_default_context().wrap_socket(raw, server_hostname=self.host)
        key = base64.b64encode(os.urandom(16)).decode()
        req = (f"GET {self.path} HTTP/1.1\r\nHost: {self.host}\r\nUpgrade: websocket\r\nConnection: Upgrade\r\n"
               f"Sec-WebSocket-Key: {key}\r\nSec-WebSocket-Version: 13\r\n"
               "User-Agent: gladiator-capture/p02 (personal non-commercial research)\r\n\r\n")
        self.sock.sendall(req.encode())
        resp = b""
        while b"\r\n\r\n" not in resp:
            chunk = self.sock.recv(4096)
            if not chunk:
                raise WebSocketClosed("handshake closed")
            resp += chunk
            if len(resp) > MAX_HANDSHAKE:
                raise ConnectionError("handshake too large")
        head, rest = resp.split(b"\r\n\r\n", 1)
        lines = head.decode(errors="replace").split("\r\n")
        if " 101 " not in lines[0] + " ":
            raise ConnectionError("handshake failed: " + lines[0])
        accept = base64.b64encode(hashlib.sha1((key + GUID).encode()).digest()).decode()
        headers = {k.lower(): v.strip() for k, _, v in (l.partition(":") for l in lines[1:])}
        if headers.get("sec-websocket-accept") != accept:
            raise ConnectionError("bad Sec-WebSocket-Accept")
        if headers.get("upgrade", "").lower() != "websocket" or "upgrade" not in headers.get("connection", "").lower():
            raise ConnectionError("missing Upgrade/Connection headers")
        self.reader = FrameReader(self.sock.recv)
        self.reader.buf = rest

    def send_text(self, text: str) -> None:
        self.sock.sendall(encode_frame(text.encode()))

    def recv_text(self) -> str:
        parts = []
        while True:
            fin, opcode, data = self.reader.frame()
            if opcode == 0x9:  # ping
                self.sock.sendall(encode_frame(data, 0xA))
                continue
            if opcode == 0xA:  # pong
                continue
            if opcode == 0x8:
                try:
                    self.sock.sendall(encode_frame(data[:2], 0x8))
                except OSError:
                    pass
                raise WebSocketClosed("close frame")
            parts.append(data)
            if fin:
                return b"".join(parts).decode("utf-8", errors="replace")

    def settimeout(self, t: float) -> None:
        self.sock.settimeout(t)

    def close(self) -> None:
        try:
            self.sock.sendall(encode_frame(b"", 0x8))
        except OSError:
            pass
        self.sock.close()
