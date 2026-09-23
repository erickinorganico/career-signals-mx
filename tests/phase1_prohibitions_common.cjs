const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawnSync } = require('node:child_process');
const path = require('node:path');

function check(id, description) {
  test(description, () => {
    const root = path.resolve(__dirname, '..');
    const subject = process.env.GSD_PROHIB_SUBJECT ||
      `tests/fixtures/phase1_prohibitions/${id}.clean.json`;
    const python = path.join(root, '.venv', 'Scripts', 'python.exe');
    const result = spawnSync(python, [path.join(root, 'tests', 'phase1_prohibitions.py'), id, subject], {
      cwd: root, encoding: 'utf8', windowsHide: true, timeout: 15000,
    });
    assert.equal(result.status, 0, result.stderr || String(result.error));
    assert.match(result.stdout, /checked actual Phase 1 API/);
  });
}

module.exports = { check };
