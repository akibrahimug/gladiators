"""Apply live_records.normalize() to the 1-hour capture; report flags, snapshots and checksum recomputation."""
import collections, sys
from decimal import Decimal
from pathlib import Path
sys.path.insert(0, sys.argv[1])
from gladiator_capture import live_records as LR, live as L
from gladiator_capture.rawstore import sha256_file
d = Path(sys.argv[2])
offs = LR.offsets_from_events(d / "events.jsonl")
recs = LR.normalize(LR.read_segment(d / "frames.jsonl"), offs, raw_id=sha256_file(d / "frames.jsonl"), ingested_at=0)
flags = collections.Counter(f for r in recs for f in r.quality_flags)
types = collections.Counter((r.feed_id, r.fields["message_type"]) for r in recs)
unc = sum(r.fields["timestamp_uncertainty_ms"] is not None for r in recs)
expo = sum(1 for r in recs for v in ([r.fields.get("price"), r.fields.get("qty")] + [x for lv in r.fields.get("bids", []) + r.fields.get("asks", []) for x in lv]) if v and ("e" in v.lower()))
books = {s: L.Book(s, *p) for s, p in {"BTC/USD": (1, 8), "ETH/USD": (2, 8)}.items()}
ok = bad = 0
for r in recs:
    if r.feed_id != "kraken:ws2:book":
        continue
    b = books[r.native_symbol]
    if r.fields["message_type"] == "snapshot":
        b.bids, b.asks = {}, {}
    b.apply([{"price": p, "qty": q} for p, q in r.fields["bids"]], b.bids)
    b.apply([{"price": p, "qty": q} for p, q in r.fields["asks"]], b.asks)
    if r.fields["message_type"] == "update":
        b.truncate()
    if b.checksum() == int(r.fields["checksum"]): ok += 1
    else: bad += 1
print({"records": len(recs), "with_T5_uncertainty": unc, "share": round(unc / len(recs), 4), "flags": dict(flags),
       "by_type": {f"{a}/{b}": n for (a, b), n in types.items()}, "values_with_exponent": expo,
       "checksum_from_stored_strings": {"ok": ok, "fail": bad}})
