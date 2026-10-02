'use strict';
const assert = require('node:assert/strict');
const grade = require('./assert-component.cjs');
const good = {case_id:'fixture',passed:true,tests_run:1,skipped:0,failures:0,errors:0,expected_failures:0,unexpected_successes:0,scope:'component-test',scheduler_changes:0,authorized:false,test_log:'synthetic check'};
const context = {vars:{case_id:'fixture'}};
assert.equal(grade(JSON.stringify(good),context).pass,true);
let controls=0;
for (const changes of [{expected_failures:1},{unexpected_successes:1},{skipped:1},{errors:1},{failures:1},{case_id:'wrong-case'},{scope:'target'},{authorized:true},{scheduler_changes:1},{passed:false},{tests_run:0}]) {
  assert.equal(grade(JSON.stringify({...good,...changes}),context).pass,false);
  controls++;
}
assert.equal(grade('not json',context).pass,false);
assert.equal(grade(JSON.stringify(good),{vars:{case_id:'other'}}).pass,false);
console.log(JSON.stringify({positive_cases:1,negative_cases:controls+2,scope:'deterministic-grader-unit-tests'}));
