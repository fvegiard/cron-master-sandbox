import json
import sys
from pathlib import Path
normal=json.loads(Path(sys.argv[1]).read_text()); negative=json.loads(Path(sys.argv[2]).read_text())
expected=json.loads(Path('eval/cases.json').read_text()); rows=normal['results']['results']; seen=[]
for row in rows:
    result=json.loads(row['response']['output']); case=row['testCase']['vars']['case_id']; seen.append(case)
    assert row['success'] is True and result['case_id']==case
    assert result['tests_run']==1 and result['skipped']==0 and result['errors']==0 and result['failures']==0
    assert result['authorized'] is False and result['scope']=='component-test'
assert len(rows)==len(expected) and set(seen)==set(expected)
bad=negative['results']['results']; assert len(bad)==1 and bad[0]['success'] is False
control=json.loads(bad[0]['response']['output'])
assert control['negative_control'] is True and control['failures']==1 and control['errors']==0
assert 'copy_failure_reported' in control['test_log']
print(json.dumps({'cases_passed':len(rows),'negative_control':'intended_classifier_mutation_rejected','scope':'component-evaluator-not-LLM-agent','production_certified':False}))
