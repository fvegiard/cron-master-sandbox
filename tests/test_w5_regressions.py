import hashlib
import json
import tempfile
import unittest
from pathlib import Path
import test_cron_master as base
from cron_master import Ledger

class W5RegressionTests(unittest.TestCase):
    def test_null_retry_count_does_not_crash(self):
        out = base.audit(base.inv(base.job(restart_count=None)))
        self.assertFalse(any('Retry count exceeds' in p['reason'] for p in out['proposals']))
    def test_null_quarantine_does_not_allow_delete(self):
        job = base.GovernanceTests().retirement()
        job['disabled_days'] = None
        self.assertNotIn('DELETE_CANDIDATE', base.actions(job))
    def test_invalid_checkpoint_preserves_previous_head(self):
        with tempfile.TemporaryDirectory() as td:
            ledger = Ledger(Path(td) / 'state.sqlite')
            try:
                data = {'target':'TEST','coverage':{'windows':'partial'},'open_items':[], 'next_action':'inspect','research_receipts':[]}
                first = ledger.record_session(data, None)
                for field in data:
                    with self.subTest(field=field):
                        bad = dict(data); bad[field] = None
                        with self.assertRaises(ValueError): ledger.record_session(bad, first['id'])
                        self.assertEqual(ledger.latest()['id'], first['id'])
            finally: ledger.close()
    def test_wrong_target_receipt_rejected(self):
        self.check_target_receipt('OTHER', 'TEST', False)
    def test_target_receipt_requires_declared_target(self):
        self.check_target_receipt('TEST', None, False)
    def test_matching_target_receipt_keeps_unattested_status(self):
        self.check_target_receipt('TEST', 'TEST', True)
    def check_target_receipt(self, observed, declared, accept):
        with tempfile.TemporaryDirectory() as td:
            root = Path(td); ledger = Ledger(root / 'state.sqlite')
            payload = json.dumps({'scope':'target','passed':True,'target_id':observed}).encode()
            (root / 'receipt.json').write_bytes(payload)
            receipt = {'path':'receipt.json','scope':'target','sha256':hashlib.sha256(payload).hexdigest()}
            item = {'claim':'fixture only','scope':'Cronie; TEST fixture','source_url':'https://github.com/cronie-crond/cronie','source_kind':'repository','status':'target_verified','test_receipts':[receipt]}
            if declared is not None: item['target_id'] = declared
            try:
                if accept:
                    result = ledger.record_lesson(item, root)
                    self.assertEqual(result['target_id'], declared)
                    self.assertEqual(result['authenticity'], 'not_attested')
                else:
                    with self.assertRaises(ValueError): ledger.record_lesson(item, root)
                    self.assertEqual(ledger.db.execute('SELECT COUNT(*) FROM lessons').fetchone()[0], 0)
            finally: ledger.close()
