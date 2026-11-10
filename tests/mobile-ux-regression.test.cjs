const { test } = require('node:test');
const assert = require('node:assert/strict');
const fs = require('node:fs');
const path = require('node:path');
const { JSDOM } = require('jsdom');
const root = path.resolve(__dirname, '..');

test('mobile : un message de succès masqué ne bloque pas les liens ni ne prétend recevoir un lead', async () => {
  const dom = new JSDOM(`<!doctype html><style>.w-form-done{display:none}</style><body>
    <a href="#etape" id="next">Suivant</a><input name="telephone" placeholder="Téléphone">
    <div class="w-form-done">Merci</div></body>`,
    { url: 'https://example.test/', runScripts: 'outside-only', pretendToBeVisual: true });
  const w = dom.window;
  w.matchMedia = () => ({ matches: true });
  try {
    w.eval(fs.readFileSync(path.join(root, 'tools/mobile-ux.js'), 'utf8'));
    w.document.dispatchEvent(new w.Event('DOMContentLoaded'));
    await new Promise(resolve => setTimeout(resolve, 650));
    assert.equal(w.document.getElementById('mux-barre'), null);
    assert.equal(w.document.querySelector('input').getAttribute('aria-label'), 'Téléphone');
    assert.equal(w.document.body.classList.contains('mux-tactile'), true);
    const click = new w.MouseEvent('click', { bubbles: true, cancelable: true });
    assert.equal(w.document.getElementById('next').dispatchEvent(click), true);
    w.document.querySelector('.w-form-done').style.display = 'block';
    await new Promise(resolve => setTimeout(resolve, 50));
    assert.equal(w.document.getElementById('mux-barre'), null);
    assert.equal(w.document.getElementById('next').dispatchEvent(new w.MouseEvent('click', { bubbles: true, cancelable: true })), true);
    await new Promise(resolve => setTimeout(resolve, 20));
  } finally { w.close(); }
});
