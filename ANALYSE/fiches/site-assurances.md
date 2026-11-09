# Fiche — `site-assurances`

> Famille : **Pages légales / site vitrine** · Mémoire d'analyse du 2026-11-09 · source : `ANALYSE/scripts/inventaire_exhaustif.py`

## Verdict

⚪ **Page sans formulaire** (contenu, remerciement, légale ou wrapper).

## Identité

| Champ | Valeur |
|---|---|
| Dossier | `site-assurances` |
| Titre HTML | « Assurance professionnelle | Comparateurpro » |
| `lang` | `fr` |
| Canonical | `*(absente)*` |
| Meta description | 40 caractères |
| H1 | 1 · H2 : 18 |
| Texte du 1er H1 | « Assurance professionnelle » |

## Poids et actifs

| Mesure | Valeur |
|---|---|
| Poids total du dossier | **2.98 Mo** (33 fichiers) |
| `index.html` | 61.6 Ko |
| Images | 20 (1.6 Mo) |
| Polices | 1 |
| JS / CSS | 1 / 3 |
| Médias jamais référencés | **1** |
| Références locales cassées | 0 |

Médias orphelins (extrait) : `assets/sante.jpg`

## Capture et tracking

| Élément | État |
|---|---|
| Formulaires HTML | 0 |
| Formulaires marqués `data-ubepro-lead` | **0** |
| Champs du formulaire principal | 0 |
| `lead-handler.js` présent / chargé | non / non |
| `verification-sms.js` présent / chargé | non / non |
| Ordre des modules correct | non |
| GTM | *(aucun)* |
| `formId` CRM | `—` |

## SEO, indexation et conformité

- `robots.txt` : **absent** · `sitemap.xml` : **absent**
- Points d'attention : canonical absente · robots.txt absent · sitemap.xml absent

## Documentation présente

- Fichiers Markdown : 1 — *(aucun rapport)*

## Constats d'expertise

Site vitrine multi-pages (7 pages HTML, 63 Ko d'index) — le seul dossier du dépôt
avec une vraie arborescence de contenu. `README.md` explique comment le lancer
(`python3 -m http.server 4000`). Aucun lien vers les LP du dépôt : c'est un univers séparé.

## Actions recommandées

- [ ] Ajouter un `robots.txt`.
- [ ] Ajouter un `sitemap.xml`.
- [ ] Décider si la page doit être trackée ; si oui, ajouter GTM après le Consent Mode.

---

*Fiche générée automatiquement à partir de mesures statiques ; les mentions « code détecté » ne valent pas preuve de fonctionnement en production.*
