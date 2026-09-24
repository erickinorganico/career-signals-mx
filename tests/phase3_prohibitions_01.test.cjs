const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const { existsSync } = require('node:fs');

for (const [id, description] of [
  ['p1', 'sparse state sex and field cells stay present with null and cause'],
  ['p2', 'professional cohort keeps its exact known-age completed-study label'],
]) {
  test(description, () => {
    const root = path.resolve(__dirname, '..');
    const subject = process.env.GSD_PROHIB_SUBJECT ||
      'tests/fixtures/phase3_prohibitions/01.clean.json';
    const localPython = process.platform === 'win32'
      ? path.join(root, '.venv', 'Scripts', 'python.exe')
      : path.join(root, '.venv', 'bin', 'python');
    const python = process.env.BRUJULA_TEST_PYTHON ||
      (existsSync(localPython) ? localPython : 'python');
    const result = spawnSync(python,
      [path.join(root, 'tests', 'phase3_prohibitions_01.py'), id, subject],
      { cwd: root, encoding: 'utf8', windowsHide: true, timeout: 30000 });
    assert.equal(result.status, 0, result.stderr || String(result.error));
    assert.match(result.stdout, /checked computed Phase 3 profiles and population definitions/);
  });
}
