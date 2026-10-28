# P02 capture validation results: held files (TASK-P02-002)

[Task](../../tasks/TASK-P02-002.md) · [Validation plan](capture-validation-plan.md) · [Event contract](event-contract.md) · [Capture and recovery](capture-and-recovery.md)

**Status: results, 2026-10-28.**
- **Revision and scope:** run at code revision `0811834` under DEC-058, on held files only, against the thresholds approved in DEC-056. There was no network access and no live capture.
- **Not a G02 decision:** G02 still needs the items in §3 and the user's dated approval.
- **Inputs:** the P01 sample files, identified in the scratchpad manifest (SHA-256 `2492dc56…261aa9`).

**How it was run:**
- **Unit tests:** `python3 -I -B -m unittest discover -s tests`, 31 tests, OK. They use synthetic data only.
- **Validation:** `python3 -I -B run_validation.py --sample-root <scratchpad> --out <scratchpad>/p202-run2`, from `/`. The launcher inserts `src`, so `-I` isolation holds, and the held files are only read.
- **Report:** `report.json`, SHA-256 `c920d603d77a126356f0733b06b49029e8d478f9cbf21cfef463c0e89a4f316f`, kept outside the repository. A second, separate-process run (`p202-run3`) gave a **byte-identical** report.

**Clocks:**
- Held files have no retrieval journal from P01, so each file's modification time stands in for `retrieved_at`. If those files are copied or touched, the S-12 drops, the TH-6 flags and the report hash will change.
- `ingested_at` is our real clock at parse time. It is excluded from the content hash (`output_hash`), because event contract §6 determinism concerns the normalized content.

## 1. Criteria

| ID | Result | Evidence |
| --- | --- | --- |
| CV-01 | **Pass, measured.** 0 of 2,703,561 records are untraceable. Each record's `raw_id` is a registered raw object, either the file itself or its ZIP member (§2 rule 4), with the container linked. Each record also carries `rights_id` | report `criteria` |
| CV-02 | **Pass, all records.** 0 of 2,703,561 are missing a time, the basis or a valid unit | report `criteria` |
| CV-03 | **19 of 19 runnable fixtures pass** (F-01 to F-18, with F-06b). F-15 needs live capture and was not run. F-14 runs through `fetch()` with a scripted transport. F-17 runs `is_stale()` on the COT header time | report `fixtures` |
| CV-04 | **Pass.** F-02b, F-03, F-06 and F-06b give the expected reasons. W-A: 620 rows, 0 quarantined. W-D: 2,689,488 trades, 0 quarantined | report |
| CV-05 | **Pass.** W-E: XBTUSD 12 and ETHUSD 6 missing intervals, all `status_unknown`. W-A: 0 | report W-E, F-04 |
| CV-06 | **Pass.** The reports give raw rows / accepted / quarantined / duplicates / missing: W-A 620 / 620 / 0 / 0 / 0; XBTUSD 4,731 / 4,731 / 0 / 0 / 12; ETHUSD 4,067 / 4,067 / 0 / 0 / 6. Fail-closed is implemented as `entry_blocked()`: below Q-4, or `status_unknown` on the decision day. It is tested on synthetic data. Neither W-E pair is blocked at 2026-09-30 | report; tests |
| CV-07 | **Pass.** F-18: 346/365 disqualifies, 347/365 qualifies. The minimum over **every** 365-day look-back, at a daily step, from 2016 to 2025-10: XBTUSD 1.0000, ETHUSD 0.9973. The listing-partway and minimum-length clauses are implemented in `qualifies()` and unit-tested. Delisting ends a series by construction | report W-E; tests |
| CV-08 | **Pass, all records.** 0 records lack `venue`, `source_id` or `feed_id` | report `criteria` |
| CV-09 | **Pass.** Two separate processes gave byte-identical reports. The W-A content hash is `d29b8f86…8599` | report hashes |
| CV-10 | **Pass.** F-16: 0 records visible on 2025-01-07, 31 from `Last-Modified`. F-09, where both versions carry the same `Last-Modified`: version 2 takes basis `retrieved` and `available_at` = its retrieval time, so it is invisible before then (DEC-053) | report |
| CV-11 | **Partial.** Exercised through `fetch()` with a scripted transport:<br>- RC-01: 5xx then success; all four attempts failing;<br>- RC-02: 403 with no retry; 429 with `Retry-After`; 429 without it;<br>- RC-03: truncation;<br>- RC-04: repeated checksum mismatch, giving `SOURCE_UNAVAILABLE`;<br>- RC-12, through F-09.<br>RC-05 is shown only as idempotent re-ingest (F-02a); a crash marker is not implemented. **Not exercised:** RC-05's crash marker, RC-06 (disk full), RC-07 and RC-08 (clock offset) | report `recovery` |
| CV-12 | **Not run.** Live capture (W-J) needs a capture implementation. It is authorised by DEC-057 | — |

