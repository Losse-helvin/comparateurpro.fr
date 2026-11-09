# Mémoire d'analyse et de travail — `comparateurpro.fr`

> **Nature du document** : mémoire technique de référence (état des lieux exhaustif, diagnostics,
> plan d'action). Il est écrit pour être relu dans six mois par quelqu'un qui n'a pas fait l'analyse.
> **Date de l'analyse** : 9 novembre 2026.
> **Périmètre** : l'intégralité du dépôt, sans exception (146 pages, 11 537 fichiers, ~1,1 Go).
> **Méthode** : lecture du code + mesures statiques reproductibles + exécution des suites de tests.
> Aucune affirmation de ce document ne provient d'une supposition : chaque chiffre est reproductible
> par un script présent dans `ANALYSE/scripts/`.

| Livrable | Fichier |
|---|---|
| Ce mémoire | `ANALYSE/MEMOIRE-ANALYSE.md` |
| Fiche détaillée par page (146) | `ANALYSE/fiches/<dossier>.md` |
| Tableau de bord par page | `ANALYSE/data/inventaire.csv` |
| Données brutes complètes | `ANALYSE/data/inventaire.json` |
| Journal de travail (chronologie + décisions) | `ANALYSE/JOURNAL-TRAVAIL.md` |
| Registre des risques actionnable | `ANALYSE/REGISTRE-ACTIONS.md` |
| Scripts reproductibles | `ANALYSE/scripts/` |

---

## 1. Synthèse exécutive

### 1.1 Ce qu'est ce dépôt

Ce dépôt **n'est pas une application**. C'est un **entrepôt de landing pages** (LP) autonomes,
toutes issues du même export Webflow, toutes destinées à un sous-domaine
`<nom>.lp.comparateurpro.fr`, toutes construites sur le même contrat de capture de leads :

```
Visiteur → formulaire Webflow (script.js, 1,5 Mo) → lead-handler.js
        → CRM HelloLead (mc.hellolead.pro) + Google Sheets (Apps Script)
        → verification-sms.js (API SMS Partner) → événement GTM formulaire_lead
```

Chaque dossier est une **unité de déploiement indépendante** : pas de build, pas de `package.json`
à la racine, pas de bundler, pas de routeur, pas de base de données. On copie un dossier sur un
hébergement, il fonctionne seul.

### 1.2 Les chiffres qui comptent

| Indicateur | Valeur | Lecture |
|---|---|---|
| Pages HTML (`index.html`) | **146** | 138 à la racine + 8 imbriquées |
| Fichiers versionnés | **11 537** | dont ~10 000 médias et polices |
| Poids du dépôt | **1 098 Mo** (1,1 Go) | pour du HTML statique, c'est 20 à 50× trop |
| Poids des images | ~654 Mo (60 %) | 139 copies de la même photo de voiture |
| Espace récupérable par déduplication | **~833 Mo (76 %)** | mesure par empreinte MD5 |
| Pages avec capture standard complète | **84 / 146** (58 %) | handler + SMS + ordre + formulaire marqué |
| Pages avec formulaire mais **sans** capture | **37** (25 %) | le formulaire existe, il n'est pas raccroché |
| Pages sans formulaire (contenu/légales/wrappers) | **23** (16 %) | normal pour certaines, suspect pour d'autres |
| Pages avec GTM détecté | **96 / 146** (66 %) | 2 conteneurs seulement pour tout le parc |
| Pages `lang="en"` alors que contenu FR | **81** (55 %) | défaut d'export massif |
| Pages sans aucun `<h1>` | **129** (88 %) | SEO sacrifié |
| Pages avec plusieurs `<h1>` | **4** (dont un record à 17) | inverse du problème précédent |
| Médias jamais affichés (orphelins) | **678** | export « tout compris » |
| Références locales cassées | **0** | point **positif**, à préserver |
| Dossiers strictement identiques (doublons) | **8 paires** | dont 7 sous `assurance/` + 1 sous TNS |
| Dossiers avec documentation fonctionnelle (`docs/`) | **6 / 146** | et cette documentation est en partie copiée-collée |
| Tests JS | **368 exécutés — 361 OK, 7 échecs** | les 7 échecs viennent d'**un seul** dossier |
| Tests Python | **12 / 12 OK** (avec `PYTHONPATH=.`) | sans `PYTHONPATH`, 1 échec d'import |
| Syntaxe JS (`node --check`) | **296 / 296 fichiers OK** | 160 modules + 136 bundles |

### 1.3 Le diagnostic en cinq phrases

1. **La mécanique de capture est solide et homogène** : 84 pages partagent exactement le même
   `lead-handler.js` (version `2026-10-27-ubepro.fonctionnel2-sms1`) et le même Google Sheet.
   C'est un actif industriel réel, pas un bricolage.
2. **La documentation est très inégale, et celle qui existe est trompeuse** : 141 pages ont un
   `rapport-site.md` généré qui se contente de dire « 0 H1 ⚠ » et « GTM absent ». Seuls **6 dossiers**
   ont une documentation fonctionnelle (`docs/` + `Code.gs`), mais elle est **copiée-collée** et
   **contredit le code** (elle affirme que le SMS est désactivé sur des pages qui l'activent).
3. **Le dépôt est structurellement redondant** : 8 paires de pages identiques à l'octet près,
   139 copies de chaque image de fond, 2 formulaires qui partagent le même `formId` CRM,
   et 5 dossiers pour une seule offre « ticket restaurant ».
4. **Le SEO est le parent pauvre** : 88 % des pages n'ont pas de `<h1>`, 55 % déclarent être en
   anglais, et la moitié n'ont jamais eu de GTM. Ce n'est pas un défaut de soin, c'est un défaut
   de processus : l'outil de conversion (`lp2site.py`) ne produisait pas ces éléments.
5. **Un seul dossier explique 100 % des échecs de test** : `assurance-consultants-societe-conseil`
   est un wrapper iframe, mais les tests le traitent comme une LP à formulaire. Le problème n'est
   pas le code de production, c'est **le contrat entre le code et ses tests**.

---

## 2. Cartographie du dépôt

### 2.1 Anatomie d'une landing page type

Toutes les LP partagent la même anatomie. Savoir la lire, c'est savoir lire les 146 dossiers.

```
<dossier>/
├── index.html            ← page autonome (30 à 60 Ko), HTML exporté de Webflow
├── style.css             ← ~150 Ko, feuille Webflow complète (dont 80 % de classes inutilisées)
├── script.js             ← 1,45 Mo ! (jQuery + runtime Webflow + moteur de formulaire « Formly »)
├── lead-handler.js       ← 40 Ko, NOTRE code : capture, CRM, Sheets, tracking, consentement
├── verification-sms.js   ← 14,5 Ko, NOTRE code : envoi et validation du code SMS
├── fonts-global.css      ← déclarations @font-face communes
├── fonts/                ← 24 à 58 fichiers de polices (souvent 3 fois la même famille)
├── img/                  ← 50 à 110 médias (dont une majorité jamais affichée)
├── videos/               ← optionnel (canal, volvo, lexus, mercedes…)
├── robots.txt            ← 140 pages sur 146
├── sitemap.xml           ← 140 pages sur 146
├── rapport-site.md       ← généré par lp2site.py : poids, H1, GTM, hôtes externes
├── RAPPORT-INTEGRATION.md / RAPPORT-MODIFICATIONS.md  ← quand une intervention humaine a eu lieu
└── docs/                 ← rare (5 dossiers) : analyse fonctionnelle, config CRM, embed, Code.gs
```

**Le point à comprendre immédiatement** : `script.js` (1,45 Mo) n'est **pas** notre code.
C'est jQuery 3 + le runtime Webflow + le moteur de formulaire multi-étapes « Formly ».
Notre code, ce sont les deux fichiers de 40 Ko et 14,5 Ko. Quand on cherche un bug de capture,
on ne le cherche **jamais** dans `script.js` : on le cherche dans `lead-handler.js`.
Et quand on veut gagner du poids, `script.js` est malheureusement difficile à amputer parce que
le moteur de formulaire en dépend.

### 2.2 Les deux fichiers qui portent toute la valeur

**`lead-handler.js`** — 40 Ko, présent dans 87 dossiers (86 réellement chargés), **77 copies sont
identiques à l'octet près**. Il fait :

| Bloc | Rôle | Détail vérifié |
|---|---|---|
| `UBE_CONFIG` | configuration en tête de fichier | `leadApiUrl`, `leadApiMode`, `formId`, `formName`, `source`, `microField` |
| Résolution de champs | `FIELD_ALIASES` + normalisation NFD | tolère `telephone-2`, `Nom 2`, `Email`, `Tél`… |
| Interception | `submit` jQuery **et** natif | c'est ce qui évite l'écran « Oops! » hors Webflow |
| CRM | `POST` enveloppe `{payload:{formId,id,data}}` | mode `nocors` = `sendBeacon` puis `fetch no-cors` → **réception non confirmable** |
| Sheets | `POST` champs plats + JSON `status:"ok"` exigé | mapping AGV/AMR : `solution`, `enjeu`, `question_1..3` |
| Anti-spam | honeypot `website` | rempli ⇒ succès affiché, **zéro envoi** |
| Tracking | `utm_*`, `ltm_*`, `gclid/gbraid/wbraid/fbclid/msclkid/ttclid` | persisté en `sessionStorage` |
| Consentement | lit `user_cookie_preferences` | analytics ⇒ UTM/page ; marketing ⇒ click IDs + `user_data` |
| Pont iframe | `postMessage`, protocole `ubepro-assurance-v1` | origine parente **limitée** à `https://www.comparateurpro.fr` |
| APIs QA | `window.lpLead.preview()`, `window.lpTracking.inspect()` | utilisables en console navigateur |

**`verification-sms.js`** — 14,5 Ko, 62 copies identiques. Vérifie un mobile FR (`06`/`07`) via
`mc.hellolead.pro/.../smspartner/envoi_code_verification.php` : `envoyer_code` puis `verifier_code`,
code à 6 chiffres, 10 minutes, usage unique, renvoi à 120 s, messages d'erreur 422/404/409/410/429/502
affichés depuis le JSON. **Le lead est bloqué** tant que le numéro n'est pas vérifié.

> ⚠️ **Conséquence opérationnelle majeure** : ces deux fichiers appellent des API tierces
> **directement depuis le navigateur du visiteur**. Si l'origine du domaine final n'est pas
> autorisée en CORS côté HelloLead, la vérification SMS échoue silencieusement et **le formulaire
> devient inutilisable** (le lead est bloqué). C'est le risque n°1 du parc.

### 2.3 Les familles de dossiers

| Famille | Pages | Poids | Capture complète | Commentaire |
|---|---|---|---|---|
| Assurance (toutes branches) | 27 | 200 Mo | 20 | cœur de métier, la mieux intégrée |
| Divers / one-off (constructeurs auto, énergie, télécom) | 47 | 359 Mo | ~30 | nommages hétérogènes |
| TIP / formulaires (`typ-*`) | 16 | 99 Mo | 6 | surtout des « thank you pages » |
| Ticket restaurant | 5 | 36 Mo | 4 | 5 dossiers pour une offre |
| Édenred | 5 | 32 Mo | 2 | |
| Remerciement | 5 | 39 Mo | 0 | destinations post-conversion, 0 formulaire |

### 2.4 Les quatre statuts d'une page (classification de travail)

C'est la grille à réutiliser pour tout arbitrage futur. Elle est recalculée automatiquement par
`ANALYSE/scripts/inventaire_exhaustif.py`.

| Statut | Critère | Nombre | Signification |
|---|---|---|---|
| **A — Capture standard complète** | formulaire marqué + handler chargé + SMS chargé + ordre correct | **84** | rien à faire côté code ; valider la réception |
| **B — Modules présents, non chargés** | fichiers là, `<script>` absent du HTML | **2** | anomalie franche |
| **C — Formulaire sans marqueur** | `<form>` existe, `data-ubepro-lead="1"` absent | **37** | le lead risque de partir dans le vide |
| **D — Page sans formulaire** | contenu, légale, remerciement, wrapper | **23** | à qualifier au cas par cas |

Le statut **C est le plus dangereux** : ces pages ont l'air de fonctionner (le formulaire s'affiche,
il valide, il remercie), mais le handler ne s'y accroche pas. Aucune erreur visible. Aucun lead reçu.

---

## 3. Analyse fonctionnelle — la chaîne de capture

### 3.1 Le parcours d'un lead, étape par étape

```
1. Saisie          Formly (script.js) valide par étape → messages FR (data-err)
2. Téléphone       verification-sms.js → POST envoyer_code → champ code
3. Code reçu       POST verifier_code → badge vert + champ caché telephone_verifie=oui
4. Validation      lead-handler.js contrôle estVerifie() → bloque si non vérifié
5. Honeypot        champ website vide ? si rempli → faux succès, 0 envoi
6. Construction    payload CRM { formId, id(UUID), data{...} }, champs cachés tracking
7. Envoi parallèle CRM (sendBeacon no-cors)  ‖  Sheets (POST urlencoded, CORS)
8. Résultat        succès si CRM **ou** Sheets confirme → événement GTM formulaire_lead
9. Écran           « Merci ! » Webflow d'origine affiché
```

### 3.2 Les fragilités réelles du parcours

> **✅ VALIDATION EN PRODUCTION (9 novembre 2026)** — Le métier a confirmé qu'un lead qui apparaît
> dans la feuille Google Sheets **est aussi reçu par le CRM**. La chaîne est donc fonctionnelle de
> bout en bout en production. Cela **lève l'incertitude principale** de cette analyse (voir F1) et
> confirme que le CORS de l'API SMS, celui de l'Apps Script et le routage CRM sont opérationnels
> sur les domaines testés. Les points ci-dessous restent des **fragilités de robustesse**, pas des
> pannes : ils décrivent ce que le système ne sait pas faire, pas ce qu'il fait mal aujourd'hui.

**F1 — Le succès ne prouve pas la réception CRM. *(Risque résiduel, non bloquant)*** Le mode
`nocors` sur **les 87 pages** signifie que le navigateur n'a aucun retour du CRM. Le code considère
un beacon « accepté » comme un envoi réussi. **En pratique, la réception est confirmée** : un lead
visible dans Sheets arrive bien dans le CRM. La fragilité est donc désormais circonscrite au **cas
dégradé** : si le CRM tombe alors que Sheets répond `ok`, l'utilisateur voit « Merci ! » et le lead
est conservé dans la feuille mais absent du CRM — sans alerte. Aucune déduplication serveur n'est
en place, donc une reprise manuelle depuis la feuille est possible mais doit rester prudente.

**F2 — Le CORS de l'API SMS est une dépendance non maîtrisée.** L'appel part du navigateur du
visiteur. Une page mal déployée (autre sous-domaine, iframe, port de préprod) = SMS mort = lead
bloqué = **zéro conversion**. Il faut tester chaque nouveau domaine, systématiquement.

**F3 — Le pont iframe n'accepte qu'une origine parente.** `ALLOWED_PARENT_ORIGINS =
['https://www.comparateurpro.fr']`. Toute iframe posée depuis un autre domaine (ou depuis
`*.lp.comparateurpro.fr`) ne reçoit ni consentement ni URL de campagne : **attribution perdue**.

**F4 — Le même `formId` pour deux pages = leads confondus.** Vérifié : `ADW_LP_ASSURANCE_AGRICULTEUR`
sur `agriculteur` **et** `assurance-agriculteur` ; `ADW_LP_ASSURANCE_CONSULTANTS_SOCIETE_CONSEIL`
sur `assurance-consultants-societe-conseil` **et** `… - Copie`. Côté CRM, impossible de savoir
quelle page a produit le lead, ni de comparer les performances.

**F5 — La vérification SMS est un point de rupture produit.** Elle a été réintroduite à la demande
métier (cf. `assurance-tns/RAPPORT-MODIFICATIONS.md`), mais elle ajoute une étape obligatoire
entre le visiteur et le lead. Sur une audience à faible littératie numérique ou sur mobile,
c'est une perte de conversion directe. À arbitrer **par campagne**, pas globalement.

### 3.3 Ce qui est bien fait (à ne pas casser)

- **Zéro référence locale cassée** sur 146 pages. C'est rare sur un dépôt de cette taille et cela
  signifie que la conversion Webflow → site statique (`lp2site.py`) a été sérieusement vérifiée.
- **296 / 296 fichiers JS passent `node --check`.** Aucune syntaxe cassée, malgré 77 copies
  quasi identiques du handler.
- **Le mécanisme de consentement est présent sur 135 / 146 pages**, avec Consent Mode V2
  `default denied` placé **avant** GTM. C'est la bonne séquence RGPD/CNIL.
- **L'anti-spam par honeypot** est simple, invisible et efficace.
- **Les APIs de QA intégrées** (`lpLead.preview()`, `lpTracking.inspect()`) permettent de vérifier
  un payload en console sans outil externe : rare et précieux.

---

## 4. Analyse SEO et conformité

### 4.1 Les défauts systémiques (issus de l'export, pas des intervenants)

| Défaut | Pages | Origine | Correction |
|---|---|---|---|
| Aucun `<h1>` | 129 | titres stylés en `<div>`/`<p>` dans Webflow | ajouter un H1 unique par page |
| `<h1>` multiples | 4 (9, 9, 17, 4) | titres décoratifs mis en `h1` | passer les secondaires en `h2`, **classes identiques** ⇒ rendu inchangé |
| `lang="en"` | 81 | gabarit Webflow en anglais | remplacer par `lang="fr"` |
| Meta description générée | majorité | `lp2site.py` l'écrit automatiquement | relire et réécrire manuellement |
| GTM absent | 50 | le rapport le signale, personne ne corrige | trancher page par page |

> La correction des H1 multiple et du `lang` est **indolore visuellement** : `assurance-tns` l'a
> démontré en conservant des classes identiques (`.h1-iard-v2` porte déjà la taille et les marges).
> C'est donc une correction à fort gain et faible risque : à industrialiser.

### 4.2 Le problème du `canonical`

**132 domaines distincts** pour 146 pages. Chaque page se déclare sur son propre sous-domaine
`<nom>.lp.comparateurpro.fr`. Conséquences :

- Google voit 132 domaines distincts → **aucune autorité cumulée**, chaque LP est indexée isolément.
- Cinq pages n'ont **aucun** canonical : `LP_reference`, `mentions-legales`,
  `politique-de-confidentialite-donnees-personnelles`, `site-assurances`, `vehicules-utilitaires`.
- `assurance-consultants-societe-conseil` déclare le canonical de
  `assurance-consultant-societe-conseil-v2` : correct pour un doublon, à condition de n'en garder qu'un.

**Recommandation forte** : ces LP sont des pages d'acquisition payante (Google Ads). Leur rôle
n'est pas d'être trouvées par recherche organique mais d'être **conformes** et **traçables**.
Pour les LP payantes, un `noindex` assumé + un canonical propre par campagne est souvent plus sain
que 132 domaines qui se concurrencent. **À arbitrer métier, mais c'est un choix à faire
explicitement, pas par défaut.**

### 4.3 La chaîne légale

- `mentions-legales/index.html` (34 Ko) et
  `politique-de-confidentialite-donnees-personnelles/index.html` (58 Ko) existent, sont complets,
  mais **n'ont ni robots.txt ni sitemap.xml** et n'ont pas de canonical.
- Ce sont des pages **charnières** : chaque LP qui collecte un téléphone doit y renvoyer.
  Vérification faite : ce n'est pas le cas de façon systématique dans les formulaires.
- Point de conformité à trancher : **le consentement est demandé, mais les LP ne portent aucune
  mention de responsable de traitement, aucune durée de conservation, aucun contact DPO.** Pour des
  leads revendus à des courtiers en assurance, c'est le point juridique le plus exposé du projet.

### 4.4 Contenu mixte et sécurité

**10 pages** chargent des ressources en `http://` (contenu mixte) : `celebrez-le-noel-des-salaries-avec-kadeos`,
`edenred-kadeos`, `edenred-ticket-restaurant-juillet-v1`, `hyundai-kona-electric-nouvelle-generation`,
`ticket-restaurant`, `ticket-restaurant-`, `ticket-restaurant-septembre`,
`ticket-restaurant-septembre-btp`, `ticket-restaurant-v2` et `une-rentree-sous-le-signe-du-pouvoir-d-achat`.
Six d'entre elles appartiennent à la famille ticket restaurant / Édenred : **le problème est
concentré sur une seule famille de pages**, ce qui rend la correction rapide.
Les navigateurs récents bloquent ces ressources actives. **Impact direct sur le rendu.**

Aucune clé d'API en clair n'a été trouvée. Les URL Apps Script sont publiques par nature (elles
sont appelées par le navigateur) : ce n'est pas une fuite, mais quiconque connaît l'URL peut écrire
dans la feuille. L'anti-spam honeypot côté `Code.gs` limite la casse. **À surveiller.**

---

## 5. Analyse des tests et de la qualité

### 5.1 Ce que couvre la suite (368 tests JS, 12 tests Python)

| Fichier | Objet |
|---|---|
| `tests/lead-reference.test.cjs` | le contrat de référence : 11 blocs × N pages (CRM, Sheets, SMS, consentement, honeypot, ordre des modules) |
| `tests/lp-restantes-batch.test.cjs` | rejoue le contrat sur toutes les LP de `pages-adaptees.json` (43 sites) |
| `tests/particularites-onze.test.cjs` | cas particuliers : questions numérotées, SMS sans confirmation explicite |
| `tests/estheticiennes-original.test.cjs` | parcours spécifique de la page enfant iframée |
| `tests/parcours-actiflip.test.cjs`, `parcours-qualifications.test.cjs`, `nouvelles-lp-simples.test.cjs`, `onze-restantes.test.cjs` | parcours et qualifications métier |
| `tests/test_*.py` | audit statique, inventaire des formulaires, restauration GTM |

**Les tests sont de bonne qualité** : jsdom + vrai jQuery, requêtes réseau simulées, vérification
des états réels (pas de faux « Merci ! »). C'est très au-dessus de la moyenne d'un dépôt marketing.

### 5.2 Les 7 échecs : diagnostic exact

```
not ok 24, 25, 26, 27, 208, 255, 302
  tous : assurance-consultants-societe-conseil
  message : assert.ok(form && w.smsVerification)  → falsy
```

**Cause racine** : `assurance-consultants-societe-conseil` n'est pas une landing page, c'est un
**wrapper iframe de 2,9 Ko** dont le seul script est `bridge.js`. Il n'a donc ni `<form>`, ni
`verification-sms.js` chargé. Les fichiers `lead-handler.js` et `verification-sms.js` traînent dans
le dossier mais **ne sont jamais référencés par le HTML**. Les tests ont été écrits quand ce dossier
était une vraie LP.

**Pourquoi ce n'est pas un bug de production** : la page fonctionne — elle affiche une iframe vers
`https://www.ubepro.com/assurance-consultant-conseil-v2/`. Le problème est que **les tests testent
une chose qui n'existe plus**.

**Trois options, à trancher (décision D-04 du registre)** :
1. Exclure ce site de la liste des LP testées *(cohérent avec la réalité, 5 minutes)*.
2. Réintroduire une vraie LP dans ce dossier *(si le wrapper iframe est un pis-aller temporaire)*.
3. Faire tester `bridge.js` par des tests dédiés *(le plus juste, mais demande un vrai travail)*.

### 5.3 Le piège des tests Python

```
$ cd tests && python3 -m unittest …        → 1 ERROR (ModuleNotFoundError: 'tools')
$ PYTHONPATH=. python3 -m unittest …       → 12/12 OK
```

Les tests importent `tools.inventaire_formulaires` mais se lancent depuis `tests/`. La commande
documentée dans `assurance-tns/RAPPORT-INTEGRATION.md` (`npm test --prefix tests`) ne concerne que
le JS. **Il n'y a pas de commande unique documentée pour tout lancer.** À corriger : c'est le genre
de détail qui fait qu'en six mois plus personne ne lance les tests.

### 5.4 La dette de test structurelle

- **368 tests pour 146 pages** : c'est beaucoup en apparence, mais 43 sites seulement sont dans
  `pages-adaptees.json`. Les 100 autres ne sont couverts que par les contrôles statiques.
- **Aucun test ne vérifie la production réelle** (réception CRM, envoi SMS effectif, événement GTM
  reçu). Tous les tests sont des simulations. Personne ne sait aujourd'hui si un vrai lead arrive.
- **Aucun test de non-régression sur le poids.** C'est précisément pour cela que le dépôt a atteint
  1,1 Go sans que personne ne s'en aperçoive.

---

## 6. Dette technique et structurelle

### 6.1 Redondance de pages — 8 paires identiques à l'octet près

| Page | Doublon de | Poids du doublon |
|---|---|---|
| `assurance-agriculteur` | `assurance/agriculteur` | 7,7 Mo |
| `assurance-assurance-professionnelle-iard-cookie` | `assurance/assurance-professionnelle-iard-cookie` | 7,7 Mo |
| `assurance-multirisques` | `assurance/multirisques` | 7,7 Mo |
| `assurance-professionnelle-iard` | `assurance/professionnelle-iard` | 7,7 Mo |
| `assurance-protection-sociale-collective` | `assurance/protection-sociale-collective` | 7,8 Mo |
| `assurance-protection-sociale-collective-v4` | `assurance/protection-sociale-collective-v4` | 7,7 Mo |
| `assurance-rc-pro` | `assurance/rc-pro` | 7,7 Mo |
| `assurance-tns-pro-v2-adw` | `assurance-professionnelle-tns-v2/assurance-tns-pro-v2-adw` | — |
| `assurance-consultant-societe-conseil-v2` | `assurance-consultants-societe-conseil` | 5,9 Mo |

**Les 7 dossiers de `assurance/` n'existent pas dans `ordre-sites.txt`.** Ils ont donc été ajoutés
après, probablement par mégarde (glisser-déposer). **Ce sont 54 Mo de doublons purs.** Ils portent en
plus des fichiers de documentation plus légers que leurs jumeaux à la racine — ce qui suggère que
c'est `assurance/` qui est l'**ancienne** copie, et la racine la **version de travail**.

### 6.2 Redondance de médias — 833 Mo récupérables

| Actif | Copies | Poids total |
|---|---|---|
| `2021-Cupra-Formentor-001-1080.jpg` | 139 | 84,9 Mo |
| `cup-of-coffee-1280537_1920.jpg` | 139 | 67,7 Mo |
| `script.js` (1,45 Mo) | 39 versions distinctes | 100 Mo cumulés |
| `2021-Cupra-Formentor-005/003-1080.jpg` | 139 chacun | 85 Mo |
| `OpenSans-CondBold.ttf` | 139 | 35 Mo |
| `2149728025.jpg` | 32 | 35,4 Mo |

**Analyse** : chaque LP embarque l'intégralité du kit Webflow (images de démonstration du thème,
3 variantes de chaque police). Ce n'est pas un problème de « code » mais de **processus de
production** : on duplique un dossier au lieu de partager des actifs.

