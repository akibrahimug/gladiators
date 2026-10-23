import importlib.util
from pathlib import Path
import tempfile
import unittest

script=Path(__file__).resolve().parents[1]/'spec_audit.py'
spec=importlib.util.spec_from_file_location('spec_audit',script)
module=importlib.util.module_from_spec(spec);spec.loader.exec_module(module)

class SpecAuditTests(unittest.TestCase):
 def test_current_documentation_passes(self):
  passed,errors=module.audit()
  self.assertGreater(passed,50)
  self.assertEqual(errors,[])
 def test_missing_component_fails_closed(self):
  with tempfile.TemporaryDirectory() as d:
   passed,errors=module.audit(Path(d))
   self.assertEqual(passed,0)
   self.assertTrue(any(x.startswith('MISSING') for x in errors))
 def test_missing_requirement_detected(self):
  with tempfile.TemporaryDirectory() as d:
   root=Path(d); p=root/'core-engine'/'components';p.mkdir(parents=True)
   for name in module.REQUIRED:
    (p/name).write_text('Status: design specification\n')
   _,errors=module.audit(root)
   self.assertTrue(any(x.startswith('ABSENT') for x in errors))

if __name__=='__main__':unittest.main()
