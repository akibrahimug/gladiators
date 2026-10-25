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

**Read and set aside:** the Australian ("apply to users who reside in Australia", InvestbyBit Pty Ltd, 16 July 2026) and New Zealand (17 August 2026) Terms of Use. They do not govern a UK individual.

**Which version governs a UK user today is not established.** BT-1 names Nest Exchange Limited "formerly known as Nest Services Limited", the entity BT-4 names for UK users. The coordinator infers that BT-1 is the likely successor to BT-4 for UK users, but no Binance text read says so, and the live page could not be rendered. Both versions are assessed below.

## F-5b: eligibility, automated access and retention

| Question | BT-1 / BT-2 / BT-3 (2026) | BT-4 (UK, 2023) | Outcome |
| --- | --- | --- | --- |
| What the eligibility rule gates | BT-1 §2.1 sets the conditions to register for a Binance Account and use the Binance Services | BT-4 §2.1 opens "To be eligible to register for a Binance Account and use the Binance Services" | Binance Vision needs no account. Whether the archive is a "Binance Service" is not stated: both versions define it as "the services offered by us to you through the [Binance] Platform", and "Sites" as "our Website and any other websites, pages, features, or content we own or operate" |
| Location limb | BT-1 §2.1(f): not located or resident in a jurisdiction "where it would be illegal under Applicable Law" to use the services, or "listed in our List of Prohibited Countries" | BT-4 §2.1(g): the same two limbs | **The UK is not on BT-3.** BT-3 lists the United States; Canada and the Netherlands; and Cuba, North Korea, Iran, Crimea and the so-called Donetsk and Luhansk People's Republics. No text read makes downloading a public research archive illegal for a UK individual. The FCA measures on Binance Markets Ltd (registry SR-03) concern regulated activity, and the coordinator found nothing tying them to `data.binance.vision` |
| Person limb | "not be a Restricted Person" (sanctions lists) | The same | Not applicable to the user, as far as the coordinator knows |
| Automated access | BT-2 §I prohibits "deep linking, web crawlers, bots, spiders, automated devices, programs, scripts, algorithms…" to access or copy the Binance Services, "except as expressly permitted" | BT-4 §26 prohibits the same means used "to obtain or attempt to obtain any materials, documents or information in any manner not purposely provided through Binance Services" | **No concrete restriction for scripted downloads of the archive.** Under BT-2, the dataset terms §4.1 expressly permit "algorithmic historical backtesting for purely personal non-production research", and the archive README points to "helper scripts in both the `python` and `shell` folders of this repository for downloading from the website". Under BT-4, the archive files are "purposely provided" for download |
| Retention and copying | BT-1, BT-2: no clause on keeping public market data. BT-2 §I bars copying or exploiting "any part of the Binance Platform" | BT-4 §26: users must not "copy, download, store … or create derivative works" of "Binance IP" (defined to include database rights) | **Under BT-1/BT-2: no restriction found.** **Under BT-4: a literal tension** with the dataset licence, which grants reproduction (CC §2(a)(1)). Neither BT-1 nor BT-4 says whether a separately licensed dataset is carved out. This matters only if BT-4 still governs and the archive is a Binance Service |

**Result.** F-5b is **narrowed**, not closed:
- **Eligibility:** no concrete UK restriction found. The UK is not on the prohibited-countries list, and the eligibility rules attach to registering an account, which the archive does not need.
- **Automated access:** consistent with the dataset terms under both versions.
- **Retention:** unrestricted under the 2026 terms; ambiguous under the 2023 UK terms.
- **Residual item, F-5b′:** confirm which general terms currently govern a UK individual. If the 2023 UK terms (BT-4) still govern, decide how their "download, store" clause on Binance IP interacts with the dataset licence. Closure evidence: Binance's current UK terms page rendered in full, or a reviewer-approved reading. Like F-4a for Kraken, this is a terms-ambiguity item for the G01 reviewer, not a reason to wait for a vendor reply (DEC-033).

SR-04 stays **Conditional**. The S-1 and S-2 lines in the reassessment now read: no concrete restriction found in the general terms; F-5b′ open.

## F-7b: Binance venue status

| Need | Finding | Outcome |
| --- | --- | --- |
| Forward status | [System Status](https://developers.binance.com/docs/wallet/others/system-status): `GET /sapi/v1/system/status`, IP weight 1. The page lists no API-key header, and returns `status` "0: normal，1：system maintenance" with `msg` | A forward source exists but is **platform-wide**: not per symbol or spot-specific. Its use falls under Binance live access (SR-03), still Unresolved |
| Historical status | No status history endpoint or archive found. The same docs page's Spot Delist Schedule (`/sapi/v1/spot/delist-schedule`) requires an API key and is forward-looking. Maintenance appears in Binance announcements, which are unstructured and were not read | **No historical source.** Archived Binance bars cannot be gated on recorded venue status |

**Result.** F-7b is **narrowed**: a forward, platform-wide candidate exists if SR-03 is resolved, but there is still no historical source. For historical bars, F-7b needs the same reviewer-approved rule as F-7, for example treating missing or zero-volume bars as status-unknown. F-5c (delisted symbols) is unchanged. The delist-schedule endpoint needs a key and is forward-looking; the README says "All symbols are supported" but does not mention delisted symbols, and its fetch script targets "all current running symbols". The sample plan still checks the archive.

## Status changes

| Row | Before | After | Reason |
| --- | --- | --- | --- |
| F-5b | Open: broader Binance terms unreadable | **Narrowed to F-5b′**: no UK restriction found; automated access consistent; retention unrestricted under the 2026 terms and ambiguous under the 2023 UK terms; current governing version unconfirmed | BT-1 to BT-4, read 2026-10-25 |
| SR-04 Binance Vision | Conditional (F-5b) | Conditional (F-5b′) | This file |
| F-7b | Open: no historical or forward Binance status source | **Narrowed**: forward platform-wide endpoint documented (subject to SR-03); historical still none, needs the F-7 rule | Binance System Status docs, read 2026-10-25 |
| Data-access decision: Binance retention row; dependencies | F-5b | F-5b′; F-7b narrowed | This file |