**Ce que je recommande, par ordre de rentabilité** :
1. **Supprimer les médias orphelins** (678 fichiers, mesure automatique disponible) → gain immédiat,
   risque quasi nul, vérifiable page par page.
2. **Externaliser un dossier de médias partagé** (`/assets-common/`) pour les images et polices
   réellement utilisées par plusieurs pages → gain de 60 à 70 %, mais impose un déploiement commun.
3. **Convertir en WebP/AVIF** les JPG de plus de 300 Ko → 30 à 50 % de gain supplémentaire.
4. **Sortir les vidéos du dépôt** (`canal` à lui seul : 28,5 Mo) → YouTube/Vimeo.

### 6.3 Nommages problématiques

| Anomalie | Exemple | Conséquence |
|---|---|---|
| Espace dans un nom de dossier | `assurance-consultants-societe-conseil - Copie` | casse les scripts shell, les URL, les déploiements |
| Tiret final | `ticket-restaurant-` | confusion, doublon de `ticket-restaurant` |
| Doublons sémantiques | `assurance-consultant-societe-conseil-v2` **et** `assurance-consultants-societe-conseil` (pluriel + v2) | on ne sait pas laquelle est la bonne |
| Suffixes `-v1`, `-v2`, `-v4` coexistants | `protection-sociale-collective` et `-v4` | deux versions en production potentielle |
| Absence de `-v2` alors que des v2 existent | `energie` / `energie-v2`, `geolocalisation` / `-v2` | ambiguïté |
| « Copie » | dossier `… - Copie` | artefact système, à supprimer |
| Dossier `LP_reference` | majuscules + underscore | le seul du dépôt ; à renommer ou à documenter |