## 2. Window results

| Window | Result |
| --- | --- |
| W-A | 20 of 20 checksums verified. `Last-Modified` is held for 2 files (62 records, `archive_published`); the other 18 fall back to `retrieved` (558 records). 0 late flags, since monthly files are exempt |
| W-B | The daily file's record carries `last_modified_after_period` (it is in the changelog). The monthly file's 31 records do not, and its 2022-03-08 row equals the revised daily file. That is the documented TH-4 trade-off |
| W-C | 1 proposed epoch break on 2022-05-31 (a 17-day gap, factor ×20,000, `proposed`). LUNCUSDT starts 2022-09-09 (22 records) |
| W-D | 2,689,488 trades in `us`; 0 data gaps, 0 quarantined, 0 late (basis `archive_published`) |
| W-E | XBTUSD runs 2013-10-06 to 2026-09-30 and ETHUSD 2015-08-07 to 2026-09-30; both have `available_at` 2026-10-01, read from the MANIFEST. The manifest mismatch is logged: 1,760 pairs and 12,350 files declared, 1,759 and 12,349 present. **TH-1/TH-2 re-derived on the full archive:** 1,758 daily files scanned, 427 gaps over 7 days, 14 proposed epoch breaks. This matches the figures in the validation plan; all 14 are held for review |
| W-F | All 4 pairs are absent from the held `AssetPairs` snapshot. Their last bars (quarter-ends) are recorded as upper bounds on the delisting dates |
| W-G | 1,436 pairs and 10,052 CSVs, matching its MANIFEST; `none_published` |
| W-H | 57 completed bars per pair; the incomplete 2026-10-27 bar was dropped. 55 of 57 are flagged late, as expected. Archive comparison: see §4 |
| W-I | The FOMC statement states "2:00 p.m. EDT" (`stated_release`). The minutes state "2:00 p.m." (`first_published`). COT has no stated time (`first_published`) |

## 3. What G02 still needs

1. **CV-11:** a crash completion marker (RC-05), and disk-full and clock-offset injection (RC-06 to RC-08).
2. **CV-12 and F-15:** live capture of W-J (DEC-057).
3. **The DEC-057 retrievals**, run through a real transport for `fetch()`: the 30-day REST pull with `AssetPairs`, the HEAD requests, and the 2026Q4 archive.
4. **The user's review** of the contract and plan (P02 task 6), and a dated G02 approval.

## 4. Findings for the user

**1. Archive and REST disagree on one bar (F-4h).** XBTUSD 2026-09-10:

| | Trade count | Volume |
| --- | --- | --- |
| Archive (generated 2026-10-01) | 109,136 | `2625.5456006904283` |
| REST (retrieved 2026-10-27) | 109,159 | `2625.56074813` |

- *Inference:* either REST data changed after the archive was generated, or the two are built from different trade sets.
- Either way, archive values are **not** always what REST serves later, which is T-2a's second condition. Under T-2a, such a difference is a correction with its own `available_at`.

**2. Comparison rule: current against Proposed.**

| Rule | Mismatches (of 31 bars per pair) |
| --- | --- |
| **Current** event contract §4.1: archive volume rounded to 8 decimals must equal REST | **4.** XBTUSD 2026-09-10 (real), plus ETHUSD 2026-09-11, 09-15 and 09-21, which are float rounding: after rounding, the differences are 1 to 2 × 10⁻⁸ |
| **Proposed:** relative volume tolerance of 10⁻⁹, as in the P01 sample | **1** (XBTUSD 2026-09-10) |

The current rule is the official result until the user decides. The Proposed rule is reported alongside it, not substituted for it.

**3. Proposed refinement to event contract §3: bar keys.**
- Bars now key on `bar_start` (`native_seq` = the bar start), not the row index.
- A row index makes the key shift when a revision inserts a row, and when the 30-day REST pull's sliding window moves.
- The contract allows "native ID or row index"; this narrows it for bars. It is **Proposed**, for the user to confirm.
