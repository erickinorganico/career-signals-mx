const test = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const vm = require('node:vm');
const path = require('node:path');
const code = fs.readFileSync(path.join(__dirname, '../site/motion.js'), 'utf8');

function environment(reduced = false, observerAvailable = true) {
  const events = {};
  const state = { calls: 0, cancels: 0, classes: {}, observed: [] };
  const button = { hidden: true, addEventListener: (name, fn) => events[name] = fn, setAttribute: (name, val) => button[name] = val };
  const progress = { style: {} };
  const preference = { matches: reduced, addEventListener: (_, fn) => events.preference = fn };
  const element = { animate: () => { state.calls++; return { cancel: () => state.cancels++ }; } };
  const document = {
    documentElement: { scrollHeight: 2000, classList: { toggle: (name, enabled) => state.classes[name] = enabled } },
    querySelector: selector => selector.includes('toggle') ? button : progress,
    querySelectorAll: () => [element],
    addEventListener: () => {}
  };
  const window = {
    matchMedia: () => preference, innerHeight: 800, scrollY: 600,
    requestAnimationFrame: fn => fn(), addEventListener: () => {}
  };
  if (observerAvailable) window.IntersectionObserver = class {
    constructor(callback) { events.intersect = callback; }
    observe(target) { state.observed.push(target); }
    unobserve(target) { state.observed = state.observed.filter(x => x !== target); }
  };
  vm.runInNewContext(code, { window, document });
  return { state, events, preference, button, progress, element };
}

test('reduced motion never animates and exposes its state', () => {
  const e = environment(true);
  e.events.intersect([{ isIntersecting: true, target: e.element }]);
  assert.equal(e.state.calls, 0);
  assert.equal(e.button.disabled, true);
  assert.equal(e.button.textContent, 'Movimiento reducido');
  assert.equal(e.state.classes['motion-paused'], true);
});

test('panels reveal once; pausing cancels active animation', () => {
  const e = environment();
  e.events.intersect([{ isIntersecting: true, target: e.element }]);
  assert.equal(e.state.calls, 1);
  assert.equal(e.state.observed.length, 0);
  e.events.click();
  assert.equal(e.state.cancels, 1);
  assert.equal(e.button['aria-pressed'], 'false');
  assert.equal(e.button.textContent, 'Activar animaciones');
});

test('system preference changes cancel movement immediately', () => {
  const e = environment();
  e.events.intersect([{ isIntersecting: true, target: e.element }]);
  e.preference.matches = true;
  e.events.preference();
  assert.equal(e.state.cancels, 1);
  assert.equal(e.button.disabled, true);
});

test('unsupported observer leaves all content available', () => {
  const e = environment(false, false);
  assert.equal(e.state.calls, 0);
  assert.equal(e.progress.style.transform, 'scaleX(0.5)');
  assert.equal(e.button.hidden, false);
});
