# Plan d'optimisation — `comparateurpro.fr`

> 24 idées classées par **rapport gain / effort**, pas par ordre de préférence.
> Chaque chiffre provient des mesures de `ANALYSE/data/` ou de mesures complémentaires
> faites le 9 novembre 2026. Les estimations de gain sont explicitement séparées en
> **[mesuré]** et **[estimation]** — ne pas les confondre.

---

## 0. Le cadrage qui change tout

Avant les optimisations, une distinction à poser, parce qu'elle détermine tout le reste :

**Ce parc contient deux populations de pages qui n'ont pas le même objectif.**

| Population | Nombre | Objectif réel | Levier prioritaire |
|---|---|---|---|
| LP d'acquisition payante (Google Ads, campagnes) | ~80 | **convertir un clic payé** | vitesse, friction du formulaire, fiabilité de la capture |
| Pages « vitrine » (constructeurs auto, Édenred, remerciement) | ~60 | **informer / remercier** | contenu, poids, partage social |

Les optimiser avec la même grille est une erreur. Une LP payante dont le formulaire met 3 s
à s'afficher perd de l'argent réel ; une page de remerciement de 8 Mo ne coûte qu'en hébergement.

**Deuxième cadrage** : sur une LP payante, **le SEO organique est presque irrelevant**. Optimiser
les `<h1>` de ces pages pour Google est un gain marginal. En revanche, les corriger sert
l'**accessibilité** (structure du document), les **Quality Score** (pertinence de la page
d'atterrissage) et le **partage social**. C'est pour ces raisons qu'il faut le faire — pas pour
le trafic organique.

---

## 1. Priorité absolue — ce qui coûte de l'argent aujourd'hui

### Idée 1 — Fiabiliser la capture avant d'optimiser la vitesse
**Effort : 2 jours · Gain : le plus élevé de toute la liste**

Optimiser une page qui ne transmet pas son lead est une perte de temps. Avant toute chose :
- tester un lead réel sur 5 pages représentatives (une par famille) ;
- vérifier la réception dans le CRM **et** dans la feuille Google ;
- vérifier le SMS sur le domaine final (CORS).

**[mesuré]** 37 pages ont un formulaire non raccroché au handler. Réparer 5 pages parmi les plus
trafic pourrait suffire à financer tout ce plan.

### Idée 2 — Mesurer ce qui compte vraiment : la conversion par étape
**Effort : 3 jours · Gain : transformation de la pilotabilité**

Aujourd'hui, la seule métrique observée est « un lead est arrivé ». On ne sait pas **où** les
visiteurs abandonnent, alors que le formulaire compte jusqu'à 8 étapes.

À instrumenter par étape :
```
formulaire_etape_vue (index, total)
formulaire_etape_abandon (index, derniere_etape)
sms_code_envoye / sms_code_valide / sms_code_echec (motif)
lead_envoye / lead_confirme / lead_echec (destination)
```

**[mesuré]** Le formulaire principal a une médiane de **35 champs** (max 138) ; 45 pages en ont
plus de 30. **[estimation]** Sans mesure par étape, on ne saura pas si c'est le nombre de
questions, la vérification SMS ou le CORS qui bloque.

### Idée 3 — La vérification SMS est un péage : la rendre facultative sur les campagnes à faible valeur
**Effort : 1 jour · Gain potentiel : le plus fort levier de conversion**

**[mesuré]** La vérification SMS est active sur 86 pages et **bloque l'envoi du lead** tant que le
numéro n'est pas validé. C'est une décision métier (numéros qualifiés) mais elle a un coût :
chaque visiteur qui n'a pas son téléphone sous la main ou qui ne reçoit pas le SMS est perdu.

Trois stratégies à tester en A/B :
1. **SMS obligatoire** (statut actuel) — qualité maximale, volume minimal ;
2. **SMS différé** — le lead part sans validation, le SMS est proposé après le « Merci » ;
3. **SMS conditionnel** — obligatoire sur les offres à forte valeur (assurance TNS, RC Pro),
   facultatif sur les offres à faible panier (ticket restaurant, cartes carburant).

Le `lead-handler.js` transmet déjà `telephone_verifie=oui/non` : la donnée existe pour arbitrer.
**Il manque juste l'expérimentation.**

---

## 2. Performance — le poids (le poste le plus lourd)

