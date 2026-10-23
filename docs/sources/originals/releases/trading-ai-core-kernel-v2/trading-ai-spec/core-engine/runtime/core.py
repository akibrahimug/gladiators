#!/usr/bin/env python3
"""Offline CLI vertical slice; not a production trading system."""
import argparse, csv, hashlib, json, math, sqlite3, sys
from datetime import datetime, timezone
from pathlib import Path

DDL='''CREATE TABLE IF NOT EXISTS bars (symbol TEXT NOT NULL, ts TEXT NOT NULL, open REAL NOT NULL, high REAL NOT NULL, low REAL NOT NULL, close REAL NOT NULL, volume REAL NOT NULL, PRIMARY KEY(symbol,ts));'''

def connect(path):
    Path(path).parent.mkdir(parents=True, exist_ok=True)
    db=sqlite3.connect(path); db.execute(DDL); return db

def parse_ts(s):
    d=datetime.fromisoformat(s.replace('Z','+00:00'))
    if d.tzinfo is None or d.utcoffset() is None: raise ValueError('timezone offset required')
    return d.astimezone(timezone.utc).isoformat()

def ingest(args):
    db=connect(args.db); count=0; seen=set(); records=[]
    with open(args.csv,newline='') as f:
        reader=csv.DictReader(f)
        needed={'timestamp','symbol','open','high','low','close','volume'}
        if not needed.issubset(reader.fieldnames or []): raise ValueError(f'missing CSV columns {needed-set(reader.fieldnames or [])}')
        for line,row in enumerate(reader,2):
            try:
                ts=parse_ts(row['timestamp']); symbol=row['symbol'].strip().upper()
                if not symbol: raise ValueError('empty symbol')
                o,h,l,c,v=[float(row[k]) for k in ('open','high','low','close','volume')]
                if not all(map(math.isfinite,(o,h,l,c,v))) or min(o,h,l,c)<=0 or v<0 or l>min(o,c) or h<max(o,c) or l>h: raise ValueError('invalid OHLCV')
                key=(symbol,ts)
                if key in seen: raise ValueError('duplicate bar in import')
                seen.add(key); records.append((symbol,ts,o,h,l,c,v))
            except Exception as exc: raise ValueError(f'CSV line {line}: {exc}') from exc
    # Reject conflicting duplicate timestamps; do not silently overwrite source history.
    with db:
        for record in records:
            old=db.execute('SELECT open,high,low,close,volume FROM bars WHERE symbol=? AND ts=?',record[:2]).fetchone()
            if old is not None and tuple(old)!=tuple(record[2:]): raise ValueError(f'conflicting existing bar {record[:2]}')
            if old is None:
                db.execute('INSERT INTO bars VALUES (?,?,?,?,?,?,?)',record); count+=1
    print(f'IMPORTED={count} TOTAL_IN_FILE={len(records)} DB={args.db}')

def load(db,symbol):
    with connect(db) as conn:
        rows=conn.execute('SELECT ts,open,high,low,close,volume FROM bars WHERE symbol=? ORDER BY ts',(symbol.upper(),)).fetchall()
    if not rows: raise ValueError('no bars for symbol')
    return rows

def inspect(args):
    rows=load(args.db,args.symbol)
    digest=hashlib.sha256(json.dumps(rows,separators=(',',':')).encode()).hexdigest()
    print(f'SYMBOL={args.symbol.upper()} BARS={len(rows)} FIRST={rows[0][0]} LAST={rows[-1][0]} SNAPSHOT_SHA256={digest}')

def features(rows):
    # Predict next bar direction using only completed current and prior bars.
    out=[]
    for i in range(21,len(rows)-1):
        close=rows[i][4]; prior=rows[i-1][4]
        r1=close/prior-1
        r5=close/rows[i-5][4]-1
        r20=close/rows[i-20][4]-1
        returns=[rows[j][4]/rows[j-1][4]-1 for j in range(i-19,i+1)]
        mean=sum(returns)/len(returns)
        vol=(sum((r-mean)**2 for r in returns)/len(returns))**0.5
        out.append((rows[i][0],[r1,r5,r20,vol],int(rows[i+1][4]>close),close,rows[i+1][4]))
    return out

def run(args):
    try:
        import numpy as np
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
        from sklearn.preprocessing import StandardScaler
    except ImportError as exc: raise RuntimeError('train/backtest requires numpy and scikit-learn: pip install numpy scikit-learn') from exc
    rows=load(args.db,args.symbol); data=features(rows)
    if len(data)<80: raise ValueError('need at least 102 chronological bars for a meaningful smoke test')
    n=len(data); train_end=int(n*.6); val_end=int(n*.8)
    x=np.array([r[1] for r in data]); y=np.array([r[2] for r in data]);
    if len(set(y[:train_end]))<2: raise ValueError('training period has only one class')
    model=make_pipeline(StandardScaler(),LogisticRegression(max_iter=1000,random_state=42))
    model.fit(x[:train_end],y[:train_end])
    p=model.predict_proba(x[val_end:])[:,1]; actual=y[val_end:]
    brier=float(np.mean((p-actual)**2)); base=float(np.mean((np.mean(y[:train_end])-actual)**2))
    print(f'SYMBOL={args.symbol.upper()} SAMPLES={n} TRAIN={train_end} VALIDATION={val_end-train_end} TEST={n-val_end}')
    print(f'TEST_BRIER={brier:.6f} BASELINE_BRIER={base:.6f} TEST_UP_RATE={float(np.mean(actual)):.4f}')
    if args.action=='train':
        print('MODEL=logistic_regression STATUS=research_only CALIBRATED=false'); return
    cash=500.0; qty=0; entry=0.; trades=0; wins=0; losses=0; total_fees=0.
    fee=args.fee; threshold=args.threshold
    # One-bar holding period; next-bar close used as a proxy fill, not realistic execution.
    for i,prob in enumerate(p):
        price=data[val_end+i][3]; exit_price=data[val_end+i][4]
        if prob<threshold: continue
        stop_distance=max(price*.01,price*float(data[val_end+i][1][3])*2)
        size=min(int((cash*.01)/stop_distance),int((cash-fee)/price))
        if size<=0: continue
        gross=size*(exit_price-price)
        net=gross-2*fee
        cash+=net; total_fees+=2*fee; trades+=1
        wins+=net>0; losses+=net<0
    print(f'BACKTEST_TRADES={trades} WINS={wins} LOSSES={losses} END_EQUITY_GBP={cash:.2f} NET_PNL_GBP={cash-500:.2f} FEES_GBP={total_fees:.2f}')
    print('WARNING=proxy_close_fills_no_spread_slippage_gaps_or_stop_execution; NOT_LIVE_READY')

def main():
    p=argparse.ArgumentParser(description='Offline quantitative core vertical slice (not live-ready)')
    p.add_argument('--db',default='data/market.sqlite3'); sub=p.add_subparsers(dest='action',required=True)
    i=sub.add_parser('ingest'); i.add_argument('--csv',required=True)
    s=sub.add_parser('inspect'); s.add_argument('--symbol',required=True)
    t=sub.add_parser('train'); t.add_argument('--symbol',required=True)
    b=sub.add_parser('backtest'); b.add_argument('--symbol',required=True); b.add_argument('--threshold',type=float,default=.55); b.add_argument('--fee',type=float,default=0.)
    args=p.parse_args()
    try:
        if args.action=='ingest': ingest(args)
        elif args.action=='inspect': inspect(args)
        else: run(args)
    except Exception as exc:
        print(f'ERROR={exc}',file=sys.stderr); return 1
    return 0

if __name__=='__main__': sys.exit(main())
