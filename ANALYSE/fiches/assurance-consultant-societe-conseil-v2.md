# Fiche — `assurance-consultant-societe-conseil-v2`

> Famille : **Wrappers iframe** · Mémoire d'analyse du 2026-11-09 · source : `ANALYSE/scripts/inventaire_exhaustif.py`

## Verdict

⚪ **Page sans formulaire** (contenu, remerciement, légale ou wrapper).

> ⚠️ **Doublon de page** : `index.html` identique à `assurance-consultants-societe-conseil`.

## Identité

| Champ | Valeur |
|---|---|
| Dossier | `assurance-consultant-societe-conseil-v2` |
| Titre HTML | « Assurance consultant et societe de conseil » |
| `lang` | `fr` |
| Canonical | `https://assurance-consultant-societe-conseil-v2.lp.comparateurpro.fr/` |
| Meta description | 144 caractères |
| H1 | 0 · H2 : 0 |

## Poids et actifs

| Mesure | Valeur |
|---|---|
| Poids total du dossier | **5.73 Mo** (64 fichiers) |
| `index.html` | 2.8 Ko |
| Images | 28 (2.71 Mo) |
| Polices | 25 |
| JS / CSS | 2 / 2 |
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
| GTM | `GTM-53SH7D7F` |
| `formId` CRM | `—` |

## SEO, indexation et conformité

- `robots.txt` : présent · `sitemap.xml` : présent
- Points d'attention : aucun H1
- Hôtes tiers encore appelés : `www.googletagmanager.com`, `www.ubepro.com`
- Iframes : `https://www.googletagmanager.com/ns.html?id=GTM-53SH7D7F`, `https://www.ubepro.com/assurance-consultant-conseil-v2/`
- Sécurité : 2 iframe(s)

## Documentation présente

- Fichiers Markdown : 4 — RAPPORT-MODIFICATIONS.md rapport-site.md
- Date(s) citée(s) dans les rapports : 2026-10-22, 2026-10-26

## Constats d'expertise

**Wrapper iframe** (2,9 Ko) qui embarre `https://www.ubepro.com/assurance-consultant-conseil-v2/`.
Apporte le pont `bridge.js` (consentement + URL parente + relais SMS) et `GTM-53SH7D7F`.
Pourtant ce dossier pèse 5,9 Mo et sa racine 1,6 Mo : un `script.js` de 1,5 Mo et les polices sont
chargés **pour rien**, la page ne les utilise pas. Suppression = ~5,5 Mo gagnés.

## Actions recommandées

- [ ] Créer un H1 unique porteur du mot-clé métier.
- [ ] Supprimer le doublon (une seule page doit survivre).

---

*Fiche générée automatiquement à partir de mesures statiques ; les mentions « code détecté » ne valent pas preuve de fonctionnement en production.*