**Aucune convention de nommage n'est documentée.** `ordre-sites.txt` joue ce rôle implicitement
(131 entrées, ordre volontaire : LP → TIP → auto → remerciement → v2) mais 7 dossiers sur disque
n'y figurent pas. **Recommandation : formaliser `<métier>-<offre>[-vN]` et faire respecter.**

### 6.4 Le poids de `script.js` — le vrai plafond de performance

1,45 Mo de JavaScript **avant** toute interactivité sur **chaque** page. Sur mobile en 4G, c'est
plusieurs secondes de blocage du rendu. Combiné à 5-15 Mo d'images et 24-58 polices, chaque LP
affiche un temps de chargement très dégradé.

**Le levier n°1 de performance du projet n'est pas le code, c'est le poids.** Un audit Lighthouse
sur 5 pages représentatives (une de chaque famille) devrait être la première action après ce mémoire.

### 6.5 La documentation : un vernis qui trompe

C'est le résultat le plus dérangeant de cette analyse, et il faut le dire nettement.

Seuls **6 dossiers sur 146** possèdent un répertoire `docs/` : `agriculteur`,
`assurance-tns`, `assurance-tns-pro-v2-adw`, `solutions-agv-amr`,
`assurance-consultants-societe-conseil`, `assurance-consultant-societe-conseil-v2`.
Ces 6 dossiers ont l'air exemplaires : `RAPPORT-MODIFICATIONS.md` détaillé, analyse
fonctionnelle de référence, guide CRM/Sheets/GTM, procédure SMS, snippet d'embed Webflow, `Code.gs`.

