# Mise à niveau de `vehicules-de-societe` — 11/11/2026

La page `vehicules-de-societe/` a été ajoutée au dépôt par un commit direct sur `main` (`8bf1c09`, « Add files via upload »). Elle n'avait reçu **aucune** des révisions des 10 et 11/11. Ce document liste ce qui a été appliqué, et les deux choses qui restent à décider.

## État à l'arrivée

| Élément | Valeur trouvée |
|---|---|
| `formId` | `ADW_LP_VEHICULES_DE_SOCIETE` (hors format) |
| Consent Mode V2 | `denied` (4 signaux) |
| `source` dans `UBE_CONFIG` | `'LP VEHICULES DE SOCIETE'` |
| Champ caché `source` | `value="LP VEHICULES DE SOCIETE"` |
| `localStorage` | suffixe `' TYP'` |
| Repli de catégorie | `textValue('categorie')` |
| `mobile-ux.js` | absent |
| Balise canonical | absente |
| `sitemap.xml` / `robots.txt` | absents |

## Ce qui a été appliqué

1. **`formId` → `a13749586307084i`** — format `[a-z][14 chiffres][a-z]`, unique parmi les 147. Généré de façon déterministe (`sha256` du chemin), donc rejouable à l'identique.
2. **Consent Mode V2 : 4 signaux → `granted`**, comme les 135 pages révisées le 10/11.
3. **Tracking sans condition** : `analyticsGranted()`, `marketingGranted()`, `trackingGranted()`, `trackingKeyGranted()` renvoient `true`, comme partout ailleurs.
4. **Valeurs par défaut supprimées** : champ caché `source` vidé, `source: ''` dans la config, condition `'SOURCE PAR DEFAUT'` neutralisée, suffixe `' TYP'` retiré, repli `textValue('categorie')` retiré.
5. **`mobile-ux.js`** copié depuis `tools/` (les 139 autres pages l'ont) et référencé.
6. **Canonical ajoutée** : `https://vehicules-de-societe.lp.comparateurpro.fr/`.
7. **Registres et inventaires mis à jour** : 147 entrées (`registre-formid.json`, `test/registre-formid.json`, `url-formid.json`, `url-formid.csv`, `URL-formid-LP.xls`, `URL-formid-LP.pdf`, `LISTE-INDEX-FORMID.txt`).

## Vérification en exécution (jsdom, handler réel)

| URL | `source` | `categorie` | `gclid` |
|---|---|---|---|
| sans paramètre | `""` | `""` | absent |
| `?utm_source=google&categorie=138&gclid=XYZ` | `"google"` | `"138"` | `"XYZ"` |

`node --check` : 0 échec sur les 5 fichiers JS du dossier. `npm test` : **361/368**, aucun test supplémentaire en échec.

## Deux écarts avec le reste du site, volontairement non corrigés

**1. Le module SMS est chargé mais inactif.** `index.html` référence bien `verification-sms.js` (comme les 87 handlers qui vérifient les numéros), mais l'en-tête de son `lead-handler.js` indique « SANS SMS : aucun endpoint de code ». La page ne vérifie donc pas les numéros. Ce n'est pas une donnée par défaut : c'est un choix de parcours qui était déjà là. Dites-moi si cette LP doit vérifier les SMS comme les autres.

**2. Sa logique de soumission diffère des 87 autres handlers.** Elle envoie le lead dès que le CRM *ou* le Google Sheet répond (`if (crm.ok || sheet.ok)`), alors que les autres attendent une **confirmation** explicite (`crm.result.confirmed`) avant d'afficher le succès. Conséquence : cette page peut afficher « Merci » alors que le lead n'a pas été enregistré.

Les deux corrections toucheraient la logique métier, pas les données par défaut. Je ne les ai pas appliquées sans votre accord — dites-moi si vous les voulez alignées.

## Ce qui reste à faire côté CRM

Le `formId` **`a13749586307084i` doit être créé dans HelloLead avant la mise en ligne**, comme les autres. Tant qu'il n'existe pas, les leads de cette page partent dans le vide.

## Outillage ajouté

```bash
python3 tools/aligner_lp.py --dossier <dossier> --categorie <code> --libelle "<titre>"          # simulation
python3 tools/aligner_lp.py --dossier <dossier> --categorie <code> --libelle "<titre>" --apply
python3 tools/maj_inventaire.py   # régénère xls / csv / json depuis les registres
```

`aligner_lp.py` applique les mêmes règles à toute future LP déposée dans le dépôt, et refuse un `formId` déjà pris ou hors format.
