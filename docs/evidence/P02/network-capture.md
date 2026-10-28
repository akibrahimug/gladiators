# P02 network capture: transport and live capture

[Task](../../tasks/TASK-P02-005.md) · [Capture and recovery](capture-and-recovery.md) · [Validation plan](capture-validation-plan.md) · [Results on held files](capture-validation-results.md)

**Status: results, 2026-10-28.** Not a G02 decision. The authorised calls below were made under DEC-044, DEC-057, DEC-062 and DEC-063. Captured data is kept outside the repository (DEC-030) and identified by SHA-256.

## 1. What was built

All of it uses the standard library only.

| Module | Role |
| --- | --- |
| `transport.py` | HTTPS GET/HEAD with TLS verification. Redirects are never followed, so a 3xx comes back as a response. Truncated reads become `ConnectionError`. Also a robots check per host (404 means no exclusion; an unreachable robots file means no pull) and HEAD capture stored as a raw object |
| `ws.py` | RFC 6455 client. Checks the accept key and the Upgrade header; masks client frames; rejects masked server frames and set reserved bits; caps frame and handshake size; reassembles fragments; answers ping and close |
| `live.py` | Kraken v2 `book` (depth 10) and `trade`:<br>- every frame is journalled before parsing, into hourly segments that are ingested as raw objects (SR-02, SA-03);<br>- the CRC32 book checksum is checked, with resync capped at 6 per minute per pair;<br>- reconnect uses jittered backoff, reset only after a valid book;<br>- a parse error is recorded and the capture continues;<br>- maintenance is excluded from R-4;<br>- T-3 latency is reported per pair and channel, raw and offset-corrected; T-5 uses SNTP |
| `cli.py`, `capture.py` | The `head`, `live` and `daily` commands. `daily` stops itself after 30 days |
| `ops/launchd/` | The job template and [install steps](../../../ops/launchd/README.md) (DEC-061). The code runs from a copy outside `~/Documents` |

**Tests:** `/usr/bin/python3 -I -B -m unittest discover -s tests` passes all 55 tests on Python 3.9 and 3.12.

**TLS.** The python.org Python on this Mac has no CA certificates, so its verification fails. Verification is never disabled. All network runs use Apple's `/usr/bin/python3`, which verifies against the system certificates.

## 2. Authorised calls made

| Run | Code revision | Result | Evidence (SHA-256, outside the repository) |
| --- | --- | --- | --- |
| 18 Binance HEAD requests (W-A) | `2d1fbdd` | Robots: 404, no exclusion. All 18 returned 200 with `Last-Modified`. Monthly lags: 2024-12 files Jan 7–8 2025; 2025-01 files Feb 8 2025 | `head-summary.jsonl` `c3b8c8d4…` |
| Daily REST test (once) | `2d1fbdd` | Robots: 404. `OHLC` XBTUSD and ETHUSD and `AssetPairs` each stored on the first attempt, with no API error | `daily-summary.jsonl` `b515e70d…` |
| Live smoke, 60 s | pre-commit | 3,925 checksums OK, 0 failed. Superseded by the next two runs | — |
| **Live, 1 hour (W-J step 2)** | `2d1fbdd` | §3 | `frames.jsonl` `99f1c638…85b7` |
| Live smoke, 120 s | `8f02b24` (after the review fixes) | 7,202 checksums OK, 0 failed; 0 disconnects, 0 parse errors; initial sync 1.56 s; one segment ingested | segment `da4c5857…` |

## 3. One-hour live capture (CV-12)

2026-10-28, 09:17–10:17 UTC, BTC/USD and ETH/USD.

