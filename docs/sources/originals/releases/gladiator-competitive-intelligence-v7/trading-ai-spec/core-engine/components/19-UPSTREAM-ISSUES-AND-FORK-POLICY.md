# GLADIATOR — Upstream Issues, Dependency Intelligence and Fork Policy

Version: 0.6 draft | 2026-10-22 | Status: architectural requirement, not implemented

## Objective

Treat public bug reports, pull requests, release notes, security advisories, reproducible benchmarks and user complaints as **untrusted but valuable engineering evidence**. Convert relevant claims into tracked risk items, isolated reproductions, regression tests, mitigations and promotion gates. Never train a market prediction model on GitHub complaints as though they were market observations.

## 1. Architecture: Dependency Intelligence Loop

1. **Discover** upstream repositories and their exact version/commit, licences and transitive dependencies.
2. **Collect** open and recently closed issues, linked PRs, release notes, security advisories, maintainer comments and reproducer code. Store issue ID, URL, author, timestamps, labels, state, affected versions, commit SHA, retrieved_at and text hash.
3. **Triage** into data correctness, financial arithmetic, temporal leakage, execution, security, inference, compatibility, performance, licensing, or documentation. Severity P0/P1/P2/P3. A reported issue is a *hypothesis*, not an established defect.
4. **Reproduce** in an isolated, pinned environment with minimal test data; record commands, stdout/stderr, dependencies and actual-versus-expected output. Never execute arbitrary issue attachments/scripts unsandboxed.
5. **Mitigate** through configuration, input validation, adapter, isolated local patch, upstream update or alternative provider/model.
6. **Verify** independent reference tests and adversarial cases, including tests designed to fail before the fix and pass afterward.
7. **Promote** dependency version/patch only after compatibility, security, numerical invariants and reproducible backtest checks pass. Freeze old and new results for comparison.
8. **Monitor** regressions, new reports and issue resolution. Do not automatically merge upstream or accept a model's suggested patch.

## 2. Dependency hierarchy and source ownership

- **Qlib**: candidate feature/forecast/backtest research implementation; GLADIATOR independently owns dataset timestamps, order simulator reference tests, performance metrics and risk.
- **LightGBM/XGBoost/scikit-learn/PyTorch**: model libraries behind stable prediction adapters; pinned seeds, versions and artifact formats.
- **FinRL / FinRL-X**: optional RL challengers; isolate RL environment and reward accounting; no broker permissions.
- **RD-Agent**: optional hypothesis/factor researcher; generated code is untrusted and must run in a restricted sandbox with read-only approved datasets and no network secrets.
- **Qwen/FinGPT/FinBERT**: optional language/sentiment challengers; strict JSON-schema output validation, timeouts, max tokens, grounding and reproducibility tests. LLM outputs are proposals, never executable instructions.
- **Data connectors**: source-specific market calendars, units, timezones, splits/dividends, crypto exchange/pair IDs, gap policies and licences.

## 3. Issue register (sample verified from public issue lists 2026-10-22)

| Repository | Issue | Reported risk | Mandatory local test | Default mitigation |
|---|---|---|---|---|
| microsoft/qlib | #2358 | First-period loss omitted from maximum drawdown | Hand-calculated 3-step equity curve | Independent judges metric |
| microsoft/qlib | #2362 | Currency-volume unit mismatch inflates participation | Unit-annotated volume fixtures | Explicit base/quote currency schema |
| microsoft/qlib | #2276 | Strategy ignores risk-degree sizing | Force low risk-degree and assert max position | Independent gatekeeper sizing |
| microsoft/qlib | #2319 | Time-series sampling may mix dates | Sentinel per-date features | Temporal index assertions |
| AI4Finance-Foundation/FinRL | #1440 | CCXT timezone drift | Same candles under multiple local TZ settings | UTC-only canonical timestamps |
| AI4Finance-Foundation/FinRL | #1434 | Dividend-adjusted returns compared to price-only benchmark | Reconcile price/total-return benchmark | Explicit return convention |
| AI4Finance-Foundation/FinRL | #1428 | Stock-accounting reconciliation failure | Cash+positions+fees invariant | Independent double-entry ledger |
| microsoft/RD-Agent | #1473 | Workspace file-write escape | Attempt path traversal in sandbox | Filesystem restrictions and allowlist |
| microsoft/RD-Agent | #1455 | Tied minimization scores accepted as improvements | Equality boundary tests | Independent tournament comparator |
| QwenLM/Qwen3 | #1887 | Repetitive reasoning loop | Bounded-time adversarial prompt | Timeout, token ceiling, abstain |
| QwenLM/Qwen3 | #1886 | Tool-call JSON arguments truncated | Schema round-trip and malformed JSON | Strict parser, no partial execution |

