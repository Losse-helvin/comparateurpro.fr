/* Préserve uniquement les réponses de l'étape retrouvée après « Précédent ».
   Aucune donnée n'est stockée ou transmise par ce module. */
(function () {
  'use strict';
  function init() {
    var form = document.querySelector('form[data-ubepro-lead="1"]');
    if (!form) return;
    form.addEventListener('click', function (event) {
      var back = event.target.closest && event.target.closest('[data-form="back-btn"]');
      if (!back || !form.contains(back)) return;
      var steps = Array.prototype.slice.call(form.querySelectorAll('[data-form="step"]'));
      var before = steps.find(function (step) { return step.getClientRects().length; });
      if (!before) return;
      var snapshot = Array.prototype.map.call(form.querySelectorAll('input:not([type="hidden"]),select,textarea'), function (field) {
        return { field: field, value: field.value, checked: field.checked };
      });
      window.setTimeout(function () {
        var target = steps.find(function (step) { return step !== before && step.getClientRects().length; });
        if (!target) return;
        snapshot.forEach(function (item) {
          var field = item.field;
          if (!target.contains(field) || !field.getClientRects().length || field.disabled) return;
          if (field.type === 'radio' || field.type === 'checkbox') {
            field.checked = item.checked;
            var label = field.closest('label');
            var visual = label && label.querySelector('.w-form-formradioinput, .w-checkbox-input');
            if (visual && visual !== field) visual.classList.toggle('w--redirected-checked', item.checked);
          } else if (field.type !== 'submit' && field.type !== 'button') {
            field.value = item.value;
          }
        });
      }, 0);
    }, true);
  }
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', init, { once: true });
  else init();
})();
