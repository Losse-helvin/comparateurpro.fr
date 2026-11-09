# Journal de travail — analyse du dépôt `comparateurpro.fr`

> Chronologie de ce qui a été fait, pourquoi, et ce qui a été écarté. Ce journal sert à
> **reprendre le travail sans refaire l'analyse** et à distinguer les faits mesurés des hypothèses.

**Session du 9 novembre 2026** — branche `arena/859fe993-comparateurpro-fr`
Base : commit `1ee939e` (« Add files via upload »), unique commit du dépôt.

---

## 1. Déroulé chronologique

| Étape | Action | Résultat |
|---|---|---|
| 1 | Exploration de la racine, du log Git et de l'arborescence | 143 dossiers de premier niveau, 11 537 fichiers, 1,1 Go, **1 seul commit** |
| 2 | Lecture de `ordre-sites.txt` | 131 dossiers listés — c'est l'inventaire métier implicite |
| 3 | Lecture des 3 scripts de `tools/` | audit statique existant (bonne base, réutilisée) |
| 4 | Lecture de `lead-handler.js` et `verification-sms.js` | compréhension du contrat de capture |
| 5 | Lecture de 6 `RAPPORT-MODIFICATIONS.md` + des 6 `docs/` | découverte de la documentation copiée-collée |
| 6 | Écriture de `ANALYSE/scripts/inventaire_exhaustif.py` | mesure des 146 pages |
| 7 | Corrections du script (H1 vides, `lang`, identifiants imbriqués) | 3 itérations nécessaires |
| 8 | Analyse de redondance par MD5 sur 11 537 fichiers | 486 groupes, 833 Mo récupérables |
| 9 | `node --check` sur 296 fichiers JS | 0 échec |
| 10 | `npm ci` + `npm test` (368 tests) | 361 OK, 7 échecs, tous sur un seul site |
| 11 | `unittest` Python | 12/12 avec `PYTHONPATH=.` ; 1 erreur sans |
| 12 | Vérification croisée doc ↔ code | 6 dossiers avec contradictions |
| 13 | Écriture des 146 fiches + de ce mémoire + registre | livrables |
| 14 | Écriture de `audit_poids.py` | outil de diagnostic réutilisable, lecture seule |

---

## 2. Faits mesurés (reproductibles)

Tout ce qui suit est vérifiable par une commande documentée dans `ANALYSE/README.md`.

- 146 `index.html` (138 racine + 8 imbriqués : 7 sous `assurance/` + 1 sous `assurance-professionnelle-tns-v2/`).
- 84 pages au statut A, 37 au statut C, 23 au statut D, 2 au statut B.
- 96 pages avec GTM. Deux conteneurs seulement dans tout le parc : `GTM-53SH7D7F` (81 pages),
  `GTM-WMVZJKS` (15 pages).
- 87 dossiers avec `lead-handler.js`, 86 réellement chargés (le 87ᵉ : wrapper iframe).
- 77 copies identiques de `lead-handler.js`, 62 de `verification-sms.js`.
- Un seul Google Sheet : `script.google.com/…/AKfycbwr…/exec` sur les 87 pages.
- `leadApiMode = 'nocors'` sur **100 %** des handlers.
- 81 pages en `lang="en"`, 129 sans H1, 4 avec plusieurs H1 (max 17).
- 132 domaines canoniques distincts.
- 678 médias orphelins, **0** référence locale cassée.
- 8 paires de pages identiques à l'octet, 833 Mo récupérables par déduplication.

## 3. Hypothèses et limites — à lire avant de citer ce mémoire

| Sujet | Statut |
|---|---|
| « `lp2site.py` est l'outil de conversion » | **Fait** : cité par les 141 `rapport-site.md`. **Hypothèse** : son absence du dépôt est un oubli ; il peut aussi avoir été volontairement externalisé. |
| « `assurance/` est l'ancienne copie » | **Hypothèse** raisonnée : ses `RAPPORT-INTEGRATION.md` sont plus courts que les `RAPPORT-MODIFICATIONS.md` de la racine, et ces dossiers sont absents de `ordre-sites.txt`. Non confirmée par l'historique Git (un seul commit). |
| « Les 37 pages du statut C perdent des leads » | **Hypothèse forte mais non prouvée** : le handler ne trouve pas de formulaire marqué, donc `if (!form) return;` s'exécute. Il faudrait vérifier page par page qu'aucun autre mécanisme (ancien gestionnaire dans `script.js`, comme sur `solutions-agv-amr`) n'assure la capture. |
| « Le CORS SMS est un risque » | **Fait de code** (appel navigateur direct). **Non testé** : je n'ai pas exécuté d'appel réseau réel vers HelloLead — l'API peut autoriser toutes les origines. |
| « Le CRM ne confirme pas la réception » | ~~Risque~~ → **LEVÉ le 9 nov. 2026** : le métier a confirmé qu'un lead présent dans la feuille Google est aussi reçu par le CRM. Le `nocors` reste une limite *technique* (aucun accusé côté navigateur), mais la chaîne fonctionne en production. Le risque résiduel est le cas dégradé : Sheets OK / CRM KO. |
| Contenu des pages, qualité visuelle | **Non évalué** : je n'ai pas ouvert les pages dans un navigateur. Un audit visuel reste à faire. |

### 3 bis. Validation en production (9 novembre 2026)

