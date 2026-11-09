# Fiche — `assurance-tns`

> Famille : **Assurance** · Mémoire d'analyse du 2026-11-09 · source : `ANALYSE/scripts/inventaire_exhaustif.py`

## Verdict

✅ **Capture standard complète** (handler + SMS + ordre correct) — reste à valider la réception réelle.

## Identité

| Champ | Valeur |
|---|---|
| Dossier | `assurance-tns` |
| Titre HTML | « Assurance TNS » |
| `lang` | `fr` |
| Canonical | `https://assurance-tns.lp.comparateurpro.fr/` |
| Meta description | 115 caractères |
| H1 | 9 · H2 : 0 |
| Texte du 1er H1 | « Votre protection sociale mérite un contrat à la hauteur de votre activité. » |

## Poids et actifs

| Mesure | Valeur |
|---|---|
| Poids total du dossier | **6.16 Mo** (89 fichiers) |
| `index.html` | 43.0 Ko |
| Images | 44 (2.98 Mo) |
| Polices | 29 |
| JS / CSS | 3 / 2 |
| Médias jamais référencés | **3** |
| Références locales cassées | 0 |

Médias orphelins (extrait) : `img/logo-vectoriel-macif-p-500.jpg`, `img/mercer-logo-p-500.jpg`, `img/vinnytsia-ukraine-november-17-2023-600nw-2389537541-p-500.webp`

## Capture et tracking

| Élément | État |
|---|---|
| Formulaires HTML | 2 |
| Formulaires marqués `data-ubepro-lead` | **1** |
| Champs du formulaire principal | 56 |
| `lead-handler.js` présent / chargé | oui / oui |
| `verification-sms.js` présent / chargé | oui / oui |
| Ordre des modules correct | oui |
| GTM | `GTM-53SH7D7F` |
| `formId` CRM | `ADW_LP_ASSURANCE_TNS` |
| `formName` | `Assurance-TNS-Pro-Form` |
| Mode transport CRM | `nocors` (réception non confirmable) |
| Source de secours | `LP TNS` |
| Version du handler | `2026-10-27-ubepro.fonctionnel2-sms1` |

## SEO, indexation et conformité

- `robots.txt` : présent · `sitemap.xml` : présent
- Points d'attention : 9 H1

## Documentation présente

- Fichiers Markdown : 7 — RAPPORT-MODIFICATIONS.md RAPPORT-INTEGRATION.md rapport-site.md
- Date(s) citée(s) dans les rapports : 2026-10-22, 2026-10-26

## ⚠️ Contradictions documentaires détectées

Le dossier contient de la documentation qui **affirme le contraire de ce que fait le code**. Ne pas s'y fier ; la source de vérité est `index.html` et les fichiers JS.

- La doc affirme que la vérification SMS est exclue, mais `verification-sms.js` est bien chargé par `index.html`.
- La doc affirme un H1 unique ; le HTML en contient 9.
- La doc parle de `TNS_CONFIG` ; le handler de ce dossier n'en contient pas.

## Constats d'expertise

Bonne élève documentaire : `RAPPORT-MODIFICATIONS.md` (5,2 Ko) + 4 documents dans `docs/`
(analyse fonctionnelle, configuration CRM/Sheets/GTM, vérification SMS, embed Webflow) + `Code.gs`.
C'est le **patron de documentation** à répliquer sur les 137 autres dossiers.
Défaut résiduel : 9 balises `<h1>` dans le HTML (héritage Webflow, cf. rapport).

## Actions recommandées

- [ ] Ramener les 9 H1 à un seul (sans changer le design, via classes identiques).

---

*Fiche générée automatiquement à partir de mesures statiques ; les mentions « code détecté » ne valent pas preuve de fonctionnement en production.*