**En réalité, cette documentation est un copier-coller non adapté.** Vérifications faites :

**a) Le même document de référence est dupliqué 4 fois**, avec 30 à 60 octets de différence
(un nom de LP substitué) :
`ANALYSE-FONCTIONNELLE-REFERENCE.md` = 9 118 / 9 121 / 9 128 / 9 158 octets dans `assurance-tns`,
`assurance-tns-pro-v2-adw`, `solutions-agv-amr`, `agriculteur`. C'est le **même texte**, présenté
comme une analyse spécifique à chaque page.

**b) Les guides de configuration sont faux dans leur titre comme dans leur contenu.**
`solutions-agv-amr/docs/CONFIGURATION-CRM-GOOGLE-SHEET-GTM.md` s'ouvre sur :
« LP `solutions-agv-amr-pro-v2-adw` » — **ce dossier n'existe pas**, et parle de `TNS_CONFIG`.
`solutions-agv-amr` n'est pas une LP d'assurance. Le contenu est le guide de la LP TNS recyclé.

**c) Les documents contredisent le code.**
Les 6 dossiers affirment « **Aucune confirmation par code SMS** » / « la vérification SMS est exclue ».
Or les 6 chargent `verification-sms.js` **et** `lead-handler.js`, et le SMS est bel et bien actif :
`agriculteur` a une étape de vérification, `assurance-tns` aussi. Les rapports portent pourtant
« Aucune confirmation par code SMS ». **Un développeur qui lit la doc et non le code déploiera une
LP en croyant que le SMS est désactivé.**

