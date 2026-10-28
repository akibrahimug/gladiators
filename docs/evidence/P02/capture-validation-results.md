# P02 capture validation results: held files (TASK-P02-002)

[Task](../../tasks/TASK-P02-002.md) · [Validation plan](capture-validation-plan.md) · [Event contract](event-contract.md) · [Capture and recovery](capture-and-recovery.md)

**Status: results, 2026-10-28.** Run at code revision `90071b5` under DEC-058 (held files only), against the thresholds approved in DEC-056.
- **Not a G02 decision.** G02 needs the remaining criteria (§3) and the user's dated approval.
- **No network:** no network access, no live capture.
- **Inputs:** the P01 sample files, identified in the scratchpad manifest (SHA-256 `2492dc56…261aa9`).

**How it was run.**
- **Unit tests:** `python3 -I -m unittest discover -s tests` passed all 21 tests. They use synthetic data only.
- **Validation:** `PYTHONPATH=src python3 -m gladiator_capture.validate --sample-root <scratchpad> --out <scratchpad>/p202-run`, run from `/`. `PYTHONPATH` is needed because `-I` would drop it; the held files are only read, never imported.
- **Report:** `report.json`, SHA-256 `712112b72bf5aa567d489f82e83c8c5953635a2d4b1ade07e0c741f94ad818e4`, kept outside the repository.
- **Retrieval times:** held files have no recorded retrieval journal from P01. Each file's modification time stands in for `retrieved_at`.

## 1. Criteria

| ID | Result | Evidence |
| --- | --- | --- |
| CV-01 | **Met by construction; not separately counted.** Every record carries `raw_id`, `raw_locator` and `rights_id`, and the raw store indexes each object's request and source approval | `records.py`; `rawstore.py` |
| CV-02 | **Pass (W-A).** 0 of 620 records are missing a time or the basis. Units: `ms` for 2024-12 and `us` for 2025-01 | report W-A |
| CV-03 | **17 of 18 fixtures pass.** F-15 is live and was not run | report fixtures |
| CV-04 | **Pass.** F-02b, F-03, F-06 and F-06b behave as expected. W-A: 620 rows, 0 quarantined | report |
| CV-05 | **Pass.** W-E: XBTUSD has 12 and ETHUSD 6 `status_unknown` intervals; W-A has 0 | report W-E, F-04 |
| CV-06 | **Pass.** The coverage reports match the expected counts: W-A 620 / 620 / 0 / 0 / 0; XBTUSD 4,731 rows and 12 gaps; ETHUSD 4,067 rows and 6 gaps. The fail-closed trigger is exercised only through F-18 | report W-A, W-E |
| CV-07 | **Pass.** F-18: 346/365 is disqualified and 347/365 qualifies. Minimum 365-day coverage after 2016: XBTUSD 1.0000, ETHUSD 0.9973 | report W-E, F-18 |
| CV-08 | **Pass (W-A).** 0 records lack `venue`, `source_id` or `feed_id` | report W-A |
| CV-09 | **Pass.** Two runs over W-A give the same output hash (`7d519567…13ba`) | report W-A |
| CV-10 | **Pass.** F-16 shows 0 records visible on 2025-01-07, and 31 from `Last-Modified`. F-09 shows version 1 before the revision and version 2 after | report |
| CV-11 | **Partial.** Exercised: RC-04 (F-01 checksum mismatch), RC-05 (idempotent re-ingest, F-02a), RC-12 (F-09) and RC-02 (F-14, simulated). **Not exercised:** RC-01, RC-03, RC-06, RC-07 and RC-08. They need network, disk-fault or clock injection, which is not in this held-files implementation | — |
| CV-12 | **Not run.** Live capture (W-J) needs a capture implementation; it is authorised by DEC-057 | — |

## 2. Window results

| Window | Result |
| --- | --- |
| W-A | 20 of 20 checksums verified. `Last-Modified` is held for 2 files (62 records `archive_published`); the other 18 fall back to `retrieved` (558 records). 0 records flagged late, since monthly files are exempt |
| W-B | Daily file flagged as rewritten (it is in the changelog). The monthly file is not flagged, and its 2022-03-08 row equals the revised daily file (TH-4 trade-off as documented) |
| W-C | 1 proposed epoch break, on 2022-05-31: a 17-day gap and a ×20,000 factor, `review_status = proposed` |
| W-D | 2,689,488 trades, `us`, 0 data gaps |
| W-E | XBTUSD 2013-10-06 to 2026-09-30, ETHUSD 2015-08-07 to 2026-09-30, both `available_at` 2026-10-01. Manifest mismatch logged: 1,760 pairs and 12,350 files declared, against 1,759 and 12,349 present |
| W-F | All 4 delisted pairs end on a quarter-end (upper bounds) |
| W-G | 1,436 pairs and 10,052 CSVs, matching its manifest; `checksum_status = none_published` |
| W-H | 57 completed bars per pair, with the incomplete bar dropped. 55 of 57 are flagged late, as expected. **One XBTUSD bar differs from the archive** (§4) |
| W-I | The FOMC statement gives "2:00 p.m. EDT" (`stated_release`). The minutes give "2:00 p.m." (`first_published`). COT has no stated time (`first_published`, `Last-Modified` 19:27:36 UTC) |

## 3. What G02 still needs

1. **CV-11:** fault injection for RC-01, RC-03 and RC-06 to RC-08.
2. **CV-12 and F-15:** live capture of W-J, authorised by DEC-057.
3. **The DEC-057 retrievals:** the 30-day REST pull, the HEAD requests and the 2026Q4 archive, each run through code that supports it.
4. **The user's review** of the contract and plan (P02 task 6), and a dated G02 approval.

## 4. Findings for the G02 reviewer

**F-4h: the archive and REST disagree on one bar.** XBTUSD, 2026-09-10:

| | Trade count | Volume |
| --- | --- | --- |
| Archive (generated 2026-10-01) | 109,136 | 2625.5456… |
| REST (retrieved 2026-10-27) | 109,159 | 2625.5607… |

The REST response has 23 more trades. The other 30 compared XBTUSD bars and all 31 ETHUSD bars agree.
- *Inference:* either Kraken's REST data changed after the archive was generated, or the two are computed from different trade sets. Either way, archive values are **not** always what REST serves later, which is the second T-2a condition.
- Under T-2a, such a difference is a correction with its own `available_at`. The F-4h route (validation plan §4) is the way to measure how often this happens.

**Proposed change to the event contract's §4.1 comparison rule.**
- The current rule, "round archive volumes to 8 decimals, then compare", is too strict. ETHUSD volumes differ by 1 to 2.5 × 10⁻⁸ after rounding: for example archive `75625.84331052462` against REST `75625.84331050`. That is a relative difference of about 3 × 10⁻¹³, and the archive is binary-float text.
- The implementation therefore compares volumes with a **relative tolerance of 10⁻⁹**, as the P01 sample did.
- This is **Proposed** and needs the user's confirmation, because it changes a Proposed rule in the event contract.
