# Fiche — `template-2`

> Famille : **Outils / divers** · Mémoire d'analyse du 2026-11-09 · source : `ANALYSE/scripts/inventaire_exhaustif.py`

## Verdict

🔴 **Formulaire présent mais NON marqué** `data-ubepro-lead="1"` → aucune capture standard.

## Identité

| Champ | Valeur |
|---|---|
| Dossier | `template-2` |
| Titre HTML | « Template 2 » |
| `lang` | `en` |
| Canonical | `https://template-2.lp.comparateurpro.fr/` |
| Meta description | 112 caractères |
| H1 | 1 · H2 : 0 |
| Texte du 1er H1 | « Galerie » |

## Poids et actifs

| Mesure | Valeur |
|---|---|
| Poids total du dossier | **8.88 Mo** (90 fichiers) |
| `index.html` | 16.7 Ko |
| Images | 56 (5.83 Mo) |
| Polices | 27 |
| JS / CSS | 1 / 2 |
| Médias jamais référencés | **24** |
| Références locales cassées | 0 |

Médias orphelins (extrait) : `img/2021-Cupra-Formentor-001-1080-p-1080.jpg`, `img/2021-Cupra-Formentor-001-1080-p-1600.jpg`, `img/2021-Cupra-Formentor-001-1080-p-500.jpg`, `img/2021-Cupra-Formentor-001-1080-p-800.jpg`, `img/2021-Cupra-Formentor-002-1080-p-1080.jpg`, `img/2021-Cupra-Formentor-002-1080-p-1600.jpg`, `img/2021-Cupra-Formentor-002-1080-p-500.jpg`, `img/2021-Cupra-Formentor-002-1080-p-800.jpg` …

## Capture et tracking

| Élément | État |
|---|---|
| Formulaires HTML | 1 |
| Formulaires marqués `data-ubepro-lead` | **0** |
| Champs du formulaire principal | 0 |
| `lead-handler.js` présent / chargé | non / non |
| `verification-sms.js` présent / chargé | non / non |
| Ordre des modules correct | non |
| GTM | *(aucun)* |
| `formId` CRM | `—` |

## SEO, indexation et conformité

- `robots.txt` : présent · `sitemap.xml` : présent
- Points d'attention : lang="en"

## Documentation présente

- Fichiers Markdown : 1 — rapport-site.md
- Date(s) citée(s) dans les rapports : 2026-10-22

## Constats d'expertise

Dossier « template » : squelette Webflow réutilisable. 24 médias orphelins, formulaire non
marqué, aucun GTM. Sert de gabarit — à sortir du périmètre de production.

## Actions recommandées

- [ ] Qualifier le formulaire : marquer `data-ubepro-lead="1"` ou documenter pourquoi il ne doit pas l'être.
- [ ] Supprimer ou déplacer les 24 médias jamais affichés (gain de poids direct).
- [ ] Décider si la page doit être trackée ; si oui, ajouter GTM après le Consent Mode.

---

*Fiche générée automatiquement à partir de mesures statiques ; les mentions « code détecté » ne valent pas preuve de fonctionnement en production.*
