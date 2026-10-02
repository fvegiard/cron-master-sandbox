"""Build the exact unittest case allowlist for Promptfoo; no scheduler calls."""
import json
import sys
import unittest
from pathlib import Path
ROOT=Path(__file__).resolve().parents[1]; sys.path[:0]=[str(ROOT),str(ROOT/'tests')]
def flatten(suite):
    for item in suite:
        if isinstance(item,unittest.TestSuite): yield from flatten(item)
        else: yield item.id()
names=sorted(set(flatten(unittest.defaultTestLoader.discover(str(ROOT/'tests')))))
(ROOT/'eval/cases.json').write_text(json.dumps({name:name for name in names},indent=2),encoding='utf-8')
p=ROOT/'eval/promptfooconfig.json'; cfg=json.loads(p.read_text(encoding='utf-8-sig'))
cfg['tests']=[{'description':name,'vars':{'case_id':name}} for name in names]
p.write_text(json.dumps(cfg,indent=2),encoding='utf-8')
print(json.dumps({'registered_cases':len(names)}))
