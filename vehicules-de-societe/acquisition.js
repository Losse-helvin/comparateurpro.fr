/* La précision du budget ne concerne que la location longue durée. */
(function () {
  'use strict';
  var form = document.querySelector('form[data-ubepro-lead="1"]');
  var budget = document.getElementById('budget-location');
  if (!form || !budget) return;

  var budgetInputs = budget.querySelectorAll('input[name="reponse_6"]');
  var step = budget.closest('[data-form="step"]');
  var error = document.getElementById('acquisition-erreur');
  function updateBudget() {
    var selected = form.querySelector('input[name="reponse_5"]:checked');
    var isLocation = !!selected && selected.value === 'Location longue durée';
    budget.hidden = !isLocation;
    budget.disabled = !isLocation;
    for (var i = 0; i < budgetInputs.length; i++) {
      budgetInputs[i].required = isLocation;
      if (!isLocation) budgetInputs[i].checked = false;
    }
  }
  form.addEventListener('change', function (event) {
    if (event.target.name === 'reponse_5') updateBudget();
    if ((event.target.name === 'reponse_5' || event.target.name === 'reponse_6') && error) {
      error.hidden = true;
    }
  });
  // Formly ne valide pas systématiquement plusieurs groupes radio sur une même étape.
  form.addEventListener('click', function (event) {
    var next = event.target.closest('[data-form="next-btn"]');
    if (!next || !step || !step.contains(next)) return;
    var acquisition = form.querySelector('input[name="reponse_5"]:checked');
    var budgetSelected = form.querySelector('input[name="reponse_6"]:checked');
    var message = !acquisition ? 'Veuillez choisir un mode d’acquisition.' :
      (!budget.hidden && !budgetSelected ? 'Veuillez choisir un budget.' : '');
    if (!message) return;
    event.preventDefault();
    event.stopPropagation();
    if (error) { error.textContent = message; error.hidden = false; }
    (acquisition ? budgetInputs[0] : form.querySelector('input[name="reponse_5"]')).focus();
  }, true);
  updateBudget();
})();
