"""Reproducible property checks; Hypothesis is required, never silently skipped."""
import copy
import json
import unittest
from hypothesis import given, settings, strategies as st
import test_cron_master as base
from cron_master import result_class, validate_inventory

RUN = settings(max_examples=300, deadline=None, derandomize=True, database=None)

class PropertyTests(unittest.TestCase):
    @RUN
    @given(st.integers(min_value=-(2**31),max_value=2**31-1))
    def test_signed_unsigned_status_agree(self,code):
        self.assertEqual(result_class(base.job(last_result=code)),result_class(base.job(last_result=code & 0xffffffff)))
    @RUN
    @given(st.one_of(st.none(),st.floats(min_value=0,max_value=1e12,allow_nan=False,allow_infinity=False)))
    def test_optional_numbers_never_crash_or_authorize(self,value):
        j=base.job(restart_count=value,timeout_seconds=value,disabled_days=value,interval_seconds=value,runtime_p95_seconds=value)
        out=base.audit(base.inv(j)); json.dumps(out,allow_nan=False)
        self.assertTrue(all(p['authorized'] is False for p in out['proposals']))
    @RUN
    @given(st.text(max_size=120))
    def test_notes_never_change_authority(self,text):
        self.assertTrue(all(p['authorized'] is False for p in base.audit(base.inv(base.job(notes=text)))['proposals']))
    @RUN
    @given(st.integers(min_value=0,max_value=7))
    def test_robocopy_no_failure_is_not_outcome_verification(self,code):
        out=base.audit(base.inv(base.job(result_semantics='robocopy',last_result=code)))
        self.assertEqual(out['results'][0]['business_outcome'],'unverified')
    @RUN
    @given(st.lists(st.sampled_from(['remote-access','backup','security','business-sync','system','active-work','openhands']),min_size=1,max_size=6))
    def test_protected_retirement_never_deleted(self,tags):
        j=base.GovernanceTests().retirement(tags=[' '+x.upper()+' ' for x in tags])
        self.assertNotIn('DELETE_CANDIDATE',base.actions(j))
    @RUN
    @given(st.text(min_size=1,max_size=32).filter(lambda x: bool(x.strip())))
    def test_revision_is_preserved_in_every_proposal(self,revision):
        j=base.job(revision=revision,restart_count=99); initial=copy.deepcopy(j)
        out=base.audit(base.inv(j))
        self.assertEqual(j,initial)
        self.assertTrue(all(p['expected_revision']==revision for p in out['proposals']))
