const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const { existsSync } = require('node:fs');

for (const [id, description] of [
  ['p5', 'study field claims never become causal effects or matching occupations'],
  ['p6', 'opening findings contain no advice, extra quantity or invented significance'],
  ['p7', 'agent templates cannot activate sources or restore suppressed figures'],
]) {
  test(description, () => {
    const root = path.resolve(__dirname, '..');
    const subject = process.env.GSD_PROHIB_SUBJECT ||
      'tests/fixtures/phase3_prohibitions/03.clean.json';
    const localPython = process.platform === 'win32'
      ? path.join(root, '.venv', 'Scripts', 'python.exe')
      : path.join(root, '.venv', 'bin', 'python');
    const python = process.env.BRUJULA_TEST_PYTHON ||
      (existsSync(localPython) ? localPython : 'python');
    const result = spawnSync(python,
      [path.join(root, 'tests', 'phase3_prohibitions_03.py'), id, subject],
      { cwd: root, encoding: 'utf8', windowsHide: true, timeout: 120000 });
    assert.equal(result.status, 0, result.stderr || String(result.error));
    assert.match(result.stdout, /checked current Phase 3 claim and packet APIs/);
  });
}
