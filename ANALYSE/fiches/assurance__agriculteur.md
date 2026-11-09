# Fiche — `assurance/agriculteur` (dossier imbriqué)

> Famille : **Autres** · Mémoire d'analyse du 2026-11-09 · source : `ANALYSE/scripts/inventaire_exhaustif.py`

## Verdict

✅ **Capture standard complète** (handler + SMS + ordre correct) — reste à valider la réception réelle.

> ⚠️ **Doublon de page** : `index.html` identique à `assurance-agriculteur`.

## Identité

| Champ | Valeur |
|---|---|
| Dossier | `assurance/agriculteur` |
| Titre HTML | « Assurance Agriculteur » |
| `lang` | `fr` |
| Canonical | `https://assurance-agriculteur.lp.comparateurpro.fr/` |
| Meta description | 123 caractères |
| H1 | 1 · H2 : 0 |
| Texte du 1er H1 | « Assurance Agricole » |

## Poids et actifs

| Mesure | Valeur |
|---|---|
| Poids total du dossier | **7.47 Mo** (94 fichiers) |
| `index.html` | 32.2 Ko |
| Images | 55 (4.33 Mo) |
| Polices | 29 |
| JS / CSS | 3 / 2 |
| Médias jamais référencés | **6** |
| Références locales cassées | 0 |

Médias orphelins (extrait) : `img/black_logo_comparateurpro-p-1080.png`, `img/black_logo_comparateurpro-p-500.png`, `img/black_logo_comparateurpro-p-800.png`, `img/logo-vectoriel-macif-p-500.jpg`, `img/mercer-logo-p-500.jpg`, `img/vinnytsia-ukraine-november-17-2023-600nw-2389537541-p-500.webp`

## Capture et tracking

| Élément | État |
|---|---|
| Formulaires HTML | 2 |
| Formulaires marqués `data-ubepro-lead` | **1** |
| Champs du formulaire principal | 42 |
| `lead-handler.js` présent / chargé | oui / oui |
| `verification-sms.js` présent / chargé | oui / oui |
| Ordre des modules correct | oui |
| GTM | `GTM-53SH7D7F` |
| `formId` CRM | `ADW_LP_ASSURANCE_AGRICULTEUR` |
| `formName` | `assurance-agriculteur-formly` |
| Mode transport CRM | `nocors` (réception non confirmable) |
| Source de secours | `LP AGRICULTEUR` |
| Version du handler | `2026-10-27-ubepro.fonctionnel2-sms1` |

## SEO, indexation et conformité

- `robots.txt` : présent · `sitemap.xml` : présent
- Aucun point d'attention SEO détecté par les contrôles automatiques.

## Documentation présente

- Fichiers Markdown : 2 — RAPPORT-INTEGRATION.md rapport-site.md
- Date(s) citée(s) dans les rapports : 2026-10-22

## Constats d'expertise

Version « fonctionnelle » de l'assurance agriculteur (avec `docs/` complet et `Code.gs`),
distincte de `assurance-agriculteur`, `assurance-agriculteur-v2` et `assurance/agriculteur`.
⚠ **Collision de `formId`** avec `assurance-agriculteur` : `ADW_LP_ASSURANCE_AGRICULTEUR`. Les deux
dossiers enverront des leads impossibles à distinguer côté CRM. `sitemap.xml` présent mais pas de
`style.css` à la racine : vérifier que la feuille est bien chargée.

## Actions recommandées

- [ ] Supprimer ou déplacer les 6 médias jamais affichés (gain de poids direct).
- [ ] Supprimer le doublon (une seule page doit survivre).

---

*Fiche générée automatiquement à partir de mesures statiques ; les mentions « code détecté » ne valent pas preuve de fonctionnement en production.*
