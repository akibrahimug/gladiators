# Source-to-requirement map

[Source register](README.md) · [Requirements](../requirements.md) · [Original-specification intake](originals/README.md)

The mappings below relate recovered user intent to the new requirements scaffold. They are planning interpretations, not recovered v1.0 architecture. The [raw capture](captured/conversation-reader.json) remains the source of record; its five turns are ordered newest first. The [readable extraction](captured/recovered-user-messages.md) is chronological.

## Recovered intent

| User message ID | Recovered intent | Requirements supported |
| --- | --- | --- |
| `a0662db6-c8f5-4e18-9330-a2327ad47938` | Research publicly available information relevant to Core, Judges and Managers. | REQ-003, REQ-007, REQ-011 |
| `b7faa5c1-e64e-4705-a24e-0d578f23c77e` | Investigate established algorithms and adapt them carefully; pursue robustness. | REQ-007, REQ-009, REQ-010, REQ-011 |
| `9c53d5aa-dcab-4a43-9cfc-bc8bb280c496` | Identify market changes and relevant market-moving information. | REQ-002, REQ-003, REQ-008, REQ-009 |
| `72f9c1e2-1c3e-4998-8337-5ae595f9c368` | Prefer source events, order flow and volume over chart interpretation; investigate ledger access. | REQ-001, REQ-002, REQ-004, REQ-005, REQ-006 |
| `608958aa-5780-4eba-9ee0-733d9b3ae104` | Open an IDE and organize the documentation into phases. | REQ-011, REQ-012 |
| SRC-001 current request and clarification | Preserve existing specifications, use the latest architecture when recovered, create navigation, milestones and component traceability, and exclude live trading for this task. | REQ-003, REQ-011, REQ-012 |

“Near zero” error and access to “all things” moving markets are aspirations in the recovered conversation. They do not constitute evidence that such coverage or certainty is possible. The planning scaffold translates them into measurable data quality, coverage limits, research validation and risk-abstention requirements.

## Unresolved assistant-message references

Only the marker text below was returned. A marker is an identifier for possible recovery, not the response body and not proof that the message contains v1.0. Content must be read before its role, version or supersession can be assigned.

| Associated user message ID | Assistant message ID | Exact returned marker |
| --- | --- | --- |
| `a0662db6-c8f5-4e18-9330-a2327ad47938` | `2479d36b-99ea-4454-a2a0-24317f76bb53` | `::chatgpt-content-reference{index="2" source_message_id="2479d36b-99ea-4454-a2a0-24317f76bb53"}` |
| `b7faa5c1-e64e-4705-a24e-0d578f23c77e` | `807289bf-9dd5-4a37-b90b-86defe292ecb` | `::chatgpt-content-reference{index="4" source_message_id="807289bf-9dd5-4a37-b90b-86defe292ecb"}` |
| `9c53d5aa-dcab-4a43-9cfc-bc8bb280c496` | `c15bc74b-8501-4cc1-88f4-3dccdbeea528` | `::chatgpt-content-reference{index="4" source_message_id="c15bc74b-8501-4cc1-88f4-3dccdbeea528"}` |
| `72f9c1e2-1c3e-4998-8337-5ae595f9c368` | `46ce6aa0-17b4-48aa-b459-96fd488f1d44` | `::chatgpt-content-reference{index="4" source_message_id="46ce6aa0-17b4-48aa-b459-96fd488f1d44"}` |
| `608958aa-5780-4eba-9ee0-733d9b3ae104` | `8310da46-a461-415f-9797-7bff5ee2ce14` | `::chatgpt-content-reference{index="0" source_message_id="8310da46-a461-415f-9797-7bff5ee2ce14"}` |

The thread preview also returns the final marker above. It adds no specification content. The reader reports `nextCursor: null`, `hasMore: false` and an empty attachment list. These describe this capture’s availability; they do not prove that the full historical conversation contains only five turns.

## Reconciliation after recovery

For every imported original, record its path, digest, source message and any explicit version header in the [import manifest](originals/import-manifest.md). Then compare the original against each requirement and the phase/component traceability catalog. Mark each relationship as confirmed, conflicting, absent or superseded, with an evidence link. Unmatched specifications and unresolved conflicts keep G00 pending; do not silently rewrite either the source or the planning baseline.

## Recovery update — 2026-10-23

The original v1.0 download and earlier release archives have now been recovered from the signed-in browser. See [recovered documents](originals/RECOVERED.md). The marker limitations above describe the earlier reader capture only.
