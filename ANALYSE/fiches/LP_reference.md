# Fiche — `LP_reference`

> Famille : **Référence technique** · Mémoire d'analyse du 2026-11-09 · source : `ANALYSE/scripts/inventaire_exhaustif.py`

## Verdict

✅ **Capture standard complète** (handler + SMS + ordre correct) — reste à valider la réception réelle.

## Identité

| Champ | Valeur |
|---|---|
| Dossier | `LP_reference` |
| Titre HTML | « Véhicules de société » |
| `lang` | `fr` |
| Canonical | `*(absente)*` |
| Meta description | *(absente)* |
| H1 | 1 · H2 : 5 |
| Texte du 1er H1 | « Tous les véhicules à portée de clic. » |

## Poids et actifs

| Mesure | Valeur |
|---|---|
| Poids total du dossier | **0.82 Mo** (24 fichiers) |
| `index.html` | 25.2 Ko |
| Images | 19 (0.3 Mo) |
| Polices | 0 |
| JS / CSS | 3 / 1 |
| Médias jamais référencés | **0** |
| Références locales cassées | 0 |

## Capture et tracking

| Élément | État |
|---|---|
| Formulaires HTML | 1 |
| Formulaires marqués `data-ubepro-lead` | **1** |
| Champs du formulaire principal | 44 |
| `lead-handler.js` présent / chargé | oui / oui |
| `verification-sms.js` présent / chargé | oui / oui |
| Ordre des modules correct | oui |
| GTM | `GTM-53SH7D7F` |
| GA4 | `G-3XPBT7BZ10` |
| `formId` CRM | `ADW_LP_VEHICULES_DE_SOCIETE` |
| `formName` | `voiture-professionnel-form-ubepro` |
| Mode transport CRM | `nocors` (réception non confirmable) |
| Source de secours | `LP VEHICULES DE SOCIETE` |
| Version du handler | `2026-10-27-ubepro.fonctionnel2-sms1` |

## SEO, indexation et conformité

- `robots.txt` : **absent** · `sitemap.xml` : **absent**
- Points d'attention : meta description absente · canonical absente · robots.txt absent · sitemap.xml absent
- Hôtes tiers encore appelés : `www.googletagmanager.com`, `www.ubepro.fr`
- Iframes : `https://www.googletagmanager.com/ns.html?id=GTM-53SH7D7F`
- Sécurité : 1 iframe(s)

## Documentation présente

- Fichiers Markdown : 0 — *(aucun rapport)*

## Constats d'expertise

Cette LP est la **référence fonctionnelle du dépôt**. Son `lead-handler.js` (40 Ko) et son
`verification-sms.js` (14,5 Ko) sont les modèles copiés-partout ailleurs. Toute évolution du contrat
CRM / Sheets / SMS doit partir d'ici puis être propagée. Elle n'a volontairement ni `robots.txt`
ni `sitemap.xml` et son titre est « Véhicules de société » alors que le dossier s'appelle
`LP_reference` : ne pas s'y fier pour l'indexation.

## Actions recommandées

- [ ] Ajouter un `robots.txt`.
- [ ] Ajouter un `sitemap.xml`.
- [ ] Rédiger une meta description manuelle (ne pas laisser le générateur le faire).

---

*Fiche générée automatiquement à partir de mesures statiques ; les mentions « code détecté » ne valent pas preuve de fonctionnement en production.*
