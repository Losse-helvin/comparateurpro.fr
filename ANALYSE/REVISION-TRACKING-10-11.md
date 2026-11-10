# Révision du 10 novembre 2026 — tracking, GTM, formId, inventaire URL

> **Changement de fond.** Cette révision **annule une partie de la révision précédente** :
> les valeurs par défaut (`ADW`, codes catégories) sont **supprimées** et le tracking passe
> **sans consentement**. Les deux décisions sont incompatibles avec ce qui avait été livré
> la veille — c'est assumé et documenté ici, section par section.

---

## 1. Tracking URL et GTM sans consentement

### Ce qui a changé

| Élément | Avant | Après |
|---|---|---|
| Consent Mode V2 (`gtag('consent','default')`) | 5 signaux `denied` | **5 signaux `granted`** |
| Capture des `utm_*`, `ltm_*` | conditionnée au consentement analytics | **systématique** |
| Click IDs (`gclid`, `fbclid`, `msbraid`…) | conditionnés au consentement marketing | **systématiques** |
| `user_data` (conversions améliorées GTM) | conditionné au marketing | **transmis** |
| `page_url`, `page_referrer` | conditionnés à l'analytics | **transmis** |
| GTM présent dans le HTML | 88 / 138 pages | **135 / 138** (+47 pages équipées) |

Les 3 pages restantes sans GTM sont `mentions-legales`,
`politique-de-confidentialite-donnees-personnelles` et `site-assurances` : des pages de contenu
sans intérêt de mesure. Elles ont en revanche reçu le Consent Mode `granted` si elles en avaient un.

### Ce qui n'a PAS changé

- Le **bandeau cookies reste en place** et continue d'écrire les préférences.
- `gtag('consent','update')` est toujours appelé quand l'utilisateur clique « Accepter »
  ou ajuste ses choix dans la modale : un refus **a posteriori** reste possible.
- Aucun script tiers n'a été ajouté au-delà du conteneur GTM.

### ⚠️ Conséquence juridique — à traiter avant mise en ligne

`Consent Mode: granted` par défaut et collecte sans consentement signifient que **des cookies
de mesure d'audience et de publicité peuvent être déposés avant tout choix de l'utilisateur**.

En France, l'article 82 de la loi Informatique et Libertés et les lignes directrices CNIL
imposent le consentement préalable pour ce type de traceur. **Cette configuration n'est donc pas
conforme au régime français par défaut.** Trois cadrages possibles :

