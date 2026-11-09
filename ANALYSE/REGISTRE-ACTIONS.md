# Registre des actions — `comparateurpro.fr`

> Chaque ligne est une action **décidable**, avec son risque, son gain et son critère de réussite.
> Cocher au fur et à mesure. Les identifiants (C1, M1, Q1) sont ceux du mémoire
> `ANALYSE/MEMOIRE-ANALYSE.md`.
>
> **Règle de priorisation** : d'abord ce qui bloque un lead (C), puis ce qui coûte de l'argent (M),
> puis ce qui se voit (Q), puis le confort (G).

---

## Étape 0 — Sécuriser la connaissance (1 jour, risque nul)

| ☐ | Action | Pourquoi | Critère de réussite |
|---|---|---|---|
| ☐ | **Récupérer `lp2site.py`** et le versionner dans `tools/` | sans lui, chaque nouvelle LP réintroduit les mêmes défauts | le script est dans le dépôt et exécutable |
| ☐ | Écrire un `README.md` à la racine | 146 dossiers sans mode d'emploi | un nouvel arrivant sait déployer une LP en < 10 min |
| ☐ | Documenter la commande de test unique | aujourd'hui JS et Python se lancent différemment | une seule commande fait tout |
| ☐ | Archiver ce mémoire et `ANALYSE/` dans le dépôt | mémoire collective | commit effectué |

