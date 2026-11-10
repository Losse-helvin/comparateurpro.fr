# Optimisations prioritaires — livraison du 10 novembre 2026

> Réponse aux trois demandes du métier : défauts de tracking, `formId` courts,
> confort mobile / rapidité / confirmation.
> Tout est appliqué sur les 87 landing pages du parc. Vérifications en bas de page.

---

## 1. Défauts de tracking — `source`, `categorie`, `utm_*`, `ltm_*`

### Le problème
Si l'URL n'apportait aucun paramètre (campagne mal configurée, trafic direct, paramètres perdus
au fil des redirections), le lead partait **sans source ni catégorie**. Côté CRM et côté feuille,
ces leads étaient impossibles à attribuer.

### Ce qui a été livré
Six **constantes de routage** sont désormais toujours présentes dans le payload :

| Champ | Valeur par défaut | Origine |
|---|---|---|
| `source` | `ADW` | brief métier |
| `utm_source` | `ADW` | brief métier |
| `ltm_source` | `ADW` | brief métier |
| `categorie` | code de `categories_codes_sms.xlsx` | propre à chaque LP |
| `utm_category` | idem | |
| `ltm_category` | idem | |

### La règle qui gouverne tout : une vraie campagne reste prioritaire

```
URL avec utm_source=google  →  source = "google"        (la campagne gagne)
URL sans aucun paramètre    →  source = "ADW"           (le défaut comble le trou)
URL avec utm_source seul    →  source = "linkedin",  categorie = code LP  (mixte)
```

Vérifié en exécution réelle (jsdom) sur `assurance-tns` :

| Cas | `source` | `categorie` | `gclid` |
|---|---|---|---|
| Campagne complète (`utm_source=google&categorie=999&gclid=X`) | `google` | `999` | `X` |
| Source seule (`utm_source=linkedin`) | `linkedin` | `462` *(défaut)* | — |
| Aucun paramètre | `ADW` *(défaut)* | `462` *(défaut)* | — |
| Aucun paramètre, **sans consentement** | `ADW` | `462` | — |

### Point de conformité important
Ces six valeurs sont des **constantes de campagne**, pas des données de navigation. Elles sont donc
transmises **même sans consentement analytics** — c'est ce qui garantit qu'un lead reste attribuable.
**En revanche, aucun click ID (`gclid`, `fbclid`…) ni aucune donnée personnelle ne fuit** sans
consentement : vérifié dans le 4ᵉ cas ci-dessus.

> ⚠️ **Décision à valider par le DPO** : considérer des constantes de campagne comme hors du champ
> du consentement est défendable (ce sont des paramètres de routage métier, pas du comportement
> utilisateur), mais cela reste une interprétation. Si le DPO préfère la prudence, une seule ligne
> suffit à conditionner ces constantes au consentement analytics.

---

## 2. `formId` — suppression du préfixe `ADW_LP_`

### Le principe
`ADW` est déjà porté par le champ `source`. Le répéter dans l'identifiant du formulaire était
redondant. Les identifiants sont désormais **courts, en majuscules, sans espace ni underscore inutile**.

### Exemples demandés

| Avant | Après |
|---|---|
| `ADW_LP_ASSURANCE_TNS` | `TNS` |
| `ADW_LP_ASSURANCE_PROTECTION_SOCIALE_COLLECTIVE` | `COLLECTIVE` |
| `ADW_LP_ASSURANCE_AGRICULTEUR` | `IARD_AGRI` |
| `ADW_LP_ASSURANCE_CONSULTANTS_SOCIETE_CONSEIL` | `IARD_CONSEIL` |
| `ADW_LP_SOLUTIONS_AGV_AMR` | `AGV_1` |
| `ADW_LP_SOLUTIONS_INDUSTRIELLES_CLE_EN_MAIN` | `AGV_2` |

### Unicité garantie
Le registre couvre **87 dossiers**, chacun avec un identifiant **strictement unique**.
Les pages en doublon de dossier reçoivent un suffixe (`_2`, `_3`) pour que deux déploiements
identiques ne se confondent pas dans le CRM :

| Dossier | `formId` |
|---|---|
| `agriculteur` | `IARD_AGRI` |
| `assurance-agriculteur` | `IARD_AGRI_2` |
| `assurance/agriculteur` | `IARD_AGRI_3` |
| `assurance-agriculteur-v2` | `IARD_AGRI_V2` |

Le registre complet est dans **`ANALYSE/data/registre-formid.json`** et fait foi.

### ⚠️ Conséquence côté CRM — à faire avant tout déploiement
**Les `formId` sont des clés de routage côté CRM HelloLead.** Changer `ADW_LP_ASSURANCE_TNS` en
`TNS` sans enregistrer le nouveau code dans le CRM **casserait la réception des leads**.
La procédure de bascule est décrite en fin de document.

---

## 3. Mobile, rapidité et confirmation

### 3.1 Ce qui a été mesuré d'abord

| Constat | Mesure |
|---|---|
| Balises `viewport` | **138/138 correctes** (`width=device-width`, zoom non bloqué) |
| Points de rupture CSS | 3 principaux : **991 / 767 / 479 px** — cohérents et déjà présents |
| Boutons trop petits | **838 règles CSS** sous 44 px de hauteur |
| Champs sans étiquette | jusqu'à **14/14** sur `volvo`, **10/38** sur `assurance-tns` |
| Confirmation | le « Merci » est **écrasé au bout de 3 s** par une redirection automatique |

