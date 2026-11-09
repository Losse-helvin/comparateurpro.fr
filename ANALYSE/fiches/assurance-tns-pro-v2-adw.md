# Fiche — `assurance-tns-pro-v2-adw`

> Famille : **Assurance** · Mémoire d'analyse du 2026-11-09 · source : `ANALYSE/scripts/inventaire_exhaustif.py`

## Verdict

✅ **Capture standard complète** (handler + SMS + ordre correct) — reste à valider la réception réelle.

> ⚠️ **Doublon de page** : `index.html` identique à `assurance-professionnelle-tns-v2/assurance-tns-pro-v2-adw`.

## Identité

| Champ | Valeur |
|---|---|
| Dossier | `assurance-tns-pro-v2-adw` |
| Titre HTML | « Assurance TNS Pro V2 - ADW » |
| `lang` | `fr` |
| Canonical | `https://assurance-tns-pro-v2-adw.lp.comparateurpro.fr/` |
| Meta description | 158 caractères |
| H1 | 0 · H2 : 0 |

## Poids et actifs

| Mesure | Valeur |
|---|---|
| Poids total du dossier | **7.63 Mo** (103 fichiers) |
| `index.html` | 39.3 Ko |
| Images | 57 (4.46 Mo) |
| Polices | 29 |
| JS / CSS | 3 / 2 |
| Médias jamais référencés | **8** |
| Références locales cassées | 0 |

Médias orphelins (extrait) : `img/black_logo_comparateurpro-p-1080.png`, `img/black_logo_comparateurpro-p-500.png`, `img/black_logo_comparateurpro-p-800.png`, `img/hero-tns-pro.jpg`, `img/logo-vectoriel-macif-p-500.jpg`, `img/mercer-logo-p-500.jpg`, `img/unnamed_1-p-500.jpg`, `img/vinnytsia-ukraine-november-17-2023-600nw-2389537541-p-500.webp`

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
| `formId` CRM | `ADW_LP_ASSURANCE_TNS_PRO` |
| `formName` | `Assurance-TNS-Pro-Form` |
| Mode transport CRM | `nocors` (réception non confirmable) |
| Source de secours | `LP TNS PRO` |
| Version du handler | `2026-10-27-ubepro.fonctionnel2-sms1` |

## SEO, indexation et conformité

- `robots.txt` : présent · `sitemap.xml` : présent
- Points d'attention : aucun H1

## Documentation présente

- Fichiers Markdown : 7 — RAPPORT-MODIFICATIONS.md RAPPORT-INTEGRATION.md rapport-site.md
- Date(s) citée(s) dans les rapports : 2026-10-22, 2026-10-26

## ⚠️ Contradictions documentaires détectées

Le dossier contient de la documentation qui **affirme le contraire de ce que fait le code**. Ne pas s'y fier ; la source de vérité est `index.html` et les fichiers JS.

- La doc affirme que la vérification SMS est exclue, mais `verification-sms.js` est bien chargé par `index.html`.
- La doc parle de `TNS_CONFIG` ; le handler de ce dossier n'en contient pas.

## Constats d'expertise

Sous-produit de `assurance-tns` (même engine, `formId` distinct).
Contient un fichier de vérification Google Search Console (`google1560e922014e5a8e.html`)
qui n'existe nulle part ailleurs : preuve d'une mise en ligne réelle de ce dossier.

## Actions recommandées

- [ ] Supprimer ou déplacer les 8 médias jamais affichés (gain de poids direct).
- [ ] Créer un H1 unique porteur du mot-clé métier.
- [ ] Supprimer le doublon (une seule page doit survivre).

---

*Fiche générée automatiquement à partir de mesures statiques ; les mentions « code détecté » ne valent pas preuve de fonctionnement en production.*
