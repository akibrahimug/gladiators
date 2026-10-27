# Independent Codex PR reviews: log and dispositions

[Task](../../tasks/TASK-P01-011.md) · [Task board](../../tasks/README.md) · [G01 gate record](g01-gate-record.md)

**Received 2026-10-27, relayed by the user from Codex.** The relay stated: "This message is review feedback only, NOT confirmation of DEC-046 or G01. Keep G01 pending until the human explicitly answers." G01 stays pending. No-finding reviews are recorded as reviews, not as merge or gate approval.

Each row records the exact revision reviewed. "Inherited" means a finding carried forward from an earlier PR, not a new one.

| Delivery ID (PR:base:head) | Result as relayed | Disposition (TASK-P01-011) |
| --- | --- | --- |
| `pr12:4ce6b78f…:75334bf2…` | Standards 0, Spec 0. Both earlier P2s resolved | Recorded. No action |
| `pr13:4ce6b78f…:7587d927…` | Spec 2 P2: (1) SR-04 omits the §4.1 personal-backtesting category; (2) the map omits `OnChainEvent.observed_at`, `NativeMarketEvent.size_unit` and the `BookState` `venue`/`instrument` | (1) Resolved earlier by the [reassessment](source-reassessment.md) (TASK-P01-007), whose precedence covers the registry; the PR #19 relay confirms this. (2) **Fixed:** three rows added to the [observability map](observability-map.md#contract-fields) |
| `pr14:4ce6b78f…:1fbf301a…` | Standards 0, Spec 0 new; PR #13 findings inherited | Recorded. Inherited items as above |
| `pr14:4ce6b78f…:abcbbd93…` | Standards 0, Spec 0 new | Recorded |
| `pr15:4ce6b78f…:d71e8241…` | Spec 2 P2: (1) the H-02/H-03 nulls omit the H-01 logistic comparator; (2) H-OF3, H-OF8 and H-OF9 lack a G06 held-out stage | **Fixed** in the [research agenda](research-agenda.md): the nulls now include H-01; VAL-012 (G06) is added, conditional on data closure where needed |
| `pr16:4ce6b78f…:aed2dfbd…` | Spec 1 P2: T-4 bans all public-data advantage; the source bans it only for data delayed until after the move (27:84), and allows lag-safe horizons (27:67) | **Fixed:** T-4 in the [register](acceptance-objectives.md#2-time-latency-and-clock) is restricted to late-arriving observations, and the HFT prohibition is kept separate |
| `pr17:4ce6b78f…:14af0910…` | Spec 0 new; PR #16 finding inherited | Recorded. Inherited item as above |
| `pr18:6079c29c…:2947658b…` | Standards 0, Spec 0 new | Recorded |
| `pr19:d5a771ed…:5a6af702…` | Spec 1 P2: dataset terms §1.2 (supplemental to the Terms of Use), §1.4 (assent) and §1.5 (conflict priority) missed; §12 is not the only incorporation | **Fixed:** [correction](binance-general-terms.md#correction-2026-10-27-the-dataset-terms-own-incorporation-and-priority-clauses-f-5b) applies §1.2 to §1.5, which narrows F-5b′ to F-5b″. Binance retention is not restricted for DEC-030 use. Pointer corrections in the reassessment, registry, map, data-access decision, SA-01 and the gate record |
| `pr20:d5a771ed…:3003c2b2…` | Spec 0 new; the PR #19 P2 inherited in the copy and storage analysis | As PR #19 |
| `pr21:81773371…:0c9de2db…` | Standards 0, Spec 0 new; the PR #19 P2 inherited | As PR #19 |
| `pr22:81773371…:f5bbe477…` | Standards 0, Spec 0 new; the PR #19 P2 inherited. G01 remains pending confirmation | As PR #19. G01 pending |

**Effect on G01.** The PR #19 fix changes draft record SA-01, which DEC-046 asks the reviewer to confirm:
- **The accepted limitation shrinks** from F-5b′ to F-5b″, which only asks to confirm that the linked Terms of Use is BT-1 and whether UK Local Terms apply.
- **Retention is no longer ambiguous.**

The confirmation question should therefore be asked on the corrected records.
