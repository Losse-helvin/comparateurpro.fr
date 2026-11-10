# Comparaison avec le PDF « tableau-lien-formid-dossier »

## Résultat

Le PDF fourni contient **147 lignes** : les 147 dossiers existent dans le dépôt et correspondent exactement aux 147 dossiers du registre `ANALYSE/data/registre-formid.json`, y compris les 8 dossiers imbriqués. Pour chaque ligne, le couple **dossier / form_id du PDF correspond au registre**. Les 147 identifiants du PDF sont distincts.

Le [tableau de comparaison détaillé](data/comparaison-pdf-lien-formid-dossier.csv) reprend les 147 lignes, les identifiants détectés dans le HTML et les scripts locaux chargés, le nombre de formulaires et d'iframes et l'URL canonique déclarée dans la page.

## Identifiant dans le code

| Résultat du contrôle statique | Pages |
|---|---:|
| Identifiant détecté et conforme à celui du PDF | 88 |
| Aucun identifiant détecté par ce contrôle | 59 |
| Identifiant détecté divergent | 0 |

Parmi les 59 pages sans identifiant détecté, **36 possèdent au moins un formulaire HTML** ; les autres peuvent être des wrappers, pages de remerciement ou contenus. Un formulaire n'est pas nécessairement un formulaire final de lead : il peut être une étape de qualification ou un formulaire de préférences. Exemple : `assurance-consultants-societe-conseil` est un wrapper qui charge une iframe distante ; l'identifiant de la page distante ne peut pas être vérifié à partir du parent.

La présence d'un identifiant détecté ne confirme pas à elle seule que tous les formulaires l'envoient au CRM, ni que le CRM l'a enregistré et routé. L'absence de détection ne prouve pas non plus l'absence d'un envoi dynamique ou externe. Ne pas ajouter des identifiants en aveugle aux pages de qualification et aux wrappers.

## Liens du PDF et adresses déclarées

Les liens du PDF sont de la forme `comparateurpro.fr/<dossier>/`. Sur les **142 pages qui déclarent une URL canonique**, cette URL diffère de celle du PDF : elle est généralement de la forme `https://<campagne>.lp.comparateurpro.fr/`. Exemple :

- PDF : `comparateurpro.fr/acces-internet-et-telephonie-pro/`
- Canonical HTML : `https://acces-internet-et-telephonie-pro.lp.comparateurpro.fr/`

Cinq pages n'ont pas de canonical : `LP_reference`, `mentions-legales`, `politique-de-confidentialite-donnees-personnelles`, `site-assurances` et `vehicules-utilitaires`. Le dossier `assurance-consultants-societe-conseil - Copie` contient des espaces dans le lien PDF, qui nécessiteraient un encodage si ce lien devait être utilisé comme URL.

**Une différence de forme ne prouve pas qu'un lien soit cassé** : les chemins du PDF peuvent être des routes ou redirections. Aucune vérification HTTP ou de configuration d'hébergement n'a été faite. Il faut confirmer auprès de l'équipe chargée de l'hébergement quelles adresses sont réellement publiées avant de modifier les liens ou les canonicals.

## Tracking

L'inventaire local ne relève pas de valeurs non vides dans les champs cachés et attributs de suivi reconnus des 147 pages. Il ne couvre pas toutes les valeurs potentiellement injectées par les scripts, les iframes distantes ou le CRM. Les paramètres de liens sortants et les données réellement collectées plus tôt dans la même session sont distincts de valeurs par défaut inventées ; leur conservation reste une décision métier. Voir [le contrôle précédent](CONTROLE-FORMID-TRACKING.md).

## Méthode et limites

PDF analysé : `tableau-lien-formid-dossier.pdf`, 4 pages, SHA-256 `375919038bc779317d1b1a88a5f0027547e39c105462b521f41590194d5d14a0`. Extraction des 147 lignes avec pypdf, puis rapprochement par dossier avec le registre et l'outil `tools/audit_identifiants_lp.py`. Ce dernier inspecte statiquement les formulaires et les littéraux d'identifiant dans `lead-handler.js` et `script.js` lorsqu'ils sont chargés localement ; il n'exécute pas les scripts et n'inspecte pas les iframes externes. Comparaison des liens aux balises canonical HTML, indépendamment du protocole et du slash final.

Aucune page n'a été modifiée pour cette vérification. Prochaine étape : qualifier les 59 pages non détectées, confirmer les URL publiées, puis tester les campagnes actives de bout en bout avec réception effective côté CRM et, le cas échéant, Sheets.
