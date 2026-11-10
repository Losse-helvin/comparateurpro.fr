const { test } = require('node:test');
const assert = require('node:assert/strict');
const { JSDOM, VirtualConsole } = require('jsdom');
const fs = require('node:fs');
const path = require('node:path');
const root = path.resolve(__dirname, '..');
const delay = ms => new Promise(resolve => setTimeout(resolve, ms));

for (const [site, choiceIndex] of [['LP_reference', 0], ['LP_reference', 1], ['assurance-multirisques', 0]]) {
  test(`${site} : retour conserve la réponse, branche ${choiceIndex + 1}`, async () => {
    const vc = new VirtualConsole();
    const dom = new JSDOM(fs.readFileSync(path.join(root, site, 'index.html'), 'utf8'), {
      url: 'https://example.test/', runScripts: 'outside-only', pretendToBeVisual: true, virtualConsole: vc
    });
    const w = dom.window;
    w.HTMLCanvasElement.prototype.getContext = () => ({ fillRect(){}, getImageData(){ return {data:[0,0,0,255]}; } });
    w.matchMedia = () => ({matches:false,addListener(){},removeListener(){},addEventListener(){},removeEventListener(){}});
    w.scrollTo = () => {}; w.gtag = () => {}; w.dataLayer = [];
    w.Element.prototype.getClientRects = function () {
      for (let el = this; el; el = el.parentElement) if (el.style.display === 'none') return [];
      return [1];
    };
    w.XMLHttpRequest = function () { this.open=()=>{}; this.setRequestHeader=()=>{}; this.send=()=>{}; };
    try {
      for (const file of ['script.js','lead-handler.js','verification-sms.js']) w.eval(fs.readFileSync(path.join(root, site, file),'utf8'));
      if (site === 'LP_reference') w.eval(fs.readFileSync(path.join(root, site, 'retour-formulaire.js'),'utf8'));
      await delay(500);
      const form = w.document.querySelector('form[data-ubepro-lead="1"]');
      const steps = [...form.querySelectorAll('[data-form="step"]')];
      const first = steps[0];
      const choice = first.querySelectorAll('input[type="radio"], input[type="checkbox"]')[choiceIndex];
      assert.ok(choice); choice.click();
      await delay(500);
      if (first.getClientRects().length) {
        first.querySelector('[data-form="next-btn"]').click();
        await delay(500);
      }
      assert.equal(first.getClientRects().length, 0, 'étape suivante ouverte');
      const visible = steps.find(el => el.getClientRects().length);
      assert.ok(visible);
      const back = [...visible.querySelectorAll('[data-form="back-btn"]')].find(el => el.getClientRects().length);
      assert.ok(back); back.click(); await delay(500);
      assert.ok(first.getClientRects().length, 'étape initiale retrouvée');
      assert.equal(choice.checked, true, 'réponse conservée après retour');
      if (site === 'LP_reference') {
        assert.match(first.querySelector('.lp-parcours').textContent, /Vos besoins.*Vos coordonnées/);
        first.querySelector('[data-form="next-btn"]').click(); await delay(500);
        assert.equal(first.getClientRects().length, 0, 'on peut poursuivre avec la réponse conservée');
        const active = steps.find(el => el.getClientRects().length);
        const marker = [...active.querySelectorAll('.lp-parcours')].find(el => el.getClientRects().length);
        assert.ok(marker, 'progression visible sur chaque branche');
        if (choiceIndex === 0) {
          for (let i = 0; i < 4 && ![...form.querySelectorAll('[name="mail"]')].some(el => el.getClientRects().length); i++) {
            const step = steps.find(el => el.getClientRects().length);
            const radio = [...step.querySelectorAll('input[type="radio"]')].find(el => el.getClientRects().length);
            assert.ok(radio, 'choix disponible'); radio.click(); await delay(500);
            if (step.getClientRects().length) { const next = [...step.querySelectorAll('[data-form="next-btn"]')].find(el => el.getClientRects().length); assert.ok(next); next.click(); await delay(500); }
          }
          const email = form.querySelector('[name="mail"]'); assert.ok(email.getClientRects().length);
          email.value = 'test@example.test'; email.dispatchEvent(new w.Event('input', { bubbles:true }));
          const emailStep = steps.find(el => el.contains(email));
          emailStep.querySelector('[data-form="next-btn"]').click(); await delay(500);
          assert.equal(emailStep.getClientRects().length, 0);
          const nextStep = steps.find(el => el.getClientRects().length);
          nextStep.querySelector('[data-form="back-btn"]').click(); await delay(500);
          assert.ok(emailStep.getClientRects().length); assert.equal(email.value, 'test@example.test');
          assert.match(emailStep.querySelector('.lp-parcours').getAttribute('aria-label'), /coordonnées/);
        }
      }
    } finally { w.close(); }
  });
}
