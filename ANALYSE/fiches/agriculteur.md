# Fiche — `agriculteur`

> Famille : **Autres** · Mémoire d'analyse du 2026-11-09 · source : `ANALYSE/scripts/inventaire_exhaustif.py`

## Verdict

🔴 **Formulaire présent mais NON marqué** `data-ubepro-lead="1"` → aucune capture standard.

## Identité

| Champ | Valeur |
|---|---|
| Dossier | `agriculteur` |
| Titre HTML | « Assurance Agriculteur » |
| `lang` | `fr` |
| Canonical | `https://assurance-agriculteur.lp.comparateurpro.fr/` |
| Meta description | 123 caractères |
| H1 | 1 · H2 : 0 |
| Texte du 1er H1 | « Assurance Agricole » |

## Poids et actifs

| Mesure | Valeur |
|---|---|
| Poids total du dossier | **7.05 Mo** (76 fichiers) |
| `index.html` | 33.7 Ko |
| Images | 55 (4.33 Mo) |
| Polices | 7 |
| JS / CSS | 3 / 1 |
| Médias jamais référencés | **6** |
| Références locales cassées | 0 |

Médias orphelins (extrait) : `img/black_logo_comparateurpro-p-1080.png`, `img/black_logo_comparateurpro-p-500.png`, `img/black_logo_comparateurpro-p-800.png`, `img/logo-vectoriel-macif-p-500.jpg`, `img/mercer-logo-p-500.jpg`, `img/vinnytsia-ukraine-november-17-2023-600nw-2389537541-p-500.webp`

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
| `formId` CRM | `ADW_LP_ASSURANCE_AGRICULTEUR` |
| `formName` | `assurance-agriculteur-formly` |
| Mode transport CRM | `nocors` (réception non confirmable) |
| Source de secours | `LP AGRICULTEUR` |
| Version du handler | `2026-10-26-agriculteur.fonctionnel2-sms1` |

## SEO, indexation et conformité

- `robots.txt` : présent · `sitemap.xml` : présent
- Aucun point d'attention SEO détecté par les contrôles automatiques.
- Hôtes tiers encore appelés : `www.googletagmanager.com`
- Iframes : `https://www.googletagmanager.com/ns.html?id=GTM-53SH7D7F`
- Sécurité : 1 iframe(s)

## Documentation présente

- Fichiers Markdown : 6 — RAPPORT-MODIFICATIONS.md rapport-site.md
- Date(s) citée(s) dans les rapports : 2026-10-22, 2026-10-26

## ⚠️ Contradictions documentaires détectées

Le dossier contient de la documentation qui **affirme le contraire de ce que fait le code**. Ne pas s'y fier ; la source de vérité est `index.html` et les fichiers JS.

- La doc affirme que la vérification SMS est exclue, mais `verification-sms.js` est bien chargé par `index.html`.

## Constats d'expertise

Version « fonctionnelle » de l'assurance agriculteur (avec `docs/` complet et `Code.gs`),
distincte de `assurance-agriculteur`, `assurance-agriculteur-v2` et `assurance/agriculteur`.
⚠ **Collision de `formId`** avec `assurance-agriculteur` : `ADW_LP_ASSURANCE_AGRICULTEUR`. Les deux
dossiers enverront des leads impossibles à distinguer côté CRM. `sitemap.xml` présent mais pas de
`style.css` à la racine : vérifier que la feuille est bien chargée.

## Actions recommandées

- [ ] Qualifier le formulaire : marquer `data-ubepro-lead="1"` ou documenter pourquoi il ne doit pas l'être.
- [ ] Supprimer ou déplacer les 6 médias jamais affichés (gain de poids direct).

---

*Fiche générée automatiquement à partir de mesures statiques ; les mentions « code détecté » ne valent pas preuve de fonctionnement en production.*
