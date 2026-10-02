"""Run real unittest/Hypothesis cases and write machine-readable receipts."""
import hashlib
import json
import os
import platform
import sys
import unittest
from pathlib import Path
from datetime import datetime, timezone
ROOT=Path(__file__).resolve().parents[1]
sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
report=Path(os.environ.get('REPORT_DIR',str(ROOT/'reports'))); report.mkdir(parents=True,exist_ok=True)
suite=unittest.defaultTestLoader.discover(str(ROOT/'tests'))
result=unittest.TextTestRunner(verbosity=2).run(suite)
receipt={'scope':'synthetic-component-and-recovery-tests','passed':result.wasSuccessful() and not result.skipped and not result.expectedFailures and not result.unexpectedSuccesses,'tests_run':result.testsRun,'failures':len(result.failures),'errors':len(result.errors),'skipped':len(result.skipped),'expected_failures':len(result.expectedFailures),'unexpected_successes':len(result.unexpectedSuccesses),'failure_names':[str(t) for t,_ in result.failures],'error_names':[str(t) for t,_ in result.errors],'python':platform.python_version(),'platform':platform.platform(),'utc':datetime.now(timezone.utc).isoformat(),'source_sha256':hashlib.sha256((ROOT/'cron_master.py').read_bytes()).hexdigest(),'production_certified':False}
(report/'tests.json').write_text(json.dumps(receipt,indent=2),encoding='utf-8')
print(json.dumps(receipt))
raise SystemExit(0 if receipt['passed'] else 1)
