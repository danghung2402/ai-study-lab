'use strict';
const assert = require('node:assert/strict');
const core = require('../static/assets/brief-core.js');
const scenarios = require('../content/scenarios.json');
let checks = 0;
function test(name, run) { run(); checks++; console.log(`PASS ${name}`); }
test('empty and whitespace fields cannot produce a brief', () => {
  const empty = Object.fromEntries(core.fields.map(field => [field.key, ' \n\t ']));
  assert.equal(core.inspect(empty).filled, 0);
  assert.equal(core.inspect(empty).missing.length, 6);
  assert.throws(() => core.format(empty));
});
test('all scenarios generate six labeled sections with their real sources', () => {
  for (const scenario of scenarios) {
    assert.equal(core.inspect(scenario.fields).valid, true);
    const brief = core.format(scenario.fields);
    for (const field of core.fields) assert.ok(brief.includes(`【${field.label}】`));
    assert.ok(brief.includes(scenario.fields.sources));
    assert.ok(brief.includes('已驗證、未驗證與待確認'));
  }
});
test('missing source is identified precisely and blocks generation', () => {
  const fields = { ...scenarios[0].fields, sources: '' };
  assert.deepEqual(core.inspect(fields).missing.map(field => field.key), ['sources']);
  assert.throws(() => core.format(fields));
});
test('multiline constraints and acceptance become actual list items', () => {
  const fields = { ...scenarios[0].fields, constraints: '甲\r\n\n乙', acceptance: '先檢查\n再核對' };
  const brief = core.format(fields);
  assert.ok(brief.includes('- 甲\n- 乙'));
  assert.ok(brief.includes('1. 先檢查\n2. 再核對'));
});
test('user content remains literal text and inputs are not mutated', () => {
  const fields = { ...scenarios[0].fields, goal: '<script>alert("sample")</script>' };
  const snapshot = JSON.stringify(fields);
  assert.ok(core.format(fields).includes(fields.goal));
  assert.equal(JSON.stringify(fields), snapshot);
});
console.log(`BRIEF CHECK OK: ${checks} behavior checks, ${scenarios.length} real scenarios`);
