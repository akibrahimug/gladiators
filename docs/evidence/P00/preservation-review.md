# P00 source preservation review

[Task card](../../tasks/TASK-P00-001.md) · [Import manifest](../../sources/originals/import-manifest.md) · [Recovered index](../../sources/originals/RECOVERED.md) · [Milestones](../../milestones.md)

Review for [TASK-P00-001](../../tasks/TASK-P00-001.md). Date: **2026-10-23, Europe/London**. Coordinator: Claude Code main session, with `gladiator-spec-reader` (version inventory) and `gladiator-reviewer` (independent comparison).

Reviewed revision: `master` @ `2577b6bd4116ea0c161ef7fd60fbf3f8f9b4745f`, which contains import commit `76e9daa` ([PR #3](https://github.com/akibrahimug/gladiators/pull/3)), plus the claim commit `3841fb6` on `task/TASK-P00-001-preservation-review`.

Scope: preservation, identity and version evidence only. This review does not reconcile the architecture (TASK-P00-002), accept a baseline or pass G00. No preserved original was edited, extracted again, executed or installed.

## Summary

| Criterion | Result |
| --- | --- |
| Identity, source location, retrieval date and preserved copy for every supplied item | Met at archive level. Each archive has a filename, SHA-256, the conversation URL, retrieval date 2026-10-23 and a method line. No per-archive message or download-control ID is recorded (PF-04) |
| Byte comparisons and SHA-256 digests | Met **for the archives as committed in `76e9daa`**: all 10 archives and all 405 members verified. Whether those archives equal the browser downloads is not verified (PF-01, an accepted limitation) |
| Exported chat text labelled as an export | No exported chat text is in the import. The earlier captures are correctly labelled as a reader capture and a readable derivative |
| Explicit version headers and supersession evidence distinguished from inference | Done in [version and supersession evidence](#version-and-supersession-evidence) |
| Missing or conflicting sources have a disposition | Done in [findings and dispositions](#findings-and-dispositions); lineage conflicts are carried to TASK-P00-002 |
| Independent comparison | See [independent review](#independent-review) |

## Byte and hash preservation

Method: a read-only Python script, kept outside the repository, opens each archive as data with `zipfile`. It never extracts or executes members. It checks:

- each archive's SHA-256 against the inventory and `RECOVERED-SHA256SUMS`;
- `ZipFile.testzip()` integrity;
- the ZIP member list against the inventory, and every member's bytes against its extracted copy under `releases/<archive name>/`;
- each member's SHA-256 and size against its inventory record and `RECOVERED-SHA256SUMS`;
- that no extracted tree holds a file absent from its ZIP, and no member path is absolute or contains `..`;
- that every extracted file is tracked in Git, and no commit after import modifies or deletes a preserved file.

Results at `3841fb6`:

| Check | Result |
| --- | --- |
| Archives | 10; all digests match the inventory and `RECOVERED-SHA256SUMS`; all pass `testzip` |
| Members | 405; all byte-identical to their extracted copies; all inventory records (path, SHA-256, size) correct |
| `shasum -a 256 -c RECOVERED-SHA256SUMS` | 415 of 415 OK (10 archives + 405 members) |
| Extra or missing files in release trees | None |
| Unsafe member paths | None |
| Tracked files under `docs/sources/originals/` | 421: 405 members, 10 archives and 6 intake/record files; none unaccounted for |
| Git history | Preserved files only added (`76e9daa`); never modified or deleted |
| File types | 380 Markdown, 12 Python, 8 bytecode (`.pyc`), 5 CSV. No file has an executable mode |
| Captured sources | `docs/sources/captured/SHA256SUMS` 3 of 3 OK; unchanged |

The working tree also holds 13 untracked copies named with a " 2" suffix (for example `RECOVERED 2.md` and `archives/trading-ai-spec 2.zip`) and 10 " 2" release folders holding only empty subdirectories. All 13 files are byte-identical to their tracked counterparts. They are not part of the import, are left untouched and are excluded from every commit (PF-06).

## Release order

Stored ZIP member timestamps order the releases the same way as their names. Only `trading-ai-core-kernel-v2.zip` and `gladiator-core-reviewed-v5.zip` carry UT (UTC) extra fields; the other 8 archives store bare DOS times with no time zone, so their zone is unknown. Shared DOS times for files carried from v2 into v3 suggest one clock, but if the DOS-only times were local time the v2/v3 order by latest timestamp could flip.

| Archive | Members | Stored member timestamps |
| --- | --- | --- |
| `trading-ai-spec.zip` | 14 | 2026-10-21 20:20 |
| `trading-ai-core-kernel-v2.zip` | 25 | 2026-10-21 20:22 – 20:49 |
| `gladiator-core-components-v3.zip` | 43 | 2026-10-21 20:22 – 20:54 |
| `gladiator-core-research-update-v4.zip` | 44 | 2026-10-21 20:22 – 21:04 |
| `gladiator-core-reviewed-v5.zip` | 43 | 2026-10-22 08:33 – 08:35 |
| `gladiator-upstream-issues-v6.zip` | 42 | 2026-10-22 15:25 – 15:26 |
| `gladiator-competitive-intelligence-v7.zip` | 43 | 2026-10-22 15:25 – 15:30 |
| `gladiator-algorithm-assurance-v8.zip` | 46 | 2026-10-22 15:25 – 15:33 |
| `gladiator-market-awareness-v9.zip` | 51 | 2026-10-22 15:25 – 15:44 |
| `gladiator-order-flow-ledger-v10 (1).zip` | 54 | 2026-10-22 15:25 – 15:46 |

Timestamps and names are ordering evidence. Neither states that a release supersedes another.

## Version and supersession evidence

From the spec-reader's inventory. The coordinator re-checked the v1.0 header, the v6/v3 and v10/v8 hash identities, and that file 17's "v1.0" refers to a third-party release. Paths are relative to `releases/<release>/trading-ai-spec/`.

| Release | Explicit in-file version statement | Explicit supersession or update statement | Inference only |
| --- | --- | --- | --- |
| trading-ai-spec | `README.md:3` "Architecture specification v0.1" | None | That it is the initial package |
| trading-ai-core-kernel-v2 | `core-engine/KERNEL.md:3` "normative specification, v0.2" (kernel document only; identical through v10) | Within-document only ("supersedes dashboard work") | That "v2" means release v0.2 |
| gladiator-core-components-v3 | None in the tree | None | v0.3; only a later file (`17…:3`, v4 onward) refers to "the v0.3 specifications" |
| gladiator-core-research-update-v4 | `README.md:73` "researched update (v0.4)"; `## v0.4` amendment headings in each component | `17-RESEARCH-AUDIT-2026-10.md:3` "updates to the v0.3 specifications" | None |
| gladiator-core-reviewed-v5 | `18-ADVERSARIAL-REVIEW-2026-10-22.md:1` "GLADIATOR v0.5"; `## v0.5` component headings | `18…:6` "Reviewed the existing v0.4 Markdown components" | Observed in the bytes: v5 components are the v3 text plus `## v0.5` sections, with no `## v0.4` heading in any v5 component (16 in v4). Inference only: whether dropping the v0.4 amendments was intended |
| gladiator-upstream-issues-v6 | `19-UPSTREAM-ISSUES-AND-FORK-POLICY.md:3` "Version: 0.6 draft" (file 19 only) | None | That it follows v5 |
| gladiator-competitive-intelligence-v7 | None ("0.7" appears nowhere) | None | v0.7, from the filename only |
| gladiator-algorithm-assurance-v8 | `README.md:80` "(v0.8)" | None | None |
| gladiator-market-awareness-v9 | `README.md:85` "v0.9 market-awareness architecture"; `24…:3` "v0.9 design"; "(v0.9 amendment)" headings | None | None |
| gladiator-order-flow-ledger-v10 (1) | `core-engine/components/27-ORDER-FLOW-AND-LEDGER-INTELLIGENCE.md:3` "architecture revision v1.0 (2026-10-22)". This is the only in-file v1.0 statement. Other headers keep earlier versions (README v0.1, KERNEL v0.2, 19 v0.6, 24 v0.9) | None naming an earlier release. `README.md:91` "The architecture now includes [27]"; `24…:5` defers to 27 | That v10 is the latest release and supersedes v9 |

### v1.0 identification

| Claim (source) | Confirmable from repository files? |
| --- | --- |
| Conversation heading "GLADIATOR v1.0 — Architecture update" ([manifest](../../sources/originals/import-manifest.md)) | No. The text appears only in the manifest; no capture preserves it (PF-02) |
| "Download updated GLADIATOR project" control (manifest) | No; same as above (PF-02) |
| The archive filename identifies v1.0 (manifest) | Partly. The filename says "v10 (1)", not "v1.0"; the [intake guidance](../../sources/originals/README.md) treats a filename as a claim to check |
| File 27 supplies the v1.0 architecture (manifest) | Yes for the label: `27…:3` says "architecture revision v1.0". That it is the architecture the user requested rests on the conversation |
| The v1.0 download has 54 files ([recovered index](../../sources/originals/RECOVERED.md)) | Yes as a count of the v10 archive |
| "The v1.0 order-flow architecture supersedes earlier proposals" (recovered index) | No explicit text; inference (PF-03) |

## Findings and dispositions

| ID | Finding | Disposition |
| --- | --- | --- |
| PF-01 | Byte comparison is against the archives as committed in `76e9daa`. The original download location (`~/Downloads`) was not readable from this session. The link between the browser downloads and that commit rests on the import commit, the inventory `method` line and PR #3's statements. PR #3's Git-blob check shows only that the local commit equals what was pushed | Accepted limitation, coordinator decision 2026-10-23: criterion 2 is scoped to the committed archives. Only the user can close it, by checking the downloaded ZIPs against `RECOVERED-SHA256SUMS` |
| PF-02 | The conversation evidence behind the v1.0 identification (heading and download control) is not preserved in the repository | Open; needs the user's signed-in access. Proposed follow-up: capture those messages as a labelled message extraction under `docs/sources/captured/`, with message IDs and checksums |
| PF-03 | No release explicitly supersedes another. The recovered index's "v1.0 … supersedes earlier proposals" is an inference from naming, timestamps and file 27 | Recorded as inference. TASK-P00-002 and the G00 reviewer decide precedence |
| PF-04 | No archive is linked to a source message ID or download control; the inventory has only a general `method` line. The v10 archive name has a "(1)" suffix that looks like a browser duplicate-download suffix. The inventory `method` line ("identical ZIP copies deduplicated by SHA-256") and the [recovered index](../../sources/originals/RECOVERED.md) suggest duplicates existed and were kept once, but which filenames were dropped is not recorded | Open, low severity. Closes with PF-02 if the capture records which message produced each download |
| PF-05 | Releases are not cumulative. The v0.4 component amendments exist only in v4: v5 components are the v3 text plus `## v0.5` sections (no `## v0.4` heading in v5; 16 in v4). The v0.5 amendments and `audit/` code exist only in v5. v6 builds on the v3 text again: 15 of the 18 component files it shares with v3 are byte-identical (for example `02-ARENA.md`, `01-CORE-KERNEL.md`, `10-DATA.md`, `13-EXECUTION-AND-LEDGER.md`), while `04-MANAGEMENT.md` and `07-CODE-OF-CONDUCT.md` add upstream/fork sections and `components/README.md` differs. v10's `23-CORE-ASSURANCE-AND-PEER-REVIEW.md` equals v8's and lacks v9's amendment. v10's `README.md:75` and `18…:6,17` refer to content v10 lacks | Conflict preserved, not resolved. All 10 releases stay authoritative inputs; v10 is not treated as a complete superset. Carried to TASK-P00-002 for a per-file lineage decision |
| PF-06 | 13 untracked " 2" copies and 10 " 2" release folders (empty subdirectory trees, no files) sit under `docs/sources/originals/` | Not part of the import; byte-identical copies. Left untouched for the user to remove |
| PF-07 | Intake documents still said no originals were imported or that v1.0 was missing (source register status and SRC-003 row, intake README, checklist intro), contradicting their 2026-10-23 banners. Banners and `RECOVERED.md` also called v10 "complete" or the superseding architecture without qualification | Corrected in this task with dated wording and qualifiers pointing to PF-02, PF-03 and PF-05; earlier states remain in Git history |

## Independent review

Reviewer: `gladiator-reviewer`, run on 2026-10-23 against `2577b6b..f21ae9a`, using its own method: `shasum -c`, `unzip -tq`, `zipinfo` member lists against `find`, and every member streamed with `unzip -p | shasum` against its extracted copy. Nothing was extracted into the checkout or executed.

Results: 415 of 415 checksums OK; 10 of 10 archives without errors; member lists identical (405 files); 405 of 405 members byte-identical; all inventory records correct; no unsafe paths or symlinks; all files mode 100644; no change to preserved files after `76e9daa`; captured checksums 3 of 3 OK. Spot-checks of the version table all confirmed. **No blocker; 4 material and 6 minor findings, all in evidence or intake wording, none in the preserved bytes.**

| ID | Severity | Finding | Disposition |
| --- | --- | --- | --- |
| M1 | Material | Intake README still said v1.0 "remain[s] missing" while PF-07 claimed it was corrected | Fixed: paragraph rewritten in the past tense with a dated status |
| M2 | Material | PF-05 understated non-cumulation: v0.4 amendments are already absent in v5; the v5 row labelled an observable removal as inference | Fixed: PF-05, the v5 row and the manifest bullet corrected |
| M3 | Material | Source register said "preservation verified" before the review was resolved | Fixed: the register now points to the task card for state; the card records the result |
| M4 | Material | PF-01 cited PR #3's Git-blob check, which does not link the downloads to the commit | Fixed: PF-01 and the summary state the limitation and scope criterion 2 to the committed archives |
| m1 | Minor | Timestamps labelled UTC, but only v2 and v5 carry UT fields | Fixed |
| m2 | Minor | "v6 component files byte-identical to v3" too broad (15 of 18) | Fixed in PF-05 |
| m3 | Minor | Card scope note misnamed the P00 phase's planned evidence file | Fixed: scope note names both files |
| m4 | Minor | Unqualified "complete 54-file v1.0 package" and "supersedes earlier proposals" remained in banners, `RECOVERED.md` and the manifest | Fixed with dated qualifiers |
| m5 | Minor | Checklist version-header tick backed only at release level | Fixed: tick qualified; per-file inventory left to TASK-P00-002 |
| m6 | Minor | PF-04 omitted the inventory's deduplication note; PF-06 called folders "empty" | Fixed |

Fix verification: see the [task card](../../tasks/TASK-P00-001.md).

## Limits

- Prototype `.py` and `.pyc` files are preserved as historical material only. They were read as bytes, never executed or imported.
- This review establishes preservation and identity evidence. Architecture content, requirement mappings and lineage decisions belong to TASK-P00-002. G00 remains pending.
