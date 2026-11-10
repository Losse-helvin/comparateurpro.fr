# Audit global du dépôt — 10 novembre 2026

## Synthèse pour décision

Le dépôt est un ensemble de pages de campagne statiques, en grande partie issues d'exports Webflow, avec des modules locaux de capture de leads, de suivi et de vérification SMS. Il n'y a pas d'application racine unique ni de processus de build racine identifié. Les priorités sont : **sécuriser le routage des leads avant tout déploiement**, contrôler le consentement et les flux réels, puis fiabiliser les tests et rationaliser les fichiers. Aucun correctif de page n'a été effectué dans cet audit.

## Périmètre et méthode

- Inventaire récursif de tous les chemins versionnés via `git ls-files`, y compris les répertoires imbriqués : **11 885 fichiers**, **450 dossiers**, **147 fichiers `index.html`**, dont **8 imbriqués** sous `assurance/` ou `assurance-professionnelle-tns-v2/`. Le dossier racine lui-même n'est pas compté parmi les 450. Les dépendances installées localement, fichiers ignorés et `.git` sont exclus.
- [Inventaire de tous les dossiers et sous-dossiers](data/audit-dossiers-2026-11-10.csv) : comptage et poids récursifs. Les volumes des parents et enfants se chevauchent ; ne pas les additionner.
- [Inventaire des 147 pages](data/audit-pages-2026-11-10.csv) : langue, H1, formulaires et métadonnées extraits du HTML statique. Ces nombres sont des signaux, pas un diagnostic manuel de chaque parcours.
- Relecture des documents et scripts d'audit existants, examen ciblé du handler de référence, du wrapper consultant et des tests. Calcul des doublons sur les fichiers parcourus par `audit_poids.py` ; tests Python et tentative de suite JavaScript. L'inventaire couvre les chemins, mais **tous les contenus et parcours n'ont pas été expertisés individuellement**. Les archives PDF/XLS/XLSX/ZIP et les contenus binaires ont été inventoriés, pas audités intégralement.
- Pas d'accès aux configurations CRM, GTM, hébergeur, consentement réel ou données de production ; pas de test navigateur réel ou de lead envoyé. Les résultats ne constituent ni certification de sécurité ni avis juridique.

## Constats classés par priorité

### P0 — Routage des leads à confirmer avant publication

La révision documentée dans [REVISION-TRACKING-10-11.md](REVISION-TRACKING-10-11.md) indique que les `formId` ont été remplacés et avertit que les nouveaux identifiants doivent être créés et routés dans HelloLead. L'état réel du CRM n'est pas accessible ici. **Ne pas déployer en supposant la migration CRM faite.** Comparer registre, configuration CRM et destination pour chaque campagne active ; tester un pilote et vérifier indépendamment CRM et Sheets avant généralisation.

Dans [LP_reference/lead-handler.js](../LP_reference/lead-handler.js), lignes 22–23 et 599–635, le CRM est en `nocors` ; l'envoi par beacon ou réponse opaque ne confirme pas la réception. Aux lignes 846–856, la confirmation de Sheets **ou** celle du CRM suffit à afficher le succès. Une ligne Sheets ne démontre donc pas à elle seule que le CRM a reçu le lead. Prévoir accusé de réception vérifiable, identifiant d'événement et déduplication côté serveur, suivi des échecs et procédure de rapprochement.

### P1 — Parcours de capture et SMS

L'audit `python3 tools/audit_fonctionnalites.py` examine uniquement les **139 pages de premier niveau** : 77 satisfont son modèle statique complet, 4 ont un téléphone détecté sans satisfaire tous les critères et 58 restent à qualifier. Ces catégories ne sont pas des mesures de leads perdus : certaines pages sont des remerciements, iframes ou parcours spécifiques. Huit pages imbriquées ne sont pas couvertes par cet outil.

Le relevé HTML récursif dénombre **124 pages avec au moins un `<form>`**, dont **85 avec au moins un formulaire marqué** `data-ubepro-lead="1"`. Cela ne garantit ni que tous les formulaires d'une page sont marqués, ni qu'un formulaire non marqué est cassé : qualifier les formulaires, leurs destinations et les iframes un par un selon les campagnes actives.

Pour les parcours avec SMS, vérifier en conditions réelles : CORS par domaine, livraison du code, réponse API explicite, expiration, renvoi, erreurs et reprise. Le script d'audit existant signale qu'une réponse JSON non vide peut être acceptée sans indicateur positif explicite : confirmer le contrat de l'API avant correction ou conclusion.

### P1 — Consentement, données personnelles et sécurité

Les pages collectent des coordonnées et utilisent des services externes. La présence de code de consentement ne démontre pas la conformité de l'ensemble des balises GTM ni des flux. Avec le DPO et les responsables des services, vérifier les finalités, base légale, information, preuve et retrait du consentement, durées de conservation, accès Sheets/CRM, sous-traitants et transferts, ainsi que le déclenchement réel des tags avant et après choix. Vérifier également CORS, limitation de débit et anti-abus SMS côté serveur, validation et déduplication des leads, en-têtes de sécurité et politiques iframe sur les domaines réels. Ces éléments ne sont pas déductibles du seul dépôt.

