# Independent Codex PR reviews: log and dispositions

[Task](../../tasks/TASK-P01-011.md) · [Task board](../../tasks/README.md) · [G01 gate record](g01-gate-record.md)

**Received 2026-10-27, relayed by the user from Codex.** The relay stated: "This message is review feedback only, NOT confirmation of DEC-046 or G01. Keep G01 pending until the human explicitly answers." G01 stays pending. No-finding reviews are recorded as reviews, not as merge or gate approval.

Each row records the exact revision reviewed. "Inherited" means a finding carried forward from an earlier PR, not a new one.

| Delivery ID (PR:base:head) | Result as relayed | Disposition (TASK-P01-011) |
| --- | --- | --- |
| `pr12:4ce6b78fd0d39873740bb1a0ceb200523d9b5752:75334bf20f7e131741638f7a7ed93fe0e4412ee2` | Standards 0, Spec 0. Both earlier P2s resolved | Recorded. No action |
| `pr13:4ce6b78fd0d39873740bb1a0ceb200523d9b5752:7587d9277325d01f07c37f878394bbf9ed38500a` | Spec 2 P2: (1) SR-04 omits the §4.1 personal-backtesting category; (2) the map omits `OnChainEvent.observed_at`, `NativeMarketEvent.size_unit` and the `BookState` `venue`/`instrument` | (1) Resolved earlier by the [reassessment](source-reassessment.md) (TASK-P01-007), whose precedence covers the registry; the PR #19 relay confirms this. (2) **Fixed:** three rows added to the [observability map](observability-map.md#contract-fields) |
| `pr14:4ce6b78fd0d39873740bb1a0ceb200523d9b5752:1fbf301a0e715ea9846aa60dec6032ebe132df55` | Standards 0, Spec 0 new; PR #13 findings inherited | Recorded. Inherited items as above |
| `pr14:4ce6b78fd0d39873740bb1a0ceb200523d9b5752:abcbbd9343aed2c2ac9e2598298d18cf028cd8f9` | Standards 0, Spec 0 new | Recorded |
| `pr15:4ce6b78fd0d39873740bb1a0ceb200523d9b5752:d71e8241b5e6c3062df1371491436f9bd48bf6a5` | Spec 2 P2: (1) the H-02/H-03 nulls omit the H-01 logistic comparator; (2) H-OF3, H-OF8 and H-OF9 lack a G06 held-out stage | **Fixed** in the [research agenda](research-agenda.md): the nulls now include H-01; VAL-012 (G06) is added, conditional on data closure where needed |
| `pr16:4ce6b78fd0d39873740bb1a0ceb200523d9b5752:aed2dfbd24cb64582a6a040299054b53da3b6359` | Spec 1 P2: T-4 bans all public-data advantage; the source bans it only for data delayed until after the move (27:84), and allows lag-safe horizons (27:67) | **Fixed:** T-4 in the [register](acceptance-objectives.md#2-time-latency-and-clock) is restricted to late-arriving observations, and the HFT prohibition is kept separate |
| `pr17:4ce6b78fd0d39873740bb1a0ceb200523d9b5752:14af09102cd912360715d224a7159f205ccd4a53` | Spec 0 new; PR #16 finding inherited | Recorded. Inherited item as above |
| `pr18:6079c29c753d156e60d8e818a174883a966cfcd7:2947658b89fa24b86df497758591d91122f1acc7` | Standards 0, Spec 0 new | Recorded |
| `pr19:d5a771edaeec82aa04400fa5538d58ac4768e57a:5a6af702f1694d1f373c710d88a2354118daf51b` | Spec 1 P2: dataset terms §1.2 (supplemental to the Terms of Use), §1.4 (assent) and §1.5 (conflict priority) missed; §12 is not the only incorporation | **Fixed:** [correction](binance-general-terms.md#correction-2026-10-27-the-dataset-terms-own-incorporation-and-priority-clauses-f-5b) applies §1.2 to §1.5, which narrows F-5b′ to F-5b″. Binance retention is not restricted for DEC-030 use. Pointer corrections in the reassessment, registry, map, data-access decision, SA-01 and the gate record |
| `pr20:d5a771edaeec82aa04400fa5538d58ac4768e57a:3003c2b2a71ac7f0594b3ed2897f92adf449367b` | Spec 0 new; the PR #19 P2 inherited in the copy and storage analysis | As PR #19 |
| `pr21:81773371246b2f825c52277abfee0cde19b8cadc:0c9de2db6ba7882c095b2224df011936bd0c71fe` | Standards 0, Spec 0 new; the PR #19 P2 inherited | As PR #19 |
| `pr22:81773371246b2f825c52277abfee0cde19b8cadc:f5bbe4777779cf4368b850b152bb4ede6a977cf4` | Standards 0, Spec 0 new; the PR #19 P2 inherited. G01 remains pending confirmation | As PR #19. G01 pending |

**Effect on G01.** The PR #19 fix changes draft record SA-01, which DEC-046 asks the reviewer to confirm:
- **The accepted limitation shrinks** from F-5b′ to F-5b″, which only asks to confirm that the linked Terms of Use is BT-1 and whether UK Local Terms apply.
- **Retention is no longer ambiguous.**

The confirmation question should therefore be asked on the corrected records.