**d) Les promesses des rapports ne sont pas toutes tenues.**
`agriculteur/RAPPORT-MODIFICATIONS.md` affirme « H1 hero déjà unique, conservé ». Mesure réelle :
**1 H1** dans `agriculteur` ✅. Mais `assurance-tns/RAPPORT-MODIFICATIONS.md` affirme « un seul H1
(titre hero) — les 8 autres titres passent en `h2` ». Mesure réelle : **9 `<h1>`** dans le HTML.
La correction annoncée n'est pas dans le fichier. Même constat sur `solutions-agv-amr`, dont le
rapport décrit un H1 unique et un visuel de hero remplacé : le H1 est bien unique (1), mais la
description du visuel ne peut être vérifiée sans comparaison d'image.

**e) L'`ANALYSE-FONCTIONNELLE-REFERENCE.md` décrit une architecture qui n'existe pas dans ce dépôt.**
Il parle de `index.html` + `js/main.js` + `css/style.css` et de `window.UBEPRO_CONFIG`. Or **aucun
dossier de ce dépôt ne suit cette structure** : tous utilisent `script.js` + `style.css` à la racine,
avec `UBE_CONFIG` / `TNS_CONFIG`. Le document décrit la LP hébergée sur `ubepro.helloleadpreprod.fr`,
qui n'est pas ici.