### P1 — Tests et intégration continue

- `python3 -m unittest discover -s tests -p 'test_*.py' -v` : **12/12 réussis**.
- `npm ci --no-audit --no-fund` dans `tests/` : installation réussie ; `npm audit` : **0 vulnérabilité connue signalée** pour les dépendances de test au moment de l'exécution, pas pour les scripts tiers embarqués.
- `npm test` : interrompu après **180 secondes**, donc pas de bilan global actuel. Plusieurs échecs ont été observés dans `lead-reference.test.cjs` pour `assurance-consultants-societe-conseil` : le test attend un formulaire et `smsVerification`, alors que [la page](../assurance-consultants-societe-conseil/index.html) contient une iframe distante et un bridge. Cela révèle un décalage de contrat de test ; **cela ne prouve ni le bon fonctionnement ni la panne du parcours distant**. Les résultats de 361/368 dans les anciens documents ne sont pas une exécution complète de cette session.
- Ajouter un test du wrapper et du bridge avec origines autorisées et interdites, tests du parcours enfant, puis lancer la suite complète dans une CI avec délai adapté et rapport conservé. Ajouter des tests navigateur réels isolés et un contrôle du routage en préproduction.

### P2 — SEO et accessibilité

Sur les 147 HTML analysés : **129 sans balise H1**, **4 avec plusieurs H1**, **81 avec `lang` commençant par `en`**, et **3 sans meta description détectée**. Ces chiffres ne démontrent pas automatiquement un défaut sur chaque page : les remerciements, iframes et pages non indexables ont des objectifs différents ; vérifier aussi la langue effective et le DOM rendu. Décider d'abord quelles pages doivent être indexées, puis corriger langue, hiérarchie, titres, descriptions et canonical au cas par cas. Contrôler également au clavier les étapes, libellés, erreurs, focus et contraste ; aucun audit d'accessibilité automatisé ou humain complet n'a été réalisé.

### P2 — Poids et maintenance

`python3 ANALYSE/scripts/audit_poids.py --csv --gros-fichiers 8` a mesuré **11 720 fichiers, environ 1 094 Mo**, et estimé **835 Mo** redondants dans 480 groupes par empreinte. Le périmètre du script diffère de `git ls-files` ; il ne faut pas comparer directement les totaux. La réduction estimée correspond à une mutualisation hypothétique, **pas à des fichiers supprimables sans risque**. Les pages peuvent être déployées indépendamment et des actifs peuvent être chargés dynamiquement ou via CSS. Vérifier dépendances et déploiements avant toute suppression, et mesurer le poids réellement téléchargé, distinct du poids du dépôt. Prioriser les vidéos et images lourdes, puis mutualiser les actifs si l'hébergement et le cache le permettent.

### P2 — Documentation et inventaires

Les documents historiques restent utiles, mais certains chiffres ou préconisations sont datés ou contradictoires. Par exemple, le mémoire historique annonce 146 pages, tandis que le comptage actuel trouve 147 `index.html` versionnés. Le registre recommande des suppressions et cite d'anciens problèmes de `formId`, alors qu'une migration ultérieure est documentée ; ne pas exécuter ces recommandations sans nouvelle validation. Le document de suppression est daté du **11 novembre 2026**, après la date de cet audit : traiter cette date comme incohérente à vérifier, non comme preuve chronologique. L'ancien README mentionne une validation de production rapportée par le métier ; elle ne prouve pas que tous les domaines et nouveaux identifiants fonctionnent aujourd'hui.

## Plan d'action proposé

1. **Avant déploiement** : obtenir la liste des campagnes réellement actives ; rapprocher chaque `formId` du CRM, tester un lead réel autorisé et confirmer CRM, Sheets et attribution. Définir un retour arrière.
2. **Ensuite** : qualifier les pages/formulaires non reconnus et les 8 pages imbriquées ; tester les parcours SMS et iframe sur les domaines finaux ; surveiller erreurs et conversions.
3. **En parallèle** : audit DPO et sécurité des flux, des tags et des droits d'accès ; mettre en place une confirmation de réception et une déduplication côté serveur.
4. **Fiabilisation** : corriger le contrat des tests wrapper, exécuter la suite complète en CI, ajouter des tests navigateurs et des contrôles de régression par campagne.
5. **Optimisation** : trier SEO et accessibilité selon l'usage des pages ; mesurer performance en conditions réelles ; mutualiser progressivement sans supprimer d'actif ni de dossier avant validation.

## Reproduction et précautions

Les deux CSV de cet audit proviennent de la liste des fichiers suivis par Git ; l'extraction HTML utilise `html.parser` et ne rend pas JavaScript. L'analyse existante détaillée par page est disponible dans [fiches/](fiches/) et [MEMOIRE-ANALYSE.md](MEMOIRE-ANALYSE.md), mais ses chiffres sont historiques. Attention : `tools/audit_fonctionnalites.py` écrit `AUDIT-FONCTIONNALITES.md` à la racine et `audit_poids.py --csv` réécrit `ANALYSE/data/doublons.csv` ; sauvegarder les modifications éventuelles avant exécution. Les fichiers générés par ces commandes pendant cet audit ont été retirés ou restaurés après mesure.
