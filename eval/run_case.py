"""A fixed-test adapter for Promptfoo, not an AI agent or scheduler executor."""
import io, json, sys, unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
allowed=json.loads((ROOT/'eval'/'cases.json').read_text())
if len(sys.argv) not in (2,3) or sys.argv[1] not in allowed:
    raise SystemExit('Unknown fixed test ID')
mutant=len(sys.argv)==3
if mutant:
    if sys.argv[2]!='--negative-control': raise SystemExit('Unknown flag')
    import cron_master
    original=cron_master.result_class
    def deliberately_bad_classifier(job):
        if job.get('result_semantics')=='robocopy' and job.get('last_result')==3:
            return 'copy_failure_reported'
        return original(job)
    cron_master.result_class=deliberately_bad_classifier
suite=unittest.defaultTestLoader.loadTestsFromName(allowed[sys.argv[1]])
stream=io.StringIO()
result=unittest.TextTestRunner(stream=stream, verbosity=2).run(suite)
print(json.dumps({'case_id':sys.argv[1], 'passed':result.wasSuccessful() and not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses and result.testsRun==1,
                  'tests_run':result.testsRun, 'skipped':len(result.skipped), 'failures':len(result.failures),
                  'errors':len(result.errors), 'expected_failures':len(result.expectedFailures), 'unexpected_successes':len(result.unexpectedSuccesses), 'scope':'component-test', 'negative_control':mutant,
                  'scheduler_changes':0, 'authorized':False, 'test_log':stream.getvalue()}))