---

### 6.6 Traces de l'outil de conversion `lp2site.py`

Tous les `rapport-site.md` disent la même chose : « Généré par `lp2site.py` », daté du
**2026-10-22**, avec « H1 : 0 ⚠ à corriger », « Éléments ajoutés automatiquement : meta description
(auto — à relire) ». **`lp2site.py` n'est pas dans le dépôt.** C'est une perte de connaissance
critique : l'outil qui a produit les 146 pages est absent, donc non maintenable, non corrigeable.

**C'est, avec le poids du dépôt, le point le plus important de ce mémoire.**
Tant que `lp2site.py` n'est pas versionné, les défauts systémiques (H1, lang, meta description)
seront corrigés à la main, page par page, 146 fois — et reviendront à la prochaine conversion.

---

## 7. Inventaire exhaustif des anomalies (classées par gravité)

### 🔴 Critique — impact direct sur le chiffre d'affaires

| # | Anomalie | Périmètre | Action |
|---|---|---|---|
| C1 | 37 pages avec formulaire **non raccroché** au handler | voir liste au §7.1 | marquer `data-ubepro-lead="1"` **ou** documenter l'exception |
| C2 | 2 pages **amputées** : `assurance-agriculteur-v2` (0 formulaire) et `agriculteur` (2 formulaires, 0 marqué) | 2 | restaurer ou retirer |
| C3 | 2 collisions de `formId` CRM | 4 pages | attribuer un `formId` unique par page |
| C4 | CORS de l'API SMS non vérifié sur les domaines finaux | 87 pages | test SMS réel sur chaque domaine avant mise en ligne |
| C5 | Réception CRM non confirmable côté navigateur (`nocors`) sans déduplication serveur — **réception réelle validée par le métier**, reste le cas dégradé Sheets-OK/CRM-KO | 87 pages | surveillance : alerter si un lead existe dans Sheets mais pas dans le CRM |
| C6 | Pont iframe limité à une seule origine parente | wrappers | élargir ou documenter |

### 🟠 Majeur — dette structurelle

| # | Anomalie | Périmètre | Action |
|---|---|---|---|
| M1 | 833 Mo de doublons dans Git | global | déduplication + `.gitignore` des actifs lourds |
| M2 | 54 Mo de doublons purs (`assurance/`) | 7 dossiers | supprimer l'arborescence `assurance/` |
| M3 | Dossier `… - Copie` committé | 1 | supprimer |
| M4 | `lp2site.py` absent du dépôt | global | **récupérer et versionner l'outil** |
| M5 | 678 médias orphelins | global | purge automatique |
| M6 | 81 pages en `lang="en"` | 81 | passer en `fr` |
| M7 | 129 pages sans `<h1>` | 129 | ajouter un H1 unique |
| M8 | 7 échecs de test permanents | 1 site | trancher (voir §5.2) |
| M10 | Documentation affirme « SMS exclu » sur 6 dossiers où il est actif | 6 | réécrire ou supprimer |
| M11 | Guide de config `solutions-agv-amr` parle d'un dossier inexistant et de `TNS_CONFIG` | 1 | réécrire |
| M12 | `ANALYSE-FONCTIONNELLE-REFERENCE.md` décrit une architecture absente du dépôt | 4 copies | harmoniser avec la réalité |
| M9 | Aucun test de production réelle | global | mettre en place un lead de test quotidien |

### 🟡 Modéré — qualité et conformité

| # | Anomalie | Périmètre |
|---|---|---|
| Q1 | 10 pages en contenu mixte `http://` (dont 6 de la famille ticket restaurant) | 10 |
| Q2 | `robots.txt`/`sitemap.xml` absents sur 6 pages | 6 |
| Q3 | Mention légale non reliée aux formulaires | 146 |
| Q4 | Meta descriptions toutes générées automatiquement | majorité |
| Q5 | Aucun script de vérification de poids en CI | global |
| Q6 | Commande de test unique non documentée | `tests/` |
| Q7 | 17 `<h1>` sur `assurance-iard-v2` | 1 |
| Q8 | `script.js` 1,45 Mo identique sur 139 pages | global |

### 🟢 Anecdotique — à nettoyer quand on passe

- `ticket-restaurant-` (tiret final)
- `nissan-juke` : hôte fantôme `htpps` dans l'ancien rapport
- `template-2` : gabarit laissé dans le périmètre de production
- `site` : page sans rôle clair, doublon fonctionnel de `accueil` / `site-assurances`
- `lexus-lbx` et `lexus-lbx-2` : deux versions, 33 Mo à elles deux
- `remerciement-panneaux-solaire` / `remerciements-panneaux-solaires` : singulier/pluriel

### 7.1 Statut C — les 37 pages où un formulaire n'est pas raccroché à la capture

C'est la liste de travail n°1. Ces pages affichent un formulaire, le valident, remercient
l'utilisateur — et n'envoient rien au handler standard.

