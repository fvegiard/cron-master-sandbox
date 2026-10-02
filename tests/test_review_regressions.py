"""Synthetic regressions from ten independent source reviews; no live scheduler access."""
import hashlib
import json
import sqlite3
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path
from unittest import mock
import test_cron_master as base
from cron_master import Ledger, load_json, research_plan, result_class, validate_inventory
ROOT = Path(__file__).resolve().parents[1]

class ReviewedInputTests(unittest.TestCase):
    def test_large_integer_is_not_float_overflow(self):
        value = base.inv(base.job(restart_count=10**400))
        self.assertIs(validate_inventory(value), value)
    def test_nonobject_research_checkpoint_rejected(self):
        for value in (None, [], 1, 'text', False):
            with self.subTest(value=value), self.assertRaises(ValueError):
                research_plan(value)
    def test_nested_json_is_structured_validation_failure(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'nested.json'; p.write_text('['*10000+'0'+']'*10000)
            with self.assertRaises(ValueError): load_json(p)
    def test_application_namespace_not_scheduler_status(self):
        self.assertEqual(result_class(base.job(result_semantics='robocopy', result_namespace='application_exit', last_result=0x41301)), 'copy_failure_reported')
    def test_unknown_namespace_collision_requires_review(self):
        j=base.job(result_semantics='robocopy', last_result=0x41301)
        self.assertEqual(result_class(j), 'ambiguous_status_namespace')
        self.assertIn('INVESTIGATE', base.actions(j))
    def test_explicit_scheduler_namespace_preserved(self):
        self.assertEqual(result_class(base.job(result_semantics='robocopy', result_namespace='scheduler_status', last_result=0x41301)), 'running_status')
    def test_contradictory_enabled_state_requires_review(self):
        self.assertIn('INVESTIGATE', base.actions(base.job(enabled=True,last_result=0x41302)))
    def test_invalid_namespace_rejected(self):
        with self.assertRaises(ValueError): validate_inventory(base.inv(base.job(result_namespace='assumed')))

class ReadOnlyLedgerTests(unittest.TestCase):
    def test_read_missing_database_does_not_create_directory(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'missing'/'state.sqlite'
            with self.assertRaises(FileNotFoundError): Ledger(p,read_only=True)
            self.assertFalse(p.parent.exists())
    def test_read_existing_database_cannot_write(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'state.sqlite'; writer=Ledger(p)
            data={'target':'TEST','coverage':{'windows':'partial'},'open_items':[],'next_action':'inspect','research_receipts':[]}
            record=writer.record_session(data,None); writer.close()
            reader=Ledger(p,read_only=True)
            try:
                self.assertEqual(reader.latest()['id'],record['id'])
                with self.assertRaises(sqlite3.OperationalError): reader.record_session(data,record['id'])
                self.assertEqual(reader.latest()['id'],record['id'])
            finally: reader.close()
class BoundLessonTests(unittest.TestCase):
    def check_binding(self, scope, claim_hash, accepted):
        with tempfile.TemporaryDirectory() as td:
            root=Path(td); ledger=Ledger(root/'state.sqlite')
            payload=json.dumps({'scope':'sandbox','passed':True,'lesson_scope':scope,'claim_sha256':claim_hash}).encode()
            (root/'receipt.json').write_bytes(payload)
            item={'claim':'synthetic claim','scope':'product-v1','source_url':'https://docs.python.org/3/','source_kind':'official','status':'sandbox_verified','test_receipts':[{'path':'receipt.json','scope':'sandbox','sha256':hashlib.sha256(payload).hexdigest()}]}
            try:
                if accepted:
                    self.assertEqual(ledger.record_lesson(item,root)['authenticity'],'not_attested')
                else:
                    with self.assertRaises(ValueError): ledger.record_lesson(item,root)
                    self.assertEqual(ledger.db.execute('SELECT COUNT(*) FROM lessons').fetchone()[0],0)
            finally: ledger.close()
    def test_matching_claim_scope_accepts_only_unattested_record(self):
        self.check_binding('product-v1',hashlib.sha256(b'synthetic claim').hexdigest(),True)
    def test_other_version_receipt_cannot_promote(self):
        self.check_binding('product-v2',hashlib.sha256(b'synthetic claim').hexdigest(),False)
    def test_other_claim_receipt_cannot_promote(self):
        self.check_binding('product-v1',hashlib.sha256(b'another claim').hexdigest(),False)
    def test_unbound_receipt_cannot_promote(self):
        self.check_binding(None,None,False)

class ReviewedCLITests(unittest.TestCase):
    def cli(self,*args):
        return subprocess.run([sys.executable,str(ROOT/'cron_master.py'),*map(str,args)],capture_output=True,text=True,timeout=15)
    def assert_structured_error(self,result):
        self.assertEqual(result.returncode,2,result.stderr)
        self.assertIn('error',json.loads(result.stderr)); self.assertNotIn('Traceback',result.stderr)
    def test_missing_read_only_ledger_reports_error_without_creation(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'missing'/'state.sqlite'
            self.assert_structured_error(self.cli('session-show','--db',p))
            self.assertFalse(p.parent.exists())
    def test_research_null_is_structured_error(self):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'null.json'; p.write_text('null')
            self.assert_structured_error(self.cli('research-plan',p))
    def test_datetime_range_overflow_is_structured_error(self):
        self.assert_structured_error(self.cli('time-check','9999-12-31T23:30:00','--zone','Etc/GMT+1'))
    def test_expected_failure_is_not_a_passing_evaluation(self):
        program = '\n'.join([
            'import sys, runpy, unittest',
            'from pathlib import Path',
            'root=Path(sys.argv[1])',
            'sys.path[:0]=[str(root),str(root/"tests")]',
            'import test_cron_master as t',
            'def deliberately_failing(self): self.fail("synthetic expected failure")',
            't.StatusTests.test_robocopy_three_is_not_failure=unittest.expectedFailure(deliberately_failing)',
            'sys.argv=[str(root/"eval/run_case.py"),"test_cron_master.StatusTests.test_robocopy_three_is_not_failure"]',
            'runpy.run_path(sys.argv[0],run_name="__main__")'])
        result=subprocess.run([sys.executable,'-c',program,str(ROOT)],capture_output=True,text=True,timeout=15)
        self.assertEqual(result.returncode,0,result.stderr)
        data=json.loads(result.stdout)
        self.assertIs(data['passed'],False); self.assertEqual(data['expected_failures'],1)
        self.assertEqual(data['tests_run'],1); self.assertEqual(data['errors'],0)

class JSONDepthContractTests(unittest.TestCase):
    def test_exact_depth_limit_is_accepted(self):
        from cron_master import parse_json_bytes, MAX_JSON_DEPTH
        raw=('['*MAX_JSON_DEPTH+'0'+']'*MAX_JSON_DEPTH).encode()
        self.assertEqual(len(parse_json_bytes(raw)),1)
    def test_exceeding_depth_limit_is_rejected(self):
        from cron_master import parse_json_bytes, MAX_JSON_DEPTH
        raw=('['*(MAX_JSON_DEPTH+1)+'0'+']'*(MAX_JSON_DEPTH+1)).encode()
        with self.assertRaises(ValueError): parse_json_bytes(raw)
    def test_brackets_and_escaped_quotes_in_strings_are_not_depth(self):
        from cron_master import parse_json_bytes
        expected={'text':'['*2000+'}'*2000+chr(92)+'"[]'}
        self.assertEqual(parse_json_bytes(json.dumps(expected).encode()),expected)
