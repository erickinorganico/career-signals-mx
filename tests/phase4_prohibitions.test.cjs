const { test } = require('node:test');
const assert = require('node:assert/strict');
const { spawn } = require('node:child_process');
const { existsSync } = require('node:fs');
const path = require('node:path');

const root = path.resolve(__dirname, '..');
const localPython = process.platform === 'win32'
  ? path.join(root, '.venv', 'Scripts', 'python.exe')
  : path.join(root, '.venv', 'bin', 'python');
const python = process.env.BRUJULA_TEST_PYTHON ||
  (existsSync(localPython) ? localPython : 'python');
const allCases = ['suppressed', 'complement', 'pdf-fetch', 'stale-current'];
const selected = process.env.GSD_PROHIB_SUBJECT || '';
const cases = selected && selected.endsWith('.bad.json')
  ? allCases.filter(name => selected.replaceAll('\\', '/').endsWith(`/${name}.bad.json`))
  : allCases;
if (selected && selected.endsWith('.bad.json') && cases.length !== 1) {
  throw new Error(`unknown Phase 4 bad subject: ${selected}`);
}

test('Phase 4 computed publication prohibitions', { concurrency: true }, async t => {
  await Promise.all(cases.map(name => t.test(`Phase 4 ${name}: computed bad rejected, clean accepted`, async () => {
    const fixture = process.env.GSD_PROHIB_SUBJECT ||
      'tests/fixtures/phase4_prohibitions/clean.json';
    const result = await new Promise((resolve, reject) => {
      const child = spawn(python,
        [path.join(root, 'tests', 'phase4_prohibitions.py'), name, fixture],
        { cwd: root, windowsHide: true });
      let stdout = '', stderr = '';
      child.stdout.setEncoding('utf8').on('data', chunk => { stdout += chunk; });
      child.stderr.setEncoding('utf8').on('data', chunk => { stderr += chunk; });
      child.on('error', reject);
      child.on('close', code => resolve({ code, stdout, stderr }));
    });
    assert.equal(result.code, 0, result.stderr);
    const receipt = JSON.parse(result.stdout);
    assert.equal(receipt.case, name);
    assert.equal(receipt.bad_rejected, true);
    assert.equal(receipt.clean_accepted, true);
    assert.ok(receipt.producer && receipt.producer !== 'fixture-only');
    assert.equal(receipt.active_subject_valid, true,
      'the computed active subject was rejected by its current API');
  })));
});