### Idée 4 — Réduire de moitié le poids des images (le plus gros gain unitaire)
**Effort : 1 semaine · Gain [estimation] : −50 à −60 % de poids par page**

**[mesuré]** Les JPG pèsent **466 Mo** du dépôt, pour une moyenne de **44 images par page** et
**7,5 Mo par page**. Les images sont déjà en `loading="lazy"` (120/121 sur mon échantillon) :
le chargement initial est correct, mais le poids transféré reste énorme au scroll.

Actions concrètes :
- conversion systématique en **WebP** (déjà utilisé sur 296 fichiers seulement) : −30 à −50 % ;
- redimensionnement à la taille d'affichage réelle (les exports Webflow livrent souvent du 2000 px
  pour un affichage à 800 px) ;
- `sizes` correct sur les `srcset` : **[mesuré]** seules 38 images sur 121 ont un `srcset`.

### Idée 5 — Supprimer les polices inutiles (gain immédiat, zéro risque visuel)
**Effort : 2 heures · Gain [estimation] : −30 à −40 % du poids des polices**

**[mesuré]** Chaque page charge **10 familles de polices distinctes**, dont plusieurs ne servent
à rien : `Nissanbrand`, `Toyota Type Book` sont chargées sur des pages qui ne sont pas des LP
automobile ; `webflow-icons` est un artefact de l'éditeur. Sur 27 familles déclarées, **19 à 20
sont réellement utilisées**.

**[mesuré]** Le dépôt contient **146 Mo de fichiers `.ttf`** contre 58 Mo de `.woff2`. Les TTF ne
sont téléchargés qu'en repli, mais ils polluent le dépôt et allongent les déploiements.
**Les TTF sont supprimables sans impact navigateur moderne.**

### Idée 6 — Passer `script.js` de 1,45 Mo à < 300 Ko (ou l'assumer)
**Effort : 1 à 2 semaines, risqué · Gain [estimation] : −1 s à −2 s sur mobile**

**[mesuré]** `script.js` = **1,41 Mo médian sur 139 pages**, identique partout. C'est jQuery +
runtime Webflow + moteur de formulaire « Formly ». Sur mobile en 4G, c'est le principal facteur
de blocage du rendu.

Trois pistes, du moins risqué au plus risqué :
1. **`defer` partout** (déjà fait sur la plupart) et vérifier qu'aucun script bloquant ne subsiste ;
2. **Extraire jQuery** si le moteur de formulaire le permet (jQuery 3.7 fait ~85 Ko minifié) ;
3. **Remplacer Formly par un formulaire natif** — le plus gros gain mais demande de réécrire la
   navigation multi-étapes. À réserver aux 10 pages à plus fort trafic.

> ⚠️ Ne pas toucher `script.js` sur les 84 pages du statut A sans un test de non-régression sérieux :
> c'est lui qui gère la validation par étape, et il est identique partout.

### Idée 7 — Configurer un vrai cache et une vraie compression
**Effort : 1 jour · Gain [estimation] : −70 % de temps de chargement au 2ᵉ passage**

**[mesuré]** Le dépôt ne contient **aucune configuration de serveur** : ni `.htaccess`, ni
`_headers` (Netlify), ni `_redirects`, ni configuration Nginx.

À ajouter :
```
# Cache long sur les actifs immuables
/img/*, /fonts/*, /videos/* : Cache-Control: public, max-age=31536000, immutable
# Court sur le HTML
/*.html : Cache-Control: public, max-age=300, must-revalidate
# Compression
gzip / brotli sur text/html, text/css, application/javascript
```
Le gain est invisible au premier chargement mais devient majeur sur les visites répétées et
les campagnes où l'utilisateur revient.

### Idée 8 — Servir les polices en local, mais une seule fois
**Effort : 1 jour · Gain [estimation] : −200 Ko par page**

**[mesuré]** Les 27 fichiers de polices sont **dupliqués dans chaque dossier** (139 copies de
`OpenSans-CondBold.ttf`, 35 Mo au total pour une seule police). Aujourd'hui chaque page charge
sa propre copie.

Solution : un répertoire `/assets/fonts/` partagé, servi avec un cache long. La première page
paye le coût, toutes les suivantes le réutilisent. Même logique pour les images de fond
communes (139 copies de chaque photo Unsplash).

