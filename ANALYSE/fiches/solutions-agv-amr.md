# Fiche — `solutions-agv-amr`

> Famille : **Flotte / géolocalisation / sécurité** · Mémoire d'analyse du 2026-11-09 · source : `ANALYSE/scripts/inventaire_exhaustif.py`

## Verdict

🔴 **Formulaire présent mais NON marqué** `data-ubepro-lead="1"` → aucune capture standard.

## Identité

| Champ | Valeur |
|---|---|
| Dossier | `solutions-agv-amr` |
| Titre HTML | « Solutions AGV & AMR - marque blanche » |
| `lang` | `fr` |
| Canonical | `https://solutions-agv-amr.lp.ubepro.fr/` |
| Meta description | 119 caractères |
| H1 | 1 · H2 : 18 |
| Texte du 1er H1 | « Automatisez vos flux logistiques et réduisez vos coûts de manutention » |

## Poids et actifs

| Mesure | Valeur |
|---|---|
| Poids total du dossier | **13.53 Mo** (69 fichiers) |
| `index.html` | 37.0 Ko |
| Images | 58 (10.52 Mo) |
| Polices | 0 |
| JS / CSS | 3 / 1 |
| Médias jamais référencés | **19** |
| Références locales cassées | 0 |

Médias orphelins (extrait) : `img/ChatGPT-Image-9-janv.-2026-13_24_27-p-1080.png`, `img/674fff79418f54ebd2611b02_Ubepro-2-bleu-logo-vf-p-500.png`, `img/674fff79418f54ebd2611b02_Ubepro-2-bleu-logo-vf-p-800.png`, `img/ChatGPT-Image-9-janv.-2026-13_24_27-p-500.png`, `img/ChatGPT-Image-9-janv.-2026-13_24_27-p-800.png`, `img/Ubepro-rouge-p-500.png`, `img/Ubepro-rouge-p-800.png`, `img/bouclier-p-500.png` …

## Capture et tracking

| Élément | État |
|---|---|
| Formulaires HTML | 2 |
| Formulaires marqués `data-ubepro-lead` | **0** |
| Champs du formulaire principal | 0 |
| `lead-handler.js` présent / chargé | oui / oui |
| `verification-sms.js` présent / chargé | oui / oui |
| Ordre des modules correct | oui |
| GTM | `GTM-53SH7D7F` |
| GA4 | `G-3XPBT7BZ10` |
| `formId` CRM | `ADW_LP_SOLUTIONS_AGV_AMR` |
| `formName` | `Email-Form-AGV` |
| Mode transport CRM | `nocors` (réception non confirmable) |
| Source de secours | `ADW` |
| Version du handler | `2026-10-26-agvamr.fonctionnel3-sms1` |

## SEO, indexation et conformité

- `robots.txt` : **absent** · `sitemap.xml` : **absent**
- Points d'attention : robots.txt absent · sitemap.xml absent
- Hôtes tiers encore appelés : `solutions-agv-amr.lp.ubepro.fr`, `www.googletagmanager.com`
- Iframes : `https://www.googletagmanager.com/ns.html?id=GTM-53SH7D7F`
- Sécurité : 1 iframe(s)

## Documentation présente

- Fichiers Markdown : 5 — RAPPORT-MODIFICATIONS.md
- Date(s) citée(s) dans les rapports : 2026-10-26

## ⚠️ Contradictions documentaires détectées

Le dossier contient de la documentation qui **affirme le contraire de ce que fait le code**. Ne pas s'y fier ; la source de vérité est `index.html` et les fichiers JS.

- La doc affirme que la vérification SMS est exclue, mais `verification-sms.js` est bien chargé par `index.html`.
- La doc se présente sous un nom de dossier qui n'existe pas (`solutions-agv-amr-pro-v2-adw`).
- La doc parle de `TNS_CONFIG` ; le handler de ce dossier n'en contient pas.

## Constats d'expertise

Dossier technique « solutions AGV/AMR » (robotique industrielle). Deux formulaires HTML
mais **aucun marqué** ; `lead-handler.js` pourtant présent (13,5 Mo de dossier).
C'est la source du schéma Google Sheets « AGV/AMR » (`solution` / `enjeu`) utilisé par toutes les LP
d'assurance : ne pas casser `docs/Code.gs`.

## Actions recommandées

- [ ] Qualifier le formulaire : marquer `data-ubepro-lead="1"` ou documenter pourquoi il ne doit pas l'être.
- [ ] Supprimer ou déplacer les 19 médias jamais affichés (gain de poids direct).
- [ ] Ajouter un `robots.txt`.
- [ ] Ajouter un `sitemap.xml`.

---

*Fiche générée automatiquement à partir de mesures statiques ; les mentions « code détecté » ne valent pas preuve de fonctionnement en production.*
