const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('node:path');
const { existsSync } = require('node:fs');

for (const [id, description] of [
  ['p3', 'singleton adjustment remains review and nonofficial'],
  ['p4', 'suppressed diagnostics remain absent throughout public JSON'],
]) {
  test(description, () => {
    const root = path.resolve(__dirname, '..');
    const subject = process.env.GSD_PROHIB_SUBJECT ||
      'tests/fixtures/phase2_prohibitions/02.clean.json';
    const localPython = process.platform === 'win32'
      ? path.join(root, '.venv', 'Scripts', 'python.exe')
      : path.join(root, '.venv', 'bin', 'python');
    const python = process.env.BRUJULA_TEST_PYTHON ||
      (existsSync(localPython) ? localPython : 'python');
    const result = spawnSync(python, [path.join(root, 'tests', 'phase2_prohibitions_02.py'), id, subject], {
      cwd: root, encoding: 'utf8', windowsHide: true, timeout: 30000,
    });
    assert.equal(result.status, 0, result.stderr || String(result.error));
    assert.match(result.stdout, /checked computed Phase 2 precision and public projection/);
  });
}
