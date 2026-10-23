import csv, importlib.util, os, sqlite3, tempfile, unittest
from argparse import Namespace
from pathlib import Path
spec=importlib.util.spec_from_file_location('core',Path(__file__).parents[1]/'runtime'/'core.py')
core=importlib.util.module_from_spec(spec); spec.loader.exec_module(core)
class TestCore(unittest.TestCase):
    def test_timezone_required(self):
        with self.assertRaises(ValueError): core.parse_ts('2025-01-01T00:00:00')
    def test_duplicate_conflict_and_idempotency(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'bars.csv'; db=str(Path(td)/'db.sqlite')
            def write(close):
                with open(path,'w',newline='') as f:
                    w=csv.writer(f);w.writerow(['timestamp','symbol','open','high','low','close','volume']);w.writerow(['2025-01-01T00:00:00Z','ABC',100,110,90,close,1000])
            write(105);core.ingest(Namespace(csv=str(path),db=db));core.ingest(Namespace(csv=str(path),db=db))
            with sqlite3.connect(db) as con: self.assertEqual(con.execute('select count(*) from bars').fetchone()[0],1)
            write(106)
            with self.assertRaises(ValueError):core.ingest(Namespace(csv=str(path),db=db))
    def test_invalid_ohlc(self):
        with tempfile.TemporaryDirectory() as td:
            path=Path(td)/'bad.csv';path.write_text('timestamp,symbol,open,high,low,close,volume\n2025-01-01T00:00:00Z,ABC,100,90,80,95,1000\n')
            with self.assertRaises(ValueError):core.ingest(Namespace(csv=str(path),db=str(Path(td)/'db.sqlite')))
if __name__=='__main__':unittest.main()
