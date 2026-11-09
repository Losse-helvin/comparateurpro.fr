# Fiche — `typ-categories`

> Famille : **Wrappers iframe** · Mémoire d'analyse du 2026-11-09 · source : `ANALYSE/scripts/inventaire_exhaustif.py`

## Verdict

⚪ **Page sans formulaire** (contenu, remerciement, légale ou wrapper).

## Identité

| Champ | Valeur |
|---|---|
| Dossier | `typ-categories` |
| Titre HTML | « TYP Catégories » |
| `lang` | `en` |
| Canonical | `https://typ-categories.lp.comparateurpro.fr/` |
| Meta description | 116 caractères |
| H1 | 0 · H2 : 0 |

## Poids et actifs

| Mesure | Valeur |
|---|---|
| Poids total du dossier | **6.58 Mo** (74 fichiers) |
| `index.html` | 7.8 Ko |
| Images | 42 (3.56 Mo) |
| Polices | 25 |
| JS / CSS | 1 / 2 |
| Médias jamais référencés | **0** |
| Références locales cassées | 0 |

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

- `robots.txt` : présent · `sitemap.xml` : présent
- Points d'attention : aucun H1 · lang="en"
- Iframes : `../typ-formulaires-vehicules-thank-you-page/`, `../typ-formulaires-securite-thank-you-page/`, `../typ-formulaires-energie-thank-you-page/`, `../typ-formulaires-panneaux-thank-you-page/`, `../typ-formulaires-caisses-thank-you-page/`, `../typ-formulaires-typ-log-entreprise/`
- Sécurité : 6 iframe(s)

## Documentation présente

- Fichiers Markdown : 1 — rapport-site.md
- Date(s) citée(s) dans les rapports : 2026-10-22

## Constats d'expertise

Contient 6 iframes pointant vers les pages « thank you » de la famille `typ-formulaires`.
Un vrai routeur de tunnels, sans capture propre. Très fragile : tout repose sur des chemins relatifs
`../typ-formulaires-…`.

## Actions recommandées

- [ ] Créer un H1 unique porteur du mot-clé métier.
- [ ] Décider si la page doit être trackée ; si oui, ajouter GTM après le Consent Mode.

---

*Fiche générée automatiquement à partir de mesures statiques ; les mentions « code détecté » ne valent pas preuve de fonctionnement en production.*
