import unittest
from unittest.mock import patch
import test_cron_master as fixtures
from test_cron_master import audit, inv, job, requirement
from cron_master import validate_inventory

class SwarmFreshnessTests(unittest.TestCase):
    def test_stale_job_inside_fresh_inventory_blocks_candidate(self):
        out=audit(inv(job(restart_count=99, observed_at='2026-10-01T12:00:00+00:00')))
        self.assertNotIn('OPTIMIZE_CANDIDATE', [p['action'] for p in out['proposals']])
    def test_future_job_inside_fresh_inventory_blocks_candidate(self):
        out=audit(inv(job(restart_count=99, observed_at='2026-10-03T12:00:00+00:00')))
        self.assertNotIn('OPTIMIZE_CANDIDATE', [p['action'] for p in out['proposals']])
    def test_naive_job_time_rejected(self):
        with self.assertRaises(ValueError): validate_inventory(inv(job(observed_at='2026-10-02T12:00:00')))
    def test_unknown_requested_scheduler_blocks_create(self):
        out=audit(inv(coverage={'systemd':'complete'}), requirement())
        self.assertNotIn('CREATE_CANDIDATE', [p['action'] for p in out['proposals']])
    def test_protection_tags_case_insensitive(self):
        j=fixtures.GovernanceTests().retirement(tags=['Remote-Access'])
        self.assertNotIn('DELETE_CANDIDATE',[p['action'] for p in audit(inv(j))['proposals']])
    def test_outcome_assertion_not_promoted_to_verified(self):
        result=audit(inv(job(outcome_verified=True)))['results'][0]
        self.assertEqual(result['business_outcome'],'claimed_verified_by_input_not_attested')

class SwarmLedgerTests(unittest.TestCase):
    setUp = fixtures.MemoryTests.setUp
    tearDown = fixtures.MemoryTests.tearDown
    def test_return_record_not_later_writers_latest(self):
        with patch.object(self.ledger, 'latest', wraps=self.ledger.latest) as wrapped:
            record=self.ledger.record_session(self.session,None)
            self.assertEqual(wrapped.call_count,1)
            self.assertEqual(record['data'],self.session)