Le socle responsive est donc **sain** — ce n'était pas un problème de balises mais de finitions.

### 3.2 Le module livré : `mobile-ux.js` (9,6 Ko, non bloquant)

Injecté sur les **138 pages**, chargé en `defer`, sans toucher au design ni aux CSS existants.

| Apport | Détail | Bénéfice |
|---|---|---|
| **Zones tactiles 44 px** | agrandit tout bouton/lien d'action trop petit, **uniquement sur écran tactile** | conformité WCAG 2.5.5, fin des clics ratés |
| **Police des champs ≥ 16 px** | sur écran tactile seulement | **supprime le zoom automatique iOS** qui décalait toute la page |
| **Confirmation lisible** | barre défilante « Merci ! Redirection dans 8 s » avec **Continuer / Rester** | le message n'est plus écrasé ; le visiteur garde la main |
| **Étiquetage des champs** | `aria-label` déduit du placeholder ou du nom | lecteurs d'écran, accessibilité |
| **Erreur ramenée à l'écran** | le champ fautif est centré et surligné | l'erreur n'est plus cachée sous le clavier |

Le module ne s'active sur ordinateur que pour l'étiquetage : **le rendu desktop est inchangé**.

### 3.3 Rapidité

Trois corrections sans risque ont été appliquées :

1. **`mobile-ux.js` chargé en `defer`** — n'entre pas en concurrence avec le rendu.
2. **Aucun fichier ajouté au chemin critique** — 9,6 Ko compressés à ~3 Ko en gzip.
3. **Pas de polices ni d'images ajoutées.**

> ⚠️ **Ce qui n'a PAS été fait, volontairement** : les gros chantiers de rapidité
> (`script.js` de 1,45 Mo, conversion des images en WebP, purge des 678 médias orphelins)
> sont documentés dans **`PLAN-OPTIMISATION.md`** idées 4 à 9. Ils demandent une validation
> visuelle page par page que je ne peux pas faire sans navigateur. Les engager à l'aveugle sur
> 138 pages serait imprudent.

---

## 4. Vérifications exécutées

| Contrôle | Résultat |
|---|---|
| `node --check` sur **87 `lead-handler.js` + 138 `mobile-ux.js` + 87 `verification-sms.js`** | **0 échec** |
| Suite de tests `npm test` | **361/368** — soit **exactement les 7 échecs préexistants**, aucune régression |
| Migration idempotente (2ᵉ passage) | **0 fichier modifié** |
| Collisions de `formId` | **0** sur 87 dossiers |
| Comportement des défauts (4 cas d'URL) | conforme au tableau §1 |
| Absence de fuite de click ID sans consentement | vérifié |
| Barre de confirmation | apparaît, bouton « Rester » la referme |

> Les 7 échecs préexistants concernent uniquement `assurance-consultants-societe-conseil`,
> un **wrapper iframe** sans formulaire : les tests le traitent comme une LP. Ce point était
> déjà documenté dans le mémoire d'analyse (§5.2) et n'a rien à voir avec cette livraison.

---

## 5. Procédure de bascule CRM — à respecter impérativement

Les `formId` sont des clés de routage. **L'ordre des opérations n'est pas optionnel.**

1. **Créer les nouveaux `formId` dans le CRM HelloLead** (`TNS`, `COLLECTIVE`, `IARD_AGRI`…),
   en les faisant pointer vers les mêmes files de traitement que les anciens.
2. **Déployer une seule page pilote** (recommandé : `assurance-tns`) sur son domaine.
3. **Envoyer un lead de test réel** et vérifier :
   - réception dans le CRM sous le **nouveau** `formId` ;
   - ligne dans la Google Sheet avec `source = ADW` et `categorie = 462` ;
   - aucun `gclid` sans consentement.
4. **Contrôler 48 h de leads réels** sur la page pilote avant de généraliser.
5. Déployer les autres pages par lots, en gardant l'ancien `formId` en tête de registre
   pour pouvoir revenir en arrière (`git revert` d'un lot = retour immédiat).
6. **Conserver les anciens `formId` actifs côté CRM** au moins un mois : les visiteurs avec une
   page en cache peuvent encore soumettre l'ancien code.

---

## 6. Fichiers modifiés

| Fichier | Nature |
|---|---|
| `*/lead-handler.js` (87) | `formId` court, `categorieCode`, `source=ADW`, constantes de routage |
| `*/mobile-ux.js` (138, nouveau) | module mobile / confirmation |
| `*/index.html` (138) | ajout d'une balise `<script src="mobile-ux.js" defer>` |
| `assurance-estheticiennes-institut-beaute/script.js` + `index.html` | page au moteur autonome, alignée |
| `tests/` (4 fichiers + `pages-adaptees.json` + `registre-formid.json`) | contrat `formId` mis à jour |
| `tools/migrer_formid.py`, `ANALYSE/data/registre-formid.json` | outillage réutilisable |

Pour rejouer la migration : `python3 tools/migrer_formid.py` (simulation) puis `--apply`.