| Criterion | Approved value | Observed | Result |
| --- | --- | --- | --- |
| Volume | — | 298,915 frames; 292,861 book updates; 4,585 trades | — |
| **Q-5** book integrity | Zero books accepted after an unresolved mismatch | 292,865 checksums OK, **0 failed**, 0 resyncs | **Pass** |
| **R-1/R-2** outage handling | Outage recorded; reconnect, resubscribe, resume only on a valid book | 1 disconnect (server closed the socket at 09:55:51). Reconnected 2.18 s later; both books valid at 2.55 s | **Pass** |
| **R-3** recovery time | p95 ≤ 60 s | 1 recovery: 2.55 s | **Pass** (n = 1) |
| **R-4** valid-book time | ≥ 99 %, excluding maintenance | BTC/USD 99.89 %, ETH/USD 99.89 %; 99.93 % excluding the 1.39 s initial sync. No maintenance in the window | **Pass** |
| **R-5** storage | ≤ 2 GB compressed per pair per day | 79.9 MB uncompressed and 7.35 MB gzip per hour, for 2 pairs: about **88 MB compressed per pair per day** | **Pass** |
| **T-3** latency | Reported, not required | Offset-corrected p50 / p95 / p99: book BTC 32 / 126 / 184 ms; book ETH 32 / 125 / 196 ms; trade BTC 36 / 128 / 180 ms; trade ETH 38 / 129 / 184 ms. Maxima of 4–5 s. The correction uses the mean offset (141 ms), so the figures carry the offset's spread | Reported |
| **T-5** clock offset | Flag while above 100 ms | 55 of 60 SNTP samples succeeded: offset 34–258 ms, mean 141 ms. **Above 100 ms for most of the hour**, so `timestamp_uncertainty_ms` applies | **Flag raised** |
| **T-6** abstention | Abstain above 1 s (intraday) or 60 s (daily) | Maximum 258 ms | No abstention |

## 4. Findings for the user

1. **This Mac's clock is 34–258 ms off and drifting** (T-5). Live timestamps carry that uncertainty. It doesn't affect daily decisions (T-6 at 60 s), but intraday work would need better clock sync, for example re-enabling *Set time automatically* in System Settings.
2. **Kraken maintenance was announced for 2026-10-29, 08:01–08:16 UTC.** It falls inside a 7-day capture window. The capture now tracks it and excludes it from R-4.
3. **The 7-day run (the second part of W-J) has not started.** Each pair produces about 2 GB uncompressed per day, so 7 days is about 13 GB uncompressed for two pairs. It runs on request.

## 5. Remaining for G02

- The 7-day live window (W-J).
- The 30-day REST pull, once the user installs the job (DEC-061).
- The 2026Q4 archive, when it is published.
- RC-05 to RC-08 injection.
- The user's review and a dated G02 approval.


## Decisions asked, 2026-10-28

The user's answers. Each question and the chosen option are quoted verbatim.

| Decision | Question (verbatim) | Chosen option: label — description (verbatim) |
| --- | --- | --- |
| DEC-059 | "Kraken archive vs REST: the contract's current rule (round archive volume to 8 decimals, then require equality) gives 4 mismatches, 3 of which are float rounding on ETHUSD. Which comparison rule should the event contract use?" | "Relative 1e-9 tolerance (Recommended)" — "Prices and trade counts must match exactly; volumes may differ by at most 1e-9 relative. This leaves only the real XBTUSD 2026-09-10 difference, and matches the P01 sample." |
| DEC-060 | "Bar identity: key bars on their start time instead of their row position in the file? Row positions shift when a file gains a row, or when the REST window slides each day." | "Key on bar start (Recommended)" — "A bar keeps its identity across revisions and repeated REST pulls; the row number stays in raw_locator for tracing." |
| DEC-061 | "The 30-day Kraken REST pull (DEC-057) needs something to run it once a day. How should it run?" | "Local cron/launchd job (Recommended)" — "I add a small script and you install one launchd job on this Mac; it runs at 00:15 UTC daily, keyless, writing outside the repo. You can remove it any time." |
| DEC-062 | "Next step: build the network side, i.e. a real HTTPS transport for fetch() (for the REST pull, HEAD requests and Q4 archive) and the Kraken WebSocket live capture (W-J), as TASK-P02-005?" | "Yes, build and test it (Recommended)" — "Standard library only (urllib for HTTPS; a minimal WebSocket client). It is tested offline first; the first real calls are the 18 HEAD requests, then a 1-hour live capture, all under DEC-044/057." |

| DEC-063 | "To check the clock during live capture (T-5), the capture code sends one time query per minute (SNTP, UDP port 123) to time.apple.com. That's the server macOS already syncs with, but it isn't on the DEC-057 list. Allow it?" | "Allow it (Recommended)" — "The only way to measure T-5 during capture. It has already shown your clock is 140–200 ms off, which flags every live record under T-5." |

Unchosen options: "Keep the 8-decimal rule"; "Keep row index"; "Claude scheduled routine"; "I run it manually"; "Build it, but no real calls yet"; "Pause P02 here"; "Use the OS clock status only"; "Drop the clock check".