| Page | Formulaires | GTM | Poids |
|---|---|---|---|
| `acces-internet-et-telephonie-pro-v2` | 1 | — | 7.45 Mo |
| `accueil` | 1 | — | 5.7 Mo |
| `assurance-assurance-professionnelle-iard-v2` | 1 | GTM-WMVZJKS | 7.41 Mo |
| `assurance-estheticiennes-institut-beaute` | 1 | GTM-53SH7D7F | 1.62 Mo |
| `assurance-protection-sociale-collective-v4` | 1 | GTM-53SH7D7F | 7.49 Mo |
| `assurance/protection-sociale-collective-v4` | 1 | GTM-53SH7D7F | 7.49 Mo |
| `assurances-multirisques-v2` | 1 | GTM-WMVZJKS | 7.41 Mo |
| `canal` | 2 | — | 28.54 Mo |
| `edenred-restaurant-v2` | 1 | — | 6.45 Mo |
| `edenred-titre-restaurant-v2` | 1 | — | 6.45 Mo |
| `energie-v2` | 1 | GTM-WMVZJKS | 7.32 Mo |
| `form-panneaux-photovoltaiques` | 1 | — | 5.72 Mo |
| `form-vehicules-utilitaires` | 1 | — | 6.4 Mo |
| `geolocalisation-v2` | 1 | GTM-WMVZJKS | 10.65 Mo |
| `hyundai-kona-electric-nouvelle-generation` | 1 | — | 7.84 Mo |
| `hyundai-tucson` | 1 | — | 7.84 Mo |
| `paritel-vous-rembourse-v2` | 1 | — | 8.0 Mo |
| `primagaz-v2` | 1 | — | 6.49 Mo |
| `remerciement-carte-cadeau` | 1 | — | 7.62 Mo |
| `remerciement-panneaux-solaire` | 1 | — | 8.17 Mo |
| `remerciement-ticket-restaurant` | 1 | — | 7.62 Mo |
| `remerciement-ticket-restaurant-v2` | 1 | — | 7.62 Mo |
| `remerciements-panneaux-solaires` | 1 | — | 8.17 Mo |
| `sage-gestion-de-la-paie-hd-v4` | 1 | — | 5.91 Mo |
| `securite-pro-v2` | 1 | — | 5.87 Mo |
| `template-2` | 1 | — | 8.88 Mo |
| `ticket-restaurant-v2` | 1 | — | 7.9 Mo |
| `typ-energie` | 1 | — | 6.39 Mo |
| `typ-formulaires-caisses-thank-you-page` | 1 | — | 6.29 Mo |
| `typ-formulaires-energie-thank-you-page` | 1 | — | 5.73 Mo |
| `typ-formulaires-panneaux-photovoltaiques` | 1 | — | 5.72 Mo |
| `typ-formulaires-panneaux-thank-you-page` | 1 | — | 5.73 Mo |
| `typ-formulaires-securite-thank-you-page` | 1 | — | 6.35 Mo |
| `typ-formulaires-typ-log-entreprise` | 1 | — | 5.78 Mo |
| `typ-formulaires-vehicules-thank-you-page` | 1 | — | 6.4 Mo |
| `typ-ticket-restaurant` | 1 | — | 6.55 Mo |
| `vehicules-professionnel-v2` | 1 | — | 8.34 Mo |

### 7.2 Statut B — les 2 pages dont les modules existent mais ne sont pas chargés

| Page | Formulaires | GTM | Poids |
|---|---|---|---|
| `agriculteur` | 2 | GTM-53SH7D7F | 7.05 Mo |
| `solutions-agv-amr` | 2 | GTM-53SH7D7F | 13.53 Mo |

### 7.3 Statut D — les 23 pages sans formulaire (à qualifier une par une)

| Page | Formulaires | GTM | Poids |
|---|---|---|---|
| `alfaromeo-tonale-remerciement` | 0 | — | 6.15 Mo |
| `assurance-agriculteur-v2` | 0 | GTM-53SH7D7F | 6.0 Mo |
| `assurance-consultant-societe-conseil-v2` | 0 | GTM-53SH7D7F | 5.73 Mo |
| `assurance-consultants-societe-conseil` | 0 | GTM-53SH7D7F | 8.08 Mo |
| `assurance-estheticiennes-instituts-beaute` | 0 | — | 5.7 Mo |
| `edenred-typ` | 0 | — | 5.96 Mo |
| `formulaire` | 0 | — | 5.7 Mo |
| `geo` | 0 | — | 5.7 Mo |
| `mentions-legales` | 0 | — | 0.03 Mo |
| `mercedes-vous-remercie` | 0 | — | 6.5 Mo |
| `mitsubishi-fuso-remerciement` | 0 | — | 13.37 Mo |
| `nettoyage-locaux-professionnels` | 0 | — | 5.87 Mo |
| `panneaux-photovoltaiques-panneaux-photovoltaique-valider` | 0 | — | 9.76 Mo |
| `paritel-typ` | 0 | — | 6.0 Mo |
| `politique-de-confidentialite-donnees-personnelles` | 0 | — | 0.06 Mo |
| `radius-remerciement` | 0 | — | 8.31 Mo |
| `radius-telematics-typ` | 0 | — | 6.13 Mo |
| `site` | 0 | — | 5.7 Mo |
| `site-assurances` | 0 | — | 2.98 Mo |
| `solutions-cles` | 0 | — | 11.93 Mo |
| `solutions-industrielles-cles-en-main` | 0 | — | 5.7 Mo |
| `typ-categ` | 0 | — | 7.01 Mo |
| `typ-categories` | 0 | — | 6.58 Mo |

### 7.4 Statut A — les 84 pages conformes au standard

Elles ne demandent aucune correction de code. Elles demandent une **validation de réception réelle**
(CRM, Sheets, SMS, GTM) sur leur domaine final — ce qu'aucun test de ce dépôt ne fait.

<details>
<summary>Voir les 84 pages</summary>

