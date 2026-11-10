# Confort des formulaires — périmètre avec form_id détecté

## Réalisé

- **86 pages modifiées sur 88 ciblées** : ajout de `autocomplete` et, pour les champs reconnus, `inputmode="tel"` ou `inputmode="numeric"` dans les formulaires de lead. Les attributs déjà présents sont conservés. L'attribut `type` n'a pas été changé afin d'éviter de modifier les sélecteurs ou la validation existants. Les 2 autres pages n'avaient pas de changement applicable selon cette détection. Le clavier affiché dépend du navigateur.
- **Instructions SMS** : le texte existant a été complété dans 87 modules SMS chargés et un script SMS intégré ; il indique l'usage d'un mobile français 06/07, la vérification par code et sa validité déjà annoncée de 10 minutes. Le délai total du formulaire n'a pas été inventé : il nécessite une mesure réelle.
- **Progression pilote sur `LP_reference`** : repères « Vos besoins → Vos coordonnées », intégrés aux deux branches et aux étapes correspondantes. Ils indiquent deux grandes phases, non un nombre précis d'étapes, car le parcours est conditionnel. Les autres LP conservent leurs indicateurs existants ; aucune progression généralisée n'a été ajoutée à l'aveugle.
- **Bouton précédent pilote** : le test jsdom a révélé que `LP_reference` effaçait une réponse au retour. Un module local restaure en mémoire les champs de l'étape retrouvée, sans stockage ni envoi supplémentaires. Les deux branches initiales et le retour vers un e-mail saisi ont été testés. Un retour initial a aussi été testé sur `assurance-multirisques`. Cela ne valide pas tous les retours de toutes les LP.
- **Libellés ciblés** : « Recevoir mes devis » sur `LP_reference`, `assurance-multirisques`, `assurance/multirisques` et `energie` ; « Demander un essai » sur `alfaromeo-tonale`. Les autres CTA n'ont pas été modifiés sans validation de leur promesse et de leur parcours.

## Préservation du contrat

Les `form_id`, les noms et valeurs des champs métier, les configurations CRM, Sheets et tracking, les questions, la logique de validation et le caractère obligatoire du SMS n'ont pas été volontairement modifiés. Une comparaison statique avant/après des formulaires et de leurs champs sur les 88 pages ne trouve aucune différence hors attributs `autocomplete`/`inputmode` et libellés des boutons ciblés. La restauration de l'étape précédente maintient une réponse que le visiteur avait déjà donnée ; elle ne crée pas de réponse par défaut.

## Tests et limites

- **21 tests Python** réussis, y compris les attributs des champs reconnus, les instructions SMS et les identifiants.
- **12 tests jsdom ciblés** réussis sur le retour, le module mobile et le formulaire spécifique esthéticiennes.
- **30 tests jsdom ciblés** réussis sur LP_reference, énergie, multirisques et d'autres pages incluses par le filtre, avec réponses réseau simulées.
- Syntaxe : **89 fichiers JavaScript** modifiés ou ajoutés vérifiés avec `node --check`.
- Pas de vérification sur appareil réel ni de test de tous les parcours et de toutes les branches, pas de lead de production et pas de mesure réelle de durée ou d'amélioration de conversion. La suite JavaScript complète n'a pas été exécutée. Tester d'abord en préproduction les campagnes actives et les parcours pilotes avant d'étendre les repères ou la restauration du bouton précédent.