Le métier a fourni une feuille Google Sheets de suivi des leads et confirmé la règle suivante :

> **Tout ce qui apparaît dans cette feuille est également reçu par le CRM.**

Ce que cela change dans l'analyse :

| Point | Avant | Après |
|---|---|---|
| Chaîne de capture de bout en bout | incertaine | **validée en production** ✅ |
| CORS de l'API SMS | risque non testé | **fonctionne** sur les domaines en service ✅ |
| CORS de l'Apps Script Sheets | risque non testé | **fonctionne** ✅ |
| Routage CRM par `formId` | non prouvé | **opérationnel** ✅ |
| Risque C5 (CRM muet) | majeur | **résiduel** : seulement le cas Sheets OK / CRM KO |
| Risque C4 (CORS SMS) | majeur | **résiduel** : seulement lors d'un nouveau domaine |

**Ce que cette validation ne dit pas** (à ne pas surinterpréter) :
- elle ne dit **pas** que les 37 pages du statut C envoient des leads — elles envoient peut-être
  par un mécanisme historique, ou pas du tout. Il faut vérifier la **présence des pages** dans la
  feuille, pas seulement l'existence de la feuille ;
- elle ne dit **pas** que le taux de conversion est bon, seulement que la plomberie fonctionne ;
- elle ne dit **pas** qu'un SMS est délivré à tous les opérateurs ni sur tous les domaines
  nouvellement déployés.

**Question à trancher, désormais la plus importante** : la feuille est-elle **complète** ? Si des
leads arrivent dans le CRM sans figurer dans la feuille, c'est le signe d'un `formId` non routé
vers le script Sheets. Comparer le volume des deux sources sur une semaine est le meilleur
diagnostic possible — et c'est faisable immédiatement, sans modifier une ligne de code.

**Ce que cette analyse ne peut pas dire :**
- si un lead arrive réellement dans le CRM aujourd'hui ; *(levé le 9 nov. 2026 — voir ci-dessus)*
- si un SMS est réellement délivré sur un domaine donné ;
- si les événements GTM sont réellement reçus dans GA4 / Google Ads ;
- si les pages sont visuellement conformes à l'intention métier.

Ces quatre points exigent des tests en production avec un vrai numéro de téléphone et un
accès au CRM. **C'est le premier chantier à ouvrir après ce mémoire.**

## 4. Décisions prises pendant l'analyse

| # | Décision | Raison |
|---|---|---|
| A-01 | Ne **rien supprimer** dans le dépôt | le mandat était l'analyse, pas la modification. Les recommandations sont dans `REGISTRE-ACTIONS.md`. |
| A-02 | Écrire les livrables dans `ANALYSE/` | isoler le travail d'analyse du parc de pages, sans toucher aux dossiers de production. |
| A-03 | Générer une fiche par page plutôt qu'un tableau unique | une fiche est lisible, citable et actionnable ; le tableau existe en CSV à côté. |
| A-04 | Scripts Python sans dépendance externe | le dépôt n'a pas de `requirements.txt` ; rester en bibliothèque standard garantit que ça tourne partout. |
| A-05 | Ne pas « corriger » les 7 tests en échec | c'est un arbitrage produit (wrapper iframe ou vraie LP ?), pas un bug. Documenté, pas tranché. |
| A-06 | Mesurer la redondance par MD5 sur l'intégralité des fichiers | seule façon honnête de dire « 833 Mo » plutôt que « ça paraît lourd ». |
| A-07 | Vérifier la doc contre le code | sans cette étape, le mémoire aurait répété des affirmations fausses (« SMS exclu »). |

## 5. Erreurs commises et corrigées (pour ne pas les refaire)

1. **Parseur HTML** : les H1 sortaient vides et le `lang` faux, parce que le buffer de capture
   était réinitialisé à chaque balise ouvrante. Corrigé (réinitialisation limitée à `h1`/`title`).
   3 itérations avant d'obtenir `9 H1` sur `assurance-tns` au lieu de `0`.
2. **Doublons faux** : les 7 dossiers de `assurance/` étaient comptés comme « pages sans doublon »
   parce que l'identifiant de page était le **nom du dossier** (`agriculteur` ≠ `assurance/agriculteur`).
   Corrigé en utilisant le chemin complet. C'est ce qui a révélé les 8 paires de doublons.
3. **Fiches écrasées** : avec la clé `nom_de_dossier`, `agriculteur` et `assurance/agriculteur`
   s'écrivaient dans le même fichier. Corrigé en utilisant `__` comme séparateur de chemin.
4. **Édition de mémoire destructrice** : un remplacement de texte a fusionné deux sections du
   mémoire (§6.5 et §6.6). Détecté par relecture, corrigé. **Leçon : relire après chaque édition
   structurelle d'un long Markdown.**

## 6. Ce qu'il faudrait faire ensuite (ordre suggéré)

1. Ouvrir les points 3 et 4 du §3 de ce journal avec l'équipe métier : **est-ce qu'un lead arrive
   vraiment aujourd'hui ?** Une demi-journée de test en production vaut mieux que dix analyses.
2. Récupérer `lp2site.py`.
3. Arbitrer le sort de `assurance/` et de `… - Copie`.
4. Démarrer l'étape 1 du plan d'action du mémoire (purge, faible risque).
5. Faire un audit visuel (Lighthouse) sur 5 pages représentatives — non couvert ici.