**Commande de test unifiée à documenter** (vérifiée pendant l'analyse) :
```sh
npm ci --prefix tests && npm test --prefix tests          # 368 tests JS
PYTHONPATH=. python3 -m unittest discover -s tests -p "test_*.py"   # 12 tests Python
python3 tools/audit_fonctionnalites.py                    # audit statique
python3 ANALYSE/scripts/inventaire_exhaustif.py            # inventaire + statuts
```

---

## Étape 1 — Arrêter l'hémorragie (semaine 1, risque faible)

| ☐ | ID | Action | Gain | Risque | Critère de réussite |
|---|---|---|---|---|---|
| ☐ | M3 | Supprimer `assurance-consultants-societe-conseil - Copie` | débloque les scripts shell | nul (doublon exact) | dossier absent |
| ☐ | M2 | Supprimer l'arborescence `assurance/` (7 dossiers) | **−54 Mo** | **moyen** : confirmer d'abord que la racine est bien la version de production | 54 Mo libérés, aucune LP perdue |
| ☐ | M1 | Purger les 678 médias orphelins | **−100 Mo au moins** | faible : vérifier page par page | aucune image cassée |
| ☐ | M8 | Trancher les 7 échecs de test | suite verte | faible | `npm test` → 368/368 |
| ☐ | M5 | Activer `audit_poids.py --csv` en contrôle périodique | éviter le retour du problème | nul | rapport archivé |

> ⚠️ **Avant toute suppression** : lancer `python3 ANALYSE/scripts/audit_poids.py` et croiser avec
> `ANALYSE/data/doublons.csv`. Deux copies identiques peuvent correspondre à deux déploiements
> légitimes (préprod / prod).

---

## Étape 2 — Réparer la capture (semaine 2, impact commercial direct)

| ☐ | ID | Action | Périmètre | Critère de réussite |
|---|---|---|---|---|
| ☐ | C1 | Reprendre les **37 pages du statut C** une par une | liste §7.1 du mémoire | chaque page : soit marquée `data-ubepro-lead="1"`, soit exception écrite |
| ☐ | C2 | Restaurer ou retirer `assurance-agriculteur-v2` (0 formulaire) | 1 | page avec formulaire OU retirée du lot |
| ☐ | C2 | Raccorder `agriculteur` (2 formulaires, 0 marqué) | 1 | `formId` unique, lead test reçu |
| ☐ | C3 | Attribuer un `formId` unique à `assurance-agriculteur` | 1 | plus de collision avec `agriculteur` |
| ☐ | C4 | **Tester un vrai SMS** sur chaque domaine de production | 87 | code reçu, numéro vérifié, lead transmis |
| ☐ | C5 | Obtenir une confirmation de réception CRM (passer en `cors` si possible) | 87 | au moins une preuve de réception côté CRM |
| ☐ | M9 | Mettre en place un **lead de test quotidien** automatisé | global | alerte si aucun lead reçu en 24 h |

> **C'est l'étape la plus rentable du plan.** Une seule page du statut C réparée peut représenter
> des dizaines de leads par mois.

---

## Étape 3 — Assainir le SEO (semaine 3, sans risque visuel)

| ☐ | ID | Action | Périmètre | Méthode |
|---|---|---|---|---|
| ☐ | M6 | Passer `lang="en"` → `lang="fr"` | 81 pages | remplacement ciblé + vérification |
| ☐ | M7 | Un `<h1>` unique par page | 129 pages | conserver les classes (`.h1-iard-v2` porte la typo) — méthode validée |
| ☐ | Q7 | Réduire les 17 H1 de `assurance-iard-v2` | 1 | idem |
| ☐ | Q4 | Réécrire les meta descriptions | 20 pages à plus fort trafic | rédaction manuelle |
| ☐ | Q2 | Ajouter `robots.txt` / `sitemap.xml` | 6 pages | copie du modèle standard |
| ☐ | — | Trancher la stratégie `canonical` (132 domaines) | global | décision écrite : indexation ou `noindex` assumé |

---

## Étape 4 — Réduire le poids (semaine 4-6, gain visible et mesurable)

| ☐ | Action | Gain estimé | Risque |
|---|---|---|---|
| ☐ | Externaliser les polices partagées | 20-30 % du poids | moyen (dépend du déploiement) |
| ☐ | Convertir en WebP les JPG > 300 Ko | 30-50 % des images | faible |
| ☐ | Sortir les 4 vidéos de Git (`canal`, `lexus-lbx-2`) | **−39 Mo** | nul |
| ☐ | Évaluer l'amputation de `script.js` (1,45 Mo × 139) | le plus gros levier | élevé (moteur de formulaire) |
| ☐ | Contrôle CI : « aucun fichier > 1 Mo, aucune page > 10 Mo » | prévention | nul |

**Objectif réaliste** : 1 098 Mo → **265 Mo** sans perdre une seule fonctionnalité.

---

## Étape 5 — Industrialiser (mois 2)

| ☐ | Action |
|---|---|
| ☐ | Rétablir `lp2site.py` comme **seul** chemin de création d'une LP (corrections H1/lang intégrées au générateur) |
| ☐ | Écrire `CONTRAT-CAPTURE.md` unique (aujourd'hui éparpillé dans 6 `docs/`) |
| ☐ | Réécrire ou supprimer la documentation qui contredit le code (M10, M11, M12) |
| ☐ | Mettre en place un déploiement reproductible (aujourd'hui : copie manuelle) |
| ☐ | Ajouter un test qui détecte les affirmations documentaires démenties par le code |

---

## Décisions à trancher par le métier (je ne peux pas les prendre à votre place)

| # | Question | Options |
|---|---|---|
| D-01 | La vérification SMS est-elle conservée partout ? | (a) partout (b) uniquement sur les campagnes à forte valeur (c) nulle part |
| D-02 | `assurance/` est-il l'ancien ou le nouveau ? | (a) supprimer `assurance/` (b) supprimer la racine équivalente |
| D-03 | 132 domaines indexés ou `noindex` assumé sur les LP payantes ? | (a) statu quo (b) `noindex` + canonical par campagne |
| D-04 | `assurance-consultants-societe-conseil` : wrapper ou vraie LP ? | (a) exclure des tests (b) réintroduire une LP (c) tester le bridge |
| D-05 | Les pages de remerciement doivent-elles rester dans Git ? | (a) oui (b) hébergement léger séparé |

---

*Registre établi le 9 novembre 2026 à partir de `ANALYSE/data/inventaire.json` (146 pages mesurées).*
