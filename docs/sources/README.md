# Source register and preservation

> **Source recovery update — 2026-10-23:** Original GLADIATOR releases, including the complete 54-file v1.0 package, are now imported. See the [recovered document index](<originals/RECOVERED.md>). Earlier missing-source statements below are historical. G00 still awaits reconciliation/review.

[Project home](../../README.md) · [Requirements](../requirements.md) · [Source map](source-map.md) · [Original-specification intake](originals/README.md)

Status: **documentation scaffold; original v1.0 specification not recovered**. Access date: **22 October 2026, Europe/London**.

The referenced chat was inspected after the user confirmed that the specifications were created there. The available reader returned five recent turns, no attachments and no older-page cursor. The user messages are readable; every assistant response is a content-reference marker. Those markers do not contain the specification text. No original GLADIATOR specification was found in the local search. A direct browser attempt reached a sign-in screen; no sign-in was attempted.

This workspace preserves what was actually retrieved and distinguishes it from newly prepared planning documents. The present structure must not be labelled an authoritative reconstruction of the latest v1.0 architecture. Baseline gate **G00 remains pending** until the original specifications can be read, preserved and reconciled.

## Project sources

| ID | Source | Evidence and status | Use |
| --- | --- | --- | --- |
| SRC-001 | [Current request and clarification](captured/current-request.md) | User asks for GLADIATOR documentation, a phased plan, IDE navigation and preservation; clarifies that the specs were created in the referenced chat. | Authorizes the documentation work and excludes live trading implementation. |
| SRC-002 | [Raw reader response](captured/conversation-reader.json) and [readable extraction](captured/recovered-user-messages.md) | Five user messages and five assistant reference markers recovered from conversation `6ad910c9-4a70-83ed-b819-7f12576a37c8`, “Day Trading Income Feasibility”. No attached files or older-page cursor returned. | Evidence of stated intent and terms such as Core, Judges and Managers. Does not establish their complete contracts. |
| SRC-003 | Latest GLADIATOR v1.0 order-flow/ledger architecture and original Markdown specifications | **Missing.** No original specification text or files recovered. [Unresolved assistant-message references](source-map.md#unresolved-assistant-message-references) identify possible recovery targets. | Required to reconcile the scaffold, confirm completeness and pass G00. |

## External technical references

These references establish observable data boundaries. They are not GLADIATOR design sources and cannot fill gaps in SRC-003.

| ID | Primary source | Limited purpose |
| --- | --- | --- |
| EXT-001 | [Nasdaq TotalView-ITCH 5.0 specification](https://www.nasdaqtrader.com/content/technicalsupport/specifications/dataproducts/NQTVITCHSpecification_5.0.pdf) | Defines exchange book-event messages. Helps distinguish observable order-book events from hidden intentions, private account balances or a universal money ledger. |
| EXT-002 | [Coinbase Exchange WebSocket feeds](https://help.coinbase.com/en/developer-platform/websocket-feeds/exchange) | Distinguishes public market-data channels from authenticated user/account information. Supports separate treatment of market events and the system’s own-account ledger. |

## Preservation rules

1. Keep the [captured reader JSON](captured/conversation-reader.json) unchanged. The readable extraction is a convenience copy with source IDs; it is not a replacement for the raw capture.
2. Store any recovered original Markdown files, exports and attachments under `originals/` byte for byte. Preserve filenames and relative paths where available. Never fix wording, formatting or links inside those copies.
3. Record each original in the [import manifest](originals/import-manifest.md), including source message, version evidence and SHA-256 digest. Preserve conflicting versions separately and document the relationship.
4. Put reconciled, navigable planning documents outside `originals/`. Mark additions and interpretations as proposed until compared with the original source.
5. Map every recovered specification to requirements, phases, components and milestone evidence. Run the [intake checklist](originals/intake-checklist.md) before considering G00 complete.

A checksum verifies that a file has not changed since capture. It does not establish that a missing conversation response has been recovered or that the specification collection is complete.
