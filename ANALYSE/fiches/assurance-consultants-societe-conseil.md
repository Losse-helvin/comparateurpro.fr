# Fiche — `assurance-consultants-societe-conseil`

> Famille : **Wrappers iframe** · Mémoire d'analyse du 2026-11-09 · source : `ANALYSE/scripts/inventaire_exhaustif.py`

## Verdict

⚪ **Page sans formulaire** (contenu, remerciement, légale ou wrapper).

> ⚠️ **Doublon de page** : `index.html` identique à `assurance-consultant-societe-conseil-v2`.

## Identité

| Champ | Valeur |
|---|---|
| Dossier | `assurance-consultants-societe-conseil` |
| Titre HTML | « Assurance consultant et societe de conseil » |
| `lang` | `fr` |
| Canonical | `https://assurance-consultant-societe-conseil-v2.lp.comparateurpro.fr/` |
| Meta description | 144 caractères |
| H1 | 0 · H2 : 0 |

## Poids et actifs

| Mesure | Valeur |
|---|---|
| Poids total du dossier | **8.08 Mo** (112 fichiers) |
| `index.html` | 2.8 Ko |
| Images | 67 (4.96 Mo) |
| Polices | 29 |
| JS / CSS | 4 / 2 |
| Médias jamais référencés | **38** |
| Références locales cassées | 0 |

Médias orphelins (extrait) : `img/1200px-Assicurazioni_Generali_logo.svg.avif`, `img/2149728025.jpg`, `img/2_1.png`, `img/3_1.png`, `img/66ab46d0001cff0d067652f4_black_logo_comparateurpro.png`, `img/800px-Image-Hiscox.avif`, `img/Cepahges-1200x630-1.avif`, `img/Embleme-AXA.png` …

## Capture et tracking

| Élément | État |
|---|---|
| Formulaires HTML | 0 |
| Formulaires marqués `data-ubepro-lead` | **0** |
| Champs du formulaire principal | 0 |
| `lead-handler.js` présent / chargé | oui / non |
| `verification-sms.js` présent / chargé | oui / non |
| Ordre des modules correct | non |
| GTM | `GTM-53SH7D7F` |
| `formId` CRM | `ADW_LP_ASSURANCE_CONSULTANTS_SOCIETE_CONSEIL` |
| `formName` | `Assurance-Consultants-Societe-Conseil-Form` |
| Mode transport CRM | `nocors` (réception non confirmable) |
| Source de secours | `LP CONSULTANTS SOCIETE CONSEIL` |
| Version du handler | `2026-10-26-consultants.fonctionnel2-sms1` |

## SEO, indexation et conformité

- `robots.txt` : présent · `sitemap.xml` : présent
- Points d'attention : aucun H1
- Hôtes tiers encore appelés : `www.googletagmanager.com`, `www.ubepro.com`
- Iframes : `https://www.googletagmanager.com/ns.html?id=GTM-53SH7D7F`, `https://www.ubepro.com/assurance-consultant-conseil-v2/`
- Sécurité : 2 iframe(s)

## Documentation présente

- Fichiers Markdown : 6 — RAPPORT-MODIFICATIONS.md rapport-site.md
- Date(s) citée(s) dans les rapports : 2026-10-22, 2026-10-26

## Constats d'expertise

Wrapper iframe **identique au caractère près** à
`assurance-consultant-societe-conseil-v2/index.html` (même `md5`). C'est un doublon pur.
C'est aussi la page que ciblent 7 tests de `tests/lead-reference.test.cjs`, écrits pour une vraie LP
avec formulaire : d'où les **7 échecs** de la suite (`w.smsVerification` indéfini). `lead-handler.js`
et `verification-sms.js` sont présents dans le dossier mais **jamais chargés** par le HTML.

## Actions recommandées

- [ ] Supprimer ou déplacer les 38 médias jamais affichés (gain de poids direct).
- [ ] Créer un H1 unique porteur du mot-clé métier.
- [ ] Supprimer le doublon (une seule page doit survivre).

---

*Fiche générée automatiquement à partir de mesures statiques ; les mentions « code détecté » ne valent pas preuve de fonctionnement en production.*
