# P01 Binance general terms and venue status (F-5b, F-7b)

[Task](../../tasks/TASK-P01-008.md) · [Reassessment](source-reassessment.md) · [Source registry](source-registry.md) · [Data-access decision](data-access-decision.md) · [P01 phase](../../phases/01-research-and-data-access/README.md)

**Status: research evidence for G01, 2026-10-25.** This file selects no source. It authorises no account, key registration, vendor contact, data download, capture, spending or trading. It is the coordinator's reading of published text, not legal advice.

**Why this file exists.** The [reassessment](source-reassessment.md#new-follow-up-items) left F-5b open: Binance's general terms "returned no readable terms text to automated fetch". The user had noted that Binance Vision's "broader eligibility and retention conditions still need checking before selection" (DEC-033). This file reads those terms and follows up F-7b (Binance venue status).

**Precedence.** Where this file changes a status recorded in the reassessment, the registry, the map or the data-access decision, this file takes precedence. The [status changes](#status-changes) table lists every change.

## Method and documents read

The live terms page [binance.com/en/terms](https://www.binance.com/en/terms), which redirects to `/en-GB/terms`, rendered navigation and footer only, both to automated fetch and in a real Chrome browser from the UK on 2026-10-25. The coordinator therefore read the PDF versions that Binance publishes on its own CDN (`bnbstatic.com`). Text was extracted locally with macOS PDFKit. For each `bin.bnbstatic.com/static/cms/.../file/<hash>.pdf` URL, the file's SHA-256 equals the hash in the URL; the UK file's URL carries a hash suffix only.

| ID | Document (as titled) | Date stated | Parties / scope | SHA-256 |
| --- | --- | --- | --- | --- |
| BT-1 | [Terms of Use](https://bin.bnbstatic.com/static/cms/cg08ou2ak0tn7mcplvfg/file/47a848de135d5747a84c1f66307920fe3d23eca2f500accc64e136f1499ba387.pdf) | "Effective Date: 5 January 2026" | The "ADGM Binance Entities", the first being "NEST EXCHANGE LIMITED (formerly known as Nest Services Limited)" | `47a848de…` (equals the URL) |
| BT-2 | [Prohibited Use Policy](https://bin.bnbstatic.com/static/cms/cg08ou2ak0tn7mcplvfg/file/3c287bd60863eccef6a16b8580190c96d4c9414931928d7fafdb227bf967cd63.pdf) | "Last updated: 5 January 2026" | Applies with the Terms of Use | `3c287bd6…` (equals the URL) |
| BT-3 | [List of Prohibited Countries](https://bin.bnbstatic.com/static/cms/cg08ou2ak0tn7mcplvfg/file/2dead3dd5d9bccb32694e2f0fe5c7f2c6b583e7a6f851296edef7088340e6df5.pdf) | "Updated: 5 January 2026" | Referred to by BT-1 and BT-4 | `2dead3dd…` (equals the URL) |
| BT-4 | [Terms of Use - United Kingdom](https://public.bnbstatic.com/static/terms_doc/2023_07_27_terms_of_use_uk_consolidated-f8ef267b2.pdf) | "Last Updated: 27 July 2023", "Effective Date: 10 August 2023" | "Nest Services Limited"; the bundled privacy notice says UK users' operating entity "will be Nest Services Limited" | `cb7d0e67…f8ef267b2` |

**Read and set aside** (they do not govern a UK individual):

| Document | Date stated | Parties / scope | SHA-256 |
| --- | --- | --- | --- |
| [Terms of Use (Australia)](https://bin.bnbstatic.com/static/cms/cg08ou2ak0tn7mcplvfg/file/726b56c4be2cd37669996d366e827c3f7861eab81157b48b78fc3890985833dc.pdf) | "Last Updated: 16 July 2026" | "apply to users who reside in Australia"; InvestbyBit Pty Ltd trading as Binance Australia | `726b56c4…` (equals the URL) |
| [Terms of Use (New Zealand)](https://bin.bnbstatic.com/static/cms/cg08ou2ak0tn7mcplvfg/file/1dd5e6a2445315868bd07ea1861177cb66a7a85f3de974436e6ec1c9a6706d4c.pdf) | "Last Updated: 17 August 2026" | "apply to users who reside in New Zealand"; InvestbyBit Limited trading as Binance New Zealand | `1dd5e6a2…` (equals the URL) |

**Which version governs a UK user today is not established.** Relevant BT-1 text:
- BT-1 names Nest Exchange Limited "formerly known as Nest Services Limited", the entity BT-4 names for UK users.
- BT-1's "Novation Notification" says that if you have "an existing account with Nest Exchange Limited (formerly known as Nest Services Limited)", continuing to use the services transfers your relationship to the ADGM Binance Entities.
- BT-1 also says that "where any Local Terms apply … such Local Terms shall supplement the Agreement".

From this the coordinator infers that BT-1 is the likely successor for UK users, possibly supplemented by UK Local Terms. No text read names the UK, and the live page could not be rendered. Both versions are assessed below.

## F-5b: eligibility, automated access and retention

| Question | BT-1 / BT-2 / BT-3 (2026) | BT-4 (UK, 2023) | Outcome |
| --- | --- | --- | --- |
| What the eligibility rule gates | BT-1 §2.1 opens "To be eligible to register for a Binance Account and use the Binance Services" | BT-4 §2.1: the same opening | Binance Vision needs no account, but the rule also covers *using* the Binance Services. Whether the archive is a "Binance Service" is not stated. Both versions define the services as "the services offered by us to you through the [Binance] Platform", the Platform as reached via "Sites", and "Sites" as "our Website and any other websites, pages, features, or content we own or operate" |
| Location limb | BT-1 §2.1(f): not located or resident in a jurisdiction "where it would be illegal under Applicable Law" to use the services, or "listed in our List of Prohibited Countries" | BT-4 §2.1(g): the same two limbs | **The UK is not on BT-3.** BT-3 lists the United States; Canada and the Netherlands; and Cuba, North Korea, Iran, Crimea and the so-called Donetsk and Luhansk People's Republics. No text read makes downloading a public research archive illegal for a UK individual. The FCA measures on Binance Markets Ltd (registry SR-03) concern regulated activity; the coordinator found nothing tying them to `data.binance.vision` |
| Person limb | "not be a Restricted Person" (sanctions lists) | The same | Not applicable to the user, as far as the coordinator knows |
| Automated access | BT-2 §I prohibits "deep linking, web crawlers, bots, spiders, automated devices, programs, scripts, algorithms…" to access or copy the Binance Services, "except as expressly permitted" | BT-4 §26 prohibits the same means used "to obtain or attempt to obtain any materials, documents or information in any manner not purposely provided through Binance Services" | **No concrete restriction for scripted downloads of the archive.** Under BT-2, the dataset terms §4.1 expressly permit "algorithmic historical backtesting for purely personal non-production research", and the archive README points to "helper scripts in both the `python` and `shell` folders of this repository for downloading from the website". Under BT-4, the archive files are "purposely provided" for download. **Operating conditions** under both versions: no "unreasonable" load on Binance's infrastructure, and no bypassing of robot-exclusion headers. These apply to the sample plan's downloads |
| Retention and copying | BT-2 §I: users must not "modify, adapt, combine, … copy, replicate, transmit, alter, or otherwise exploit any part of the Binance Platform". BT-1 §27 licenses Binance IP "solely as necessary to allow you to receive the Binance Services for non-commercial personal or internal business use". No clause addresses keeping public market data | BT-4 §26: users must not "copy, download, store … or create derivative works" of "Binance IP" (defined to include database rights) | **Ambiguous under both versions.** Read literally, BT-2 §I and BT-4 §26 each conflict with the dataset licence, which grants reproduction (CC §2(a)(1)). Neither version says whether a separately licensed dataset is carved out. Both conflicts arise only if the archive is part of the Platform or Services. BT-1 §27's purpose, "non-commercial personal" use, is consistent with DEC-030 |

**Result.** F-5b is narrowed to F-5b′, which stays **Unresolved**:
- **Eligibility:** no concrete UK restriction found. The UK is not on the prohibited-countries list. The eligibility rules cover registering an account and using the Binance Services; whether the archive is a Binance Service is not stated.
- **Automated access:** consistent with the dataset terms under both versions, subject to the load and robot-exclusion conditions.
- **Retention and copying:** ambiguous under both versions, for the same reason.
- **F-5b′ (Unresolved):**
  1. whether `data.binance.vision` is part of the Binance Platform or Services;
  2. if it is, how the copy and store clauses (BT-2 §I; BT-4 §26) interact with the dataset licence;
  3. which general terms, and any UK Local Terms, currently govern a UK individual.

  Closure evidence: Binance's current UK terms rendered in full, or a reviewer-approved reading. Like F-4a for Kraken, this is a terms-ambiguity item for the G01 reviewer, not a reason to wait for a vendor reply (DEC-033).

SR-04 stays **Conditional**. By precedence, this file supersedes the reassessment's S-1 and S-2 lines for SR-04, which still cite F-5b. On S-1, no concrete UK eligibility restriction was found. On S-2, retention is not restricted by the dataset terms but is ambiguous under the general terms. Both lines now point to F-5b′.

## F-7b: Binance venue status

| Need | Finding | Outcome |
| --- | --- | --- |
| Forward status | [System Status](https://developers.binance.com/docs/wallet/others/system-status), as fetched 2026-10-25: `GET /sapi/v1/system/status`, IP weight 1. The page lists no API-key header and returns `status` "0: normal，1：system maintenance" with `msg` | A documented forward endpoint. The coordinator infers that it is **platform-wide**, because it returns one 0/1 value with no symbol or market parameter. Using it would be Binance live access. That is a REST `/sapi` endpoint, not the SR-03 WebSocket, but like SR-03 it has no rights assessment, so the coordinator treats it as **Unresolved** |
| Historical status | No status history endpoint or archive found. As fetched, the same page also lists Spot Delist Schedule (`/sapi/v1/spot/delist-schedule`), which requires an API key and is forward-looking. Maintenance appears in Binance announcements, which are unstructured and were not read | **Unresolved: no source found.** Archived Binance bars cannot be gated on recorded venue status |

**Result.** F-7b stays **Unresolved**, narrowed as follows:
- **Forward:** a platform-wide endpoint exists, but its use rights are unassessed.
- **Historical:** there is still no source. Historical bars need the same reviewer-approved rule as F-7, for example treating missing or zero-volume bars as status-unknown.

F-5c (delisted symbols) is unchanged. The delist-schedule endpoint needs a key and is forward-looking. The README says "All symbols are supported" but does not mention delisted symbols, and its fetch script targets "all current running symbols". The sample plan still checks the archive.

## Status changes

| Row | Before | After | Reason |
| --- | --- | --- | --- |
| F-5b | Open: broader Binance terms unreadable | **F-5b′, Unresolved (narrowed):** no UK restriction found; automated access consistent, subject to operating conditions; retention ambiguous under both versions; archive's status as a Binance Service, and the governing version, unconfirmed | BT-1 to BT-4, read 2026-10-25 |
| SR-04 Binance Vision | Conditional (F-5b) | Conditional (F-5b′) | This file |
| F-7b | Open: no historical or forward Binance status source | **Unresolved (narrowed):** forward platform-wide endpoint documented, rights unassessed; historical none, needs the F-7 rule | Binance System Status docs, read 2026-10-25 |
| Reassessment: F-5b and F-7b rows; header | F-5b, F-7b open | Pointer notes to this file | This file |
| Registry and map: precedence notes | — | Pointer note added | This file |
| Data-access decision: daily bars (S-1, S-2); historical trades; second venue (H-OF6) | F-5b | F-5b′; S-1 notes no UK restriction found | This file |
| Data-access decision: venue status | F-7b: no Binance source | F-7b narrowed: forward platform-wide only, no history | This file |
| Data-access decision: Binance retention row; dependencies; status line | F-5b | F-5b′: ambiguous under the general terms | This file |
| P01 phase README: progress note | — | TASK-P01-008 sentence added | This file |
