#!/usr/bin/env python3
"""Offline documentation contract audit; does NOT validate trading performance."""
from pathlib import Path
import hashlib
import re
import sys

ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / 'core-engine' / 'components'
REQUIRED = {
 '01-CORE-KERNEL.md': ['ABSTAIN','forecast','utility','stressed'],
 '02-ARENA.md': ['holdout','replay','paper','sealed'],
 '03-JUDGES.md': ['drawdown','calibration','confidence','reference'],
 '04-MANAGEMENT.md': ['rollback','budget','review'],
 '05-GATEKEEPER.md': ['kill switch','stale','cash','crypto'],
 '06-GLADIATORS.md': ['Qlib','FinRL','predict'],
 '07-CODE-OF-CONDUCT.md': ['risk','gatekeeper'],
 '08-TRANSPORTERS.md': ['idempot','replay','event'],
 '09-CONNECTORS.md': ['provider','licence','coverage'],
 '10-DATA.md': ['Parquet','available_at','checksum','Kraken','Binance'],
 '11-QLIB-AND-TRAINING.md': ['Qlib','chronological','artifact'],
 '12-RAG-MEMORY.md': ['research','time','retriev'],
 '13-EXECUTION-AND-LEDGER.md': ['fee','partial','ledger','same-bar'],
 '14-COSTS-AND-OPERATIONS.md': ['cost','phase','cloud'],
 '15-CLI-AND-ACCEPTANCE.md': ['terminal','gatekeeper','acceptance'],
 '16-SYSTEMS-THINKING.md': ['feedback','delay','loop'],
 '18-ADVERSARIAL-REVIEW-2026-10-22.md': ['external','OPEN','gate'],
}

def audit(root=ROOT):
    docs=root/'core-engine'/'components'; failures=[]; passed=0
    for name,terms in REQUIRED.items():
        p=docs/name
        if not p.exists(): failures.append(f'MISSING {name}');continue
        content=p.read_text(encoding='utf-8')
        for term in terms:
            if term.lower() not in content.lower():failures.append(f'ABSENT {name}: {term}')
            else: passed+=1
        if 'Status:' not in content and name != '18-ADVERSARIAL-REVIEW-2026-10-22.md':
            failures.append(f'NO_STATUS {name}')
    for p in docs.glob('*.md'):
        for target in re.findall(r'\[[^]]+\]\(([^)]+\.md)\)',p.read_text(encoding='utf-8')):
            if not (p.parent/target).exists():failures.append(f'BROKEN_LINK {p.name} -> {target}')
    return passed,failures

def main():
    passed, failures=audit()
    print('GLADIATOR SPEC AUDIT')
    print('MODE: DOCUMENTATION ONLY')
    print(f'COMPONENTS_CHECKED: {len(REQUIRED)}')
    print(f'CONTRACT_TERMS_PASSED: {passed}')
    print(f'FAILURES: {len(failures)}')
    for f in failures: print('FAIL:',f)
    print('TRADING_ENGINE_VALIDATED: NO')
    print('EXTERNAL_AI_PEER_REVIEW: NOT PERFORMED')
    print('LIVE_TRADING_APPROVED: NO')
    return 1 if failures else 0

if __name__=='__main__':sys.exit(main())