### Idée 9 — Sortir les vidéos du dépôt
**Effort : 1 heure · Gain [mesuré] : −53 Mo (28,4 Mo webm + 24,4 Mo mp4)**

**[mesuré]** Les 4 vidéos de `canal` et `lexus-lbx-2` expliquent que `canal` pèse 28,5 Mo à lui
seul. Les héberger sur YouTube/Vimeo (ou un CDN) supprime ce poids du dépôt **et** allège la
page pour le visiteur qui ne regarde pas la vidéo.

---

## 3. Conversion — le formulaire

### Idée 10 — Réduire le nombre d'étapes là où c'est possible
**Effort : 2 jours · Gain [estimation] : +5 à +15 % de complétion**

**[mesuré]** Le formulaire d'assurance TNS a **8 étapes**, 38 éléments visibles dont 28 boutons
radio. C'est long. Deux leviers sans perdre d'information :
- regrouper les questions courtes (2-3 par écran au lieu d'une seule) ;
- remonter la demande de coordonnées **en dernier** (aujourd'hui elle arrive souvent avant la
  fin, ce qui décourage : on demande le téléphone avant d'avoir donné envie).

### Idée 11 — Afficher la progression et l'engagement
**Effort : 1 jour · Gain [estimation] : +3 à +8 %**

Si 8 étapes sont nécessaires, il faut les **assumer visuellement** : barre de progression,
« Étape 3 sur 8 », et surtout une promesse en tête de formulaire (« 2 minutes, sans engagement »).
**[mesuré]** Aucun marqueur d'étape n'est détecté dans le HTML : c'est le JS qui gère, donc à
vérifier visuellement — mais un compteur explicite est un levier de complétion connu.

### Idée 12 — Sauvegarder la progression du formulaire
**Effort : 1 jour · Gain [estimation] : +2 à +5 % sur mobile**

Un utilisateur interrompu au milieu d'un formulaire de 8 étapes qui revient doit retrouver ses
réponses. Aujourd'hui, tout est perdu. Un `sessionStorage` du parcours (sans données sensibles)
suffit, et le `lead-handler.js` utilise déjà ce mécanisme pour le tracking.

### Idée 13 — Récupérer les abandons (le plus gros gisement inexploité)
**Effort : 3 jours · Gain [estimation] : le plus fort potentiel, à valider juridiquement**

Aujourd'hui, un visiteur qui saisit son téléphone puis abandonne à l'étape 5 est **totalement perdu**.
Une capture progressive (e-mail ou téléphone dès la première étape, envoyé en « lead partiel »)
permettrait de le relancer.

⚠️ **Attention juridique** : cela change la nature du consentement. À faire uniquement avec un
consentement explicite et une mention claire. C'est la seule idée de cette liste qui demande
l'aval du DPO avant implémentation.

### Idée 14 — Améliorer les messages d'erreur
**Effort : 1 jour · Gain [estimation] : +2 à +4 %**

**[mesuré]** `lead-handler.js` gère déjà proprement le cas « les deux destinations ont échoué »
(message clair + nouvel essai). Bon point. À généraliser : en cas d'échec SMS, proposer
explicitement un repli (« Vous ne recevez pas le code ? Cliquez ici ») plutôt qu'un message rouge.

---

## 4. SEO et partage social — les défauts systémiques

### Idée 15 — Corriger les titres de page (le défaut le plus visible)
**Effort : 1 jour · Gain [estimation] : fort sur le Quality Score et le partage**

**[mesuré]** **80 titres sur 146** sont le nom du dossier ou presque :
`« accueil »`, `« ticket-restaurant »`, `« nissan-juke »`, `« assurance-test-telephone »`,
`« assurance iard v2 »`, `« Energie »`. La longueur médiane est de **21 caractères** (recommandé
50-60) et 65 titres font moins de 20 caractères.

C'est le défaut qui se voit **partout** : dans l'onglet du navigateur, dans Google Ads, dans un
partage WhatsApp ou LinkedIn. Il nuit à la crédibilité immédiate de la page.

**Méthode** : `<Métier> : <bénéfice> | Comparateurpro`
- `accueil` → `Assurances professionnelles : comparez les offres | Comparateurpro`
- `ticket-restaurant` → `Ticket restaurant entreprise : jusqu'à 10 €/jour | Comparateurpro`
- `nissan-juke` → `Nissan Juke hybride en LLD : offre pro | Comparateurpro`

### Idée 16 — Ajouter les balises de partage social (`og:image`, `og:description`)
**Effort : 2 heures · Gain [estimation] : fort sur le clic depuis les messageries**

**[mesuré]** Aucune page n'a d'`og:image`. Les `og:title` sont les mêmes noms de dossiers que les
titres. Résultat : un lien partagé sur WhatsApp ou LinkedIn affiche **un rectangle vide et
« accueil »**.

Pour un parc de LP diffusées en campagnes et parfois partagées par des prescripteurs, c'est
une perte directe de clics. Une image 1200×630 par famille de pages (8 images au total) suffit.

### Idée 17 — Un `<h1>` par page, et une hiérarchie de titres réelle
**Effort : 2 jours · Gain : accessibilité + structure**

**[mesuré]** 129 pages sans `<h1>`, 4 pages avec plusieurs (dont `assurance-iard-v2` avec **17**).
Et **[mesuré]** `assurance-tns` a 9 `<h1>` mais **0 `<h2>` et 0 `<h3>`** : la hiérarchie est
inexistante.

La méthode indolore existe déjà et a été validée (`solutions-agv-amr` : 19 → 1 H1 sans toucher
au design, les classes portant la typographie). À industrialiser.

### Idée 18 — Corriger `lang="en"` et le sitemap
**Effort : 1 heure · Gain : accessibilité linguistique (lecteurs d'écran), conformité**

**[mesuré]** 81 pages déclarent `lang="en"` alors que le contenu est en français. Un lecteur
d'écran prononcera le texte avec la mauvaise phonétique. Correction mécanique.

**[mesuré]** 132 `sitemap.xml` séparés, **aucun sitemap racine**, et **aucun `robots.txt` à la
racine**. Un `sitemap.xml` d'index à la racine (`sitemapindex`) déclarant les 132 serait plus
propre — à condition d'avoir tranché la question de l'indexation (idée 19).

### Idée 19 — Trancher la stratégie d'indexation (décision, pas technique)
**Effort : réunion d'1 h · Gain : évite de dissiper l'autorité**

**[mesuré]** **132 domaines canoniques distincts**, un par page. Google voit 132 sites
indépendants. Pour des LP payantes, deux stratégies cohérentes existent :

- **(A) `noindex` assumé** sur les LP payantes + indexation des seules pages de contenu
  (`site-assurances`, `mentions-legales`, `politique-de-confidentialite`). C'est le choix
  habituel : cela évite que vos LP de test concurrencent vos pages officielles et évite le
  contenu dupliqué entre variantes.
- **(B) Un domaine unique** (`comparateurpro.fr/lp/<nom>`) avec un canonical par campagne :
  l'autorité se cumule, mais il faut migrer 132 déploiements.

Aujourd'hui, l'entre-deux (132 domaines indexés, aucun ne capitalise) est le pire des cas.

### Idée 20 — Conformité et mentions légales
**Effort : 2 jours · Gain : maîtrise du risque juridique**

**[mesuré]** Les pages `mentions-legales` et `politique-de-confidentialite` existent et sont
complètes, mais **aucun formulaire ne mentionne le responsable de traitement, la durée de
conservation, ni un contact DPO**, alors que la donnée collectée (téléphone vérifié + situation
professionnelle) est revendue à des courtiers.

C'est le point le plus exposé du projet. Une phrase + un lien sous chaque bouton de validation
suffit techniquement ; le contenu doit être validé juridiquement.

---

## 5. Accessibilité

### Idée 21 — Corriger les `alt` des images
**Effort : 1 jour · Gain : accessibilité + SEO images**

**[mesuré]** Sur mon échantillon, **120 images sur 121 ont `alt=""`**. Sur `nissan-juke`, les 5
images (dont les photos du véhicule) ont toutes un `alt` vide. Un `alt` vide est correct pour une
image **décorative**, pas pour une photo produit.

Règle simple : `alt` descriptif sur le contenu, `alt=""` assumé sur le décor.

### Idée 22 — Étiqueter les champs de formulaire
**Effort : 2 jours · Gain : accessibilité + conversion**

**[mesuré]** `nissan-juke` a **11 champs et 0 `<label>`**, `assurance-tns` 59 champs pour 28
labels, et **0 `aria-label` sur tout l'échantillon**. Des champs sans étiquette sont un problème
d'accessibilité (RGAA/WCAG) **et** de conversion : au clic sur le libellé, rien ne se passe.

### Idée 23 — Vérifier le contraste et la navigation clavier
**Effort : 1 jour · Non mesuré ici (nécessite un navigateur)**

Les pages utilisent beaucoup de titres colorés (`teal-color`, `eyebrow`). Un audit de contraste
automatisé (axe DevTools, Lighthouse) sur 5 pages représentatives révélerait les cas bloquants.
Non couvert par mon analyse statique.

---

## 6. Industrialisation — pour que ça ne revienne pas

### Idée 24 — Un `lp2site.py` v2 qui produit du bon du premier coup
**Effort : 1 semaine · Gain : supprime la cause racine**

**[mesuré]** L'outil qui a généré les 146 pages (`lp2site.py`) **n'est pas dans le dépôt**. Tous
les défauts systémiques (0 H1, `lang="en"`, titres = nom de dossier, meta auto, `alt=""`) sont
produits par cet outil.

Tant qu'il n'est pas versionné et corrigé, chaque nouvelle LP réintroduira les mêmes défauts, et
les corrections manuelles devront être refaites 146 fois. **C'est l'optimisation la plus rentable
à moyen terme**, même si elle ne produit aucun effet visible aujourd'hui.

---

## 7. Ordre d'exécution recommandé

| Semaine | Actions | Nature |
|---|---|---|
| **S1** | Idées 1, 2 | Fiabiliser et mesurer — sans cela, tout le reste est aveugle |
| **S2** | Idées 15, 16, 18 | Titres + partage social + `lang` : 2 jours, effet immédiat et visible |
| **S3** | Idées 5, 9, 7 | Polices (TTF), vidéos, cache serveur : gain fort, risque quasi nul |
| **S4** | Idées 4, 8 | Images en WebP, assets partagés : le gros du poids |
| **S5** | Idées 10, 11, 14, 22 | Formulaire : étapes, progression, erreurs, labels |
| **S6** | Idées 3, 12, 13 | Expérimentation : SMS, reprise de parcours, abandons |
| **S7** | Idées 17, 21, 23, 20 | Structure, accessibilité, conformité |
| **S8+** | Idées 6, 24, 19 | Chantiers de fond : `script.js`, `lp2site.py`, indexation |

---

## 8. Objectifs chiffrés à 3 mois

| Indicateur | Aujourd'hui [mesuré] | Objectif réaliste |
|---|---|---|
| Poids moyen par page | 7,5 Mo | **< 2 Mo** |
| `script.js` | 1,41 Mo | **< 400 Ko** (ou assumé) |
| Polices par page | 27 fichiers / 10 familles | **4 familles utiles** |
| Titres de page corrects | 66 / 146 | **146 / 146** |
| Pages avec `og:image` | 0 / 146 | **146 / 146** |
| Pages sans `<h1>` | 129 / 146 | **0** |
| Pages `lang="en"` | 81 | **0** |
| Images avec `alt` pertinent | ~1 % | **> 80 % des images de contenu** |
| Cache / compression configurés | aucun | **actifs sur 100 % des pages** |
| Étapes du formulaire mesurées | non | **toutes, avec taux d'abandon** |

---

## 9. Ce que je ne recommande pas

Par honnêteté, trois idées séduisantes que les mesures ne justifient pas :

1. **Passer à un framework moderne (Next.js, Astro)** : 146 pages statiques qui fonctionnent.
   Le problème est le poids des **actifs**, pas l'outil de rendu. Une migration coûterait des mois
   pour un gain que l'idée 4 obtient en une semaine.
2. **Minifier `style.css`** (154 Ko médian) : le gain est de ~30 Ko après gzip, soit ~0,1 s.
   À faire en passant, mais ce n'est pas une priorité alors que 7,5 Mo d'images sont en jeu.
3. **Ajouter un CDN payant** : la latence n'est pas le problème identifié. Le problème est le
   volume. Un CDN accélère le transfert de fichiers trop lourds ; il ne les allège pas.

---

*Document établi le 9 novembre 2026 à partir de `ANALYSE/data/inventaire.json` (146 pages) et de
mesures complémentaires sur les en-têtes, les polices, les images et les formulaires.
Les chiffres [mesuré] sont reproductibles ; les chiffres [estimation] sont des ordres de grandeur
à confirmer par un audit Lighthouse avant/après.*