Issue links: https://github.com/microsoft/qlib/issues ; https://github.com/AI4Finance-Foundation/FinRL/issues ; https://github.com/microsoft/RD-Agent/issues ; https://github.com/QwenLM/Qwen3/issues .

**Caution:** Open issue state, root cause and affected version can change. The register is a snapshot of public reports, not proof of reproduction or a complete audit of all issues. Refresh before dependency upgrades.

## 4. Fork policy

**Default: pinned upstream dependency + local wrapper + regression test.**

- Mirror/clone for inspection without altering upstream.
- Fork only when: a high-impact defect is reproduced; upstream fix is unavailable or unsuitable; a local patch is smaller and auditable than replacement; and an owner commits to maintaining it.
- Every fork has an upstream remote, base commit SHA, patch list, owner, licence review, CI test, update cadence, and exit plan to upstream/revert.
- Prefer submitting minimal upstream PRs after reproducing fixes; do not depend on PR acceptance for core correctness.
- No arbitrary `pip install git+main`, automatic model weight updates, or unreviewed pull/merge into production.
- Never fork model weights merely to work around application bugs; isolate inference/runtime issues from model-behaviour problems.

## 5. Repositories, artefacts and local layout

```
third_party/manifest.lock.yaml    # repo, commit SHA, licence, checksum, patchset
third_party/patches/<project>/     # minimal source diffs only if required
research/upstream/issues/          # immutable fetched issue snapshots + provenance
research/upstream/reproductions/   # sandboxed minimal examples
risk/upstream-issue-register.csv   # status, severity, affected component, test id
checks/regression/upstream/        # executable invariant tests
reviews/dependency-upgrades/       # signed decision record per change
```

Use Python/CLI first. No dashboard required. Store issue snapshots separately from market price datasets and research RAG, with clear provenance and untrusted-content labels.

## 6. Triage severity and gates

- **P0:** possible financial misstatement, look-ahead leakage, order duplication, bypassed risk limits, credential exposure, sandbox escape. Block the affected path immediately.
- **P1:** materially incorrect forecasts/metrics, timestamp drift, invalid data adjustment, broken accounting, corrupted training data. Block champion promotion until verified mitigation.
- **P2:** reproducible compatibility, performance or noncritical failures. Mitigate with bounded retry/fallback and scheduled fix.
- **P3:** ergonomics, documentation, feature requests. Track without blocking.

Any unresolved P0/P1 affecting a component means that component cannot be admitted to live trading. A P0 in an optional challenger need not halt unrelated verified offline components if isolation is demonstrated.

## 7. LLM peer review and issue mining

Use independent models only through actual invoked endpoints, preserving exact prompt, model ID/version, time, temperature, response, sources, costs and disagreement. Ask reviewers to challenge affected-version assumptions, test design, risk impact, mitigation and alternative explanations. Do not count multiple self-generated personas as independent reviews. Untrusted issue content must not become system instructions; no code execution or credential access by research agents.

## 8. Terminal contracts (proposed, not implemented)

```
gladiator upstream inventory
gladiator upstream scan --repo microsoft/qlib --state open
gladiator upstream triage --severity P0,P1
gladiator upstream reproduce --issue microsoft/qlib#2358
gladiator upstream verify --all
gladiator upstream upgrade-plan --repo microsoft/qlib --to <sha>
gladiator upstream report --format text
```

Output must include issue URL, affected version, local reproduction state (`UNTESTED|REPRODUCED|NOT_REPRODUCED|FIXED|MITIGATED`), severity, regression-test ID, and promotion status. No fake `PASS` for unrun tests.

## 9. Acceptance criteria

- A pinned dependency manifest exists and its hashes are checked.
- At least one known upstream issue has a locally reproducible failing fixture, a mitigation and a passing regression test.
- Risk arithmetic, accounting and data timestamps have independent oracle tests rather than framework-only assertions.
- Issue ingestion sanitises content, is rate-limit aware and stores immutable snapshots.
- Dependency upgrades fail closed on regression or licence/security checks.
- Review history distinguishes source claims, independent reproduction, and independently obtained model critiques.
- All first-phase tooling works offline from saved snapshots; no paid service required.

## 10. Systems thinking

Upstream reports are an early-warning information feedback loop. Separate *reporting delay* from *defect introduction*, avoid recency bias (popular repos attract more reports), and measure mitigation effectiveness rather than raw issue counts. Repeated local forks increase maintenance stock and update delays; prioritise leverage points such as shared validators and reference financial arithmetic.