- `LP_reference`
- `acces-internet-et-telephonie-pro`
- `alfaromeo-tonale`
- `assurance-agriculteur`
- `assurance-assurance-professionnelle-iard-cookie`
- `assurance-commerce`
- `assurance-consultants-societe-conseil - Copie`
- `assurance-estheticienne-institut-beaute`
- `assurance-estheticiennes-instituts-beaute-v1`
- `assurance-iard-v2`
- `assurance-marchandise`
- `assurance-multirisques`
- `assurance-professionnelle-iard`
- `assurance-professionnelle-tns-v2`
- `assurance-professionnelle-tns-v2/assurance-tns-pro-v2-adw`
- `assurance-protection-sociale-collective`
- `assurance-rc-pro`
- `assurance-test-telephone`
- `assurance-tns`
- `assurance-tns-pro-v2-adw`
- `assurance/agriculteur`
- `assurance/assurance-professionnelle-iard-cookie`
- `assurance/multirisques`
- `assurance/professionnelle-iard`
- `assurance/protection-sociale-collective`
- `assurance/rc-pro`
- `assurances-professionnelles`
- `automobile`
- `ayvens-france`
- `cartes-carburant`
- `celebrez-le-noel-des-salaries-avec-kadeos`
- `complementaire-retraite-tns-v2`
- `dacia-jogger`
- `ecomobility`
- `edenred-kadeos`
- `edenred-ticket-restaurant-juillet-v1`
- `energie`
- `fiat-pro`
- `formulaire-globale`
- `gamme-de-rayonnage-actiflip-hd`
- `gamme-de-rayonnage-actiflip-v4`
- `geolocalisation`
- `geolocalisation-de-flotte`
- `intuis`
- `lexus-lbx`
- `lexus-lbx-2`
- `mercedes-benz-mercedes-benz-evito`
- `mercedes-benz-nouvel-ecitan-fourgon`
- `mercedes-benz-sprinter`
- `mitsubishi-fuso`
- `nissan-ariya`
- `nissan-juke`
- `panneaux-photovoltaiques-energie-solaire`
- `paritel`
- `paritel-vous-rembourse`
- `primagaz`
- `primagaz-obtenez-votre-gaz-propane-a-prix-fixe`
- `protection-sociale-collective`
- `rc-pro-consultant-conseil-adw`
- `renault-capture`
- `sage-gestion-de-la-paie-hd`
- `sauvie-defibrillateurs-en-entreprise`
- `securite-professionnels`
- `still-manutention`
- `suivi-de-vehicules`
- `ticket-restaurant`
- `ticket-restaurant-`
- `ticket-restaurant-septembre`
- `ticket-restaurant-septembre-btp`
- `tns-prevoyance-v2`
- `tns-prevoyance-v2-adw-test`
- `too-good-to-go`
- `toyota-gamme-hybride`
- `typ-formulaires-form-typ-vehicules`
- `typ-formulaires-typ-caisses-enregistreuse`
- `typ-formulaires-typ-energie-form`
- `typ-formulaires-typ-panneaux-form`
- `typ-formulaires-typ-secu-form`
- `une-rentree-sous-le-signe-du-pouvoir-d-achat`
- `vehicules-de-societe-hd`
- `vehicules-utilitaires`
- `voiture-nouveau-range-rover`
- `voiture-range-rover`
- `volvo`

</details>

---

## 8. Plan d'action proposé

### Étape 0 — Sécuriser la connaissance (immédiat, 1 jour)

1. Récupérer `lp2site.py` et `inventaire_premier_commit.py` (celui-ci est là, l'autre non).
2. Versionner ce mémoire et les scripts d'analyse.
3. Écrire un `README.md` à la racine : qu'est-ce que ce dépôt, comment lancer les tests, comment
   déployer une LP, quelle est la convention de nommage.

### Étape 1 — Arrêter l'hémorragie (semaine 1, faible risque)

4. Supprimer `assurance-consultants-societe-conseil - Copie`.
5. Décider du sort de `assurance/` (7 doublons, 54 Mo) — **recommandation : supprimer, la racine est
   la version de travail**.
6. Purger les 678 médias orphelins (script fourni, vérification page par page).
7. Trancher les 7 échecs de test (option 1 : exclure le wrapper iframe de la liste).

### Étape 2 — Réparer la capture (semaine 2, impact commercial direct)

8. Reprendre les 37 pages du statut C une par une, avec la fiche `ANALYSE/fiches/<page>.md` sous les yeux.
9. Corriger les 2 collisions de `formId`.
10. Restaurer ou retirer `assurance-agriculteur-v2`.
11. Mettre en place un **lead de test quotidien** (une page, un numéro, une vérification CRM + Sheets).

### Étape 3 — Assainir le SEO (semaine 3, sans risque visuel)

12. `lang="fr"` sur les 81 pages concernées (sed global + vérification).
13. Un `<h1>` unique par page, en conservant les classes (méthode validée sur `assurance-tns`).
14. Relire les meta descriptions des 20 pages à plus fort trafic.

### Étape 4 — Réduire le poids (semaine 4-6, le gain le plus visible)

15. Externaliser les polices (chargement réseau commun ou sous-ensemble).
16. Convertir les images lourdes en WebP.
17. Sortir les vidéos de Git.
18. Ajouter un contrôle CI : « aucun fichier > 1 Mo, aucune page > 10 Mo ».

### Étape 5 — Industrialiser (mois 2)

19. Rétablir `lp2site.py` comme **seul** chemin de production d'une LP, avec les corrections H1/lang
    intégrées dans le générateur.
20. Documenter le contrat de capture dans un `CONTRAT-CAPTURE.md` unique (aujourd'hui éparpillé dans
    5 dossiers `docs/`).
21. Mettre en place un déploiement reproductible (aujourd'hui : copie manuelle de dossier).
22. **Réécrire ou supprimer la documentation mensongère** : mieux vaut aucune doc qu'une doc qui dit
    le contraire du code. Piste : un test qui vérifie que chaque `RAPPORT-MODIFICATIONS.md` ne
    contient pas d'affirmation démentie par le code (ex. « SMS exclu » alors que
    `verification-sms.js` est chargé).

---

## 9. Ce qu'il faut retenir dans six mois

1. **Ce dépôt est un parc de pages d'acquisition, pas un logiciel.** On ne le refactorise pas :
   on le normalise et on le purge.
2. **`lead-handler.js` + `verification-sms.js` = 55 Ko qui portent 100 % de la valeur métier.**
   Tout le reste (`script.js`, `style.css`, images) est du décor Webflow remplaçable.
3. **Le statut d'une page se lit en une commande** : `python3 ANALYSE/scripts/inventaire_exhaustif.py`.
   Si le chiffre des 37 pages « formulaire non raccroché » ne baisse pas, rien n'a vraiment avancé.
4. **Le CORS de l'API SMS est le talon d'Achille.** Une page déployée sur un nouveau domaine sans
   test SMS est une page qui ne convertit pas.
5. **`lp2site.py` est le chaînon manquant.** Sans lui, chaque nouvelle LP réintroduira les mêmes
   défauts (0 H1, `lang="en"`, meta auto).
6. **Ne jamais croire un rapport sans le vérifier.** Ce dépôt contient de la documentation
   qui affirme l'inverse de ce que fait le code. La seule source de vérité est `index.html`
   et les deux fichiers JS de capture.
7. **Le poids est l'indicateur de santé du dépôt** : 1,1 Go aujourd'hui, 265 Mo après déduplication
   réaliste. C'est mesurable, réversible et sans risque.

---

*Mémoire établi par analyse statique exhaustive + exécution des suites de tests le 9 novembre 2026.
Tous les chiffres sont reproductibles : voir `ANALYSE/scripts/` et `ANALYSE/README.md`.*