| Option | Statut | Délai |
|---|---|---|
| **A — Exemption de consentement** (mesure d'audience strictement anonyme) | conforme si les conditions CNIL sont respectées (finalité limitée, pas de recoupement, pas de transfert hors UE, IP anonymisée…) | immédiat si le paramétrage GTM/GA4 est conforme |
| **B — Consentement explicite** (état antérieur) | conforme, mais le tracking ne démarre qu'après acceptation | retour arrière possible via `--rollback` |
| **C — Intérêt légitime documenté** | fragile en France pour la publicité | nécessite une analyse juridique écrite |

**Recommandation** : faire trancher par le DPO avant la bascule en production. La configuration
technique actuelle correspond à l'**option A ou C** ; elle est réversible en une commande.

---

## 2. Suppression des valeurs par défaut

Le repli `ADW` + code catégorie de la révision précédente est **retiré intégralement** :

- `TRACKING_DEFAULTS` et `ROUTING_KEYS` supprimés des 87 handlers ;
- `source: 'ADW'` remplacé par `source: ''` dans les 87 configurations ;
- `data.categorie` ne retombe plus jamais sur `CONFIG.categorieCode`.

**Règle désormais en vigueur** : si l'URL n'apporte rien, **le champ reste vide**.

Vérifié en exécution :

| URL | `source` | `categorie` | `gclid` |
|---|---|---|---|
| `?utm_source=google&categorie=999&gclid=ABC` | `google` | `999` | `ABC` |
| *(aucun paramètre)* | `""` | `""` | *(absent)* |

> Le champ `categorieCode` reste présent dans la configuration (il documente la catégorie métier
> de chaque LP et sert à l'inventaire). Il **n'alimente plus** le payload.

---

## 3. Nouveaux `formId` — format `a53023592719547b`

Chaque page possède désormais un identifiant **unique** au format demandé :
**1 lettre + 14 chiffres + 1 lettre**.

```
n51697025492127l   → assurance-tns
a46519725349109k   → assurance-estheticiennes-institut-beaute
k09720745200274b   → LP_reference
```

**146 identifiants, 146 uniques, 100 % conformes au format.** Ils sont générés de façon
**déterministe** (`sha256` du chemin du dossier) : rejouer le script redonne toujours les mêmes
identifiants — pas de risque de dérive entre deux exécutions.

Registre de référence : `ANALYSE/data/registre-formid.json`.

### ⚠️ Bascule CRM — indispensable avant déploiement

Les `formId` sont des **clés de routage HelloLead**. Les remplacer par des identifiants
aléatoires **coupe la réception des leads** tant que les nouveaux codes ne sont pas créés côté CRM.

1. Créer les 87 nouveaux `formId` dans le CRM, pointant vers les mêmes files que les anciens.
2. Déployer **une seule page pilote** — recommandé : `assurance-tns` → `n51697025492127l`.
3. Envoyer un lead réel et vérifier : réception CRM, ligne Sheets, `source` = valeur d'URL.
4. Contrôler 48 h avant de généraliser, puis déployer par lots.
5. Conserver les anciens codes actifs un mois (page en cache).

---

## 4. Inventaire URL ↔ form_id

Fichier livré : **`URL-formid-LP.xls`** (à la racine du dépôt), 2 feuilles :

| Feuille | Contenu |
|---|---|
| **Inventaire** | 146 lignes : URL (canonical), form_id, dossier, poids, titre |
| **Controles** | unicité des identifiants, conformité du format, URL sans canonical |

Également disponibles : `ANALYSE/data/url-formid.csv` (séparateur `;`, UTF-8 BOM, ouvrable
directement dans Excel) et `ANALYSE/data/url-formid.json` (intégration outillée).

**5 pages n'ont pas de canonical** et apparaissent avec la mention
« *(canonical absent — à définir)* » : `LP_reference`, `mentions-legales`,
`politique-de-confidentialite-donnees-personnelles`, `site-assurances`, `vehicules-utilitaires`.
Leur URL définitive doit être confirmée avant publication de l'inventaire.

---

## 5. Tests et vérifications

| Contrôle | Résultat |
|---|---|
| `node --check` sur 312 fichiers JS | **0 échec** |
| `npm test` | **361/368** — uniquement les **7 échecs préexistants** |
| Identifiants uniques / conformes | **146 / 146** |
| Handlers avec `formId` divergent du registre | **0** |
| Handlers conservant un défaut `ADW` | **0** |
| Pages `consent=granted` | **135 / 138** |
| Pages avec GTM | **135 / 138** |

Plusieurs tests affirmaient l'ancien contrat (« pas de `gclid` sans consentement »). Ils ont été
**alignés sur la nouvelle règle**, avec un commentaire explicite à chaque endroit modifié :
`lead-reference`, `lp-restantes-batch`, `nouvelles-lp-simples`, `onze-restantes`.

> Les 7 échecs restants concernent uniquement `assurance-consultants-societe-conseil`,
> wrapper iframe sans formulaire, déjà documenté au §5.2 du mémoire.

---

## 6. Réversibilité

Toute la révision est réversible en une commande :

```sh
python3 tools/revision_tracking.py --rollback
```

Les fichiers originaux sont copiés dans `.revision-backup/` **avant** modification
(exclu de Git par `.gitignore`). Le journal des modifications est dans
`ANALYSE/data/journal-revision-tracking.json`.

En complément, `git revert` du commit de révision restaure l'état antérieur.
