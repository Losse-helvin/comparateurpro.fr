# Contrôle des form_id et du tracking des LP

## Périmètre et source

Les 147 `index.html` de premier et deuxième niveau ont été recensés, y compris les 8 LP imbriquées. Le tableau [audit-identifiants-tracking.csv](data/audit-identifiants-tracking.csv) décrit chaque page et est reproductible avec `python3 tools/audit_identifiants_lp.py` (rediriger la sortie vers un fichier CSV). Le contrôle statique inspecte les formulaires HTML et les identifiants littéraux dans les scripts locaux `lead-handler.js` et `script.js` chargés par chaque page ; il n'exécute pas les scripts, ne voit pas le contenu d'une iframe distante et ne prouve pas le routage.

Le PDF `URL-formid-LP.pdf` (SHA-256 `eed7e6d684402e66c6f70e468a5f51428bbee2f02c4e2f85b3875760995e3350`) a été lu avec pypdf : les 147 identifiants de la liste principale correspondent, dans l'ordre de génération du PDF, au registre `ANALYSE/data/registre-formid.json` et à son inventaire URL. Les lignes qui partagent une URL conservent leurs identifiants distincts par dossier. **Ce PDF est lui-même généré à partir du registre du dépôt** (`tools/generer_pdf_urls.py`) ; il ne constitue pas une confirmation indépendante que le CRM connaît ces clés. Les 147 identifiants sont uniques.

## Résultat par page

- **88 pages** ont un identifiant détecté dans un script local chargé ou un attribut de formulaire ; toutes les valeurs détectées correspondent au registre/PDF.
- **59 pages** n'ont pas d'identifiant littéral détecté dans ces emplacements ; **36** d'entre elles ont au moins un formulaire HTML. Cela comprend des étapes de qualification, des cookies, des pages de contenu ou de remerciement, et des wrappers ; le nombre ne signifie pas 59 leads perdus. La détection n'a trouvé aucun champ téléphone ou email visible dans les formulaires de ces pages (méthode `tools/inventaire_formulaires.py`), mais des champs dynamiques ou externes restent possibles.
- Le PDF indique 89 câblages ; il compte également les fichiers présents sans nécessairement vérifier leur chargement. Notre tableau ne suppose pas qu'un fichier non chargé envoie un identifiant. Une iframe distante peut soumettre sous un autre identifiant ; son fonctionnement n'est pas contrôlable en lisant uniquement le parent.
- Aucune divergence détectée parmi les identifiants reconnus. Ne pas ajouter un `data-form-id` à un formulaire qui ne le consomme pas : ce serait faire croire à une intégration CRM sans la réaliser. Il faut qualifier les 59 pages avec le métier et les responsables des tunnels et des iframes avant d'y ajouter une capture.

## Correction effectuée

Sur `assurance-estheticiennes-institut-beaute`, le script autonome conservait la source de repli `LP CONSULTANTS`, et le HTML contenait l'attribut mal formé `data-source=ADW=""`. Ces deux valeurs ont été remplacées par une source vide ; les paramètres réels restent utilisables. Le générateur `tools/aligner_lp.py` a aussi été corrigé pour ne plus produire `data-source==""` lors de l'effacement d'un attribut. Aucun autre champ métier, valeur de réponse, identifiant existant ou parcours n'a été modifié.

Le contrôle statique ne trouve plus de valeur non vide dans les champs cachés et attributs de suivi reconnus sur les 147 pages. Ce contrôle ne démontre pas l'absence de valeurs injectées par tout JavaScript, iframe ou service externe. Les paramètres de campagne placés volontairement dans certains **liens sortants** ont été conservés : ils attribuent ces liens à leur destination et ne sont pas des valeurs par défaut ajoutées aux leads de la LP ; leur suppression nécessite une décision métier. Les modules existants peuvent conserver des paramètres réellement rencontrés en `sessionStorage` pendant une session : ce ne sont pas des valeurs inventées, mais cela signifie qu'une URL sans paramètres après une navigation dans la même session peut hériter de l'attribution antérieure. Le test « URL sans paramètres » ci-dessous utilise une session neuve.

## Vérifications

- Test jsdom ciblé sur la page corrigée : absence de source et catégorie fabriquées en session neuve, et conservation de `utm_source=google&categorie=999` ; 8 scénarios réussis, réseau simulé.
- Tests Python : inventaire complet des pages et du registre, unicité, absence de divergence détectée, champs statiques et correction de l'outil d'alignement.
- Pas de test réel du CRM, des API SMS, des domaines publiés ni des iframes distantes. L'envoi CRM en `no-cors` ne permet pas de confirmer sa réception depuis le navigateur.

## Décisions et contrôles avant déploiement

1. Confirmer auprès de l'équipe CRM que chaque `form_id` du PDF est bien créé et routé vers la bonne campagne : des identifiants du registre ont été générés localement et le PDF n'est pas une preuve d'enregistrement CRM.
2. Fournir la liste des LP actives, les règles et destinations des 59 pages sans identifiant détecté, et l'accès ou les spécifications des iframes externes. Qualifier leurs formulaires avant toute intégration.
3. Sur un environnement de recette, tester pour chaque campagne active : URL avec et sans paramètres, propagation entre étapes, SMS si applicable, accusé de réception CRM, ligne Sheets, déduplication et événement. Vérifier également la politique de consentement et le déclenchement des tags. Ne pas envoyer de données personnelles réelles sans autorisation.
4. Confirmer si l'attribution provenant d'une page précédente de la même session et les paramètres des liens sortants doivent être conservés ou supprimés : ce sont deux choix distincts de la suppression de valeurs inventées.
