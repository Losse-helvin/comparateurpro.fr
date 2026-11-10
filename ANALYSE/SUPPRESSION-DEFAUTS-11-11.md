# Suppression totale des données par défaut — 11/11/2026

Suite au constat « il existe toujours des sources par défaut dans quelques LP ». Le contrôle porte cette fois sur **le code réellement exécuté et sur les valeurs figées dans le HTML**, pas seulement sur les constantes du handler.

## Ce qui restait, et qui est maintenant supprimé

| # | Trace | Où | Volume |
|---|---|---|---|
| 1 | `value="SOURCE PAR DEFAUT"` | champ caché `source` | **110 pages** |
| 2 | `value="LP VEHICULES…"`, `value="ADW"`, `value="LP VEHICULES UTILISATEURS"` | champ caché `source` | 3 pages |
| 3 | `value="135"`, `"160"`, `"125"`, `"192"`, `"117"`, `"201"`, `"200"`, `"138"` | champ caché `categorie` | 15 pages |
| 4 | `data-source="ADW"` | balise `<form>` | 1 page |
| 5 | `categorieCode: '…'` | `UBE_CONFIG` | **87 handlers** |
| 6 | `initialCategory` (repli de catégorie) | 87 handlers + 1 `script.js` | 88 fichiers |
| 7 | `(data.source || '') + ' TYP'` | `localStorage` | 87 handlers |
| 8 | `.val()+' TYP'` | `localStorage` | **139 `script.js`** |
| 9 | `input.value === 'SOURCE PAR DEFAUT'` | condition de remplissage | 87 handlers |

**700 actions sur 340 fichiers.** Vérifié après coup, hors dossier de sauvegarde :

```
SOURCE PAR DEFAUT : 0 fichier
categorieCode     : 0 fichier
initialCategory   : 0 fichier
' TYP'            : 0 occurrence
champ caché tracking non vide : 0
data-source non vide          : 0
```

## Effet mesuré en jsdom

`assurance-tns`, sans consentement, handler réellement exécuté :

| URL | `source` | `categorie` | `gclid` | champs cachés |
|---|---|---|---|---|
| aucun paramètre | `""` | `""` | absent | `source="" categorie=""` |
| `?utm_source=google&categorie=999&gclid=ABC` | `"google"` | `"999"` | `"ABC"` | remplis par l'URL |

Idem sur `LP_reference` et `vehicules-utilitaires`. Si l'URL n'apporte rien, **rien n'est transmis** : plus aucune valeur inventée ne part vers le CRM.

## Ce qui a été volontairement conservé

- **Attributs `data-categorie` / `data-source` vides** : le mécanisme reste, la valeur est vide.
- **`ltm_source=ADW_…` dans les liens « Vous êtes assureur ? »** (18 pages) : ce sont des liens sortants vers hellolead.pro, pas de la donnée de tracking. Un `ltm_source` sur un lien n'est pas une valeur par défaut du formulaire, et le supprimer casserait l'attribution de ces liens. Dites-moi si vous les voulez vides aussi.
- **Titres de page « Assurance TNS Pro V2 - ADW »** (2 pages) : ce sont des noms de campagne dans des `<title>`, pas des données de formulaire.
- **`data-categorie` sur `script.js` tiers (139 fichiers)** : le bundle Webflow contient le mot `TYP` dans du code minifié sans rapport (`TRAFFIC_TYPE`). Aucune valeur par défaut n'y subsiste.

## Vérifications

| Contrôle | Résultat |
|---|---|
| `node --check` sur les 87 handlers | **0 échec** |
| `node --check` sur les 140 `script.js` | **0 échec** |
| `npm test` | **361 / 368** = les 7 échecs préexistants (`assurance-consultants-societe-conseil`), aucune régression |
| Journal de suppression | `ANALYSE/data/journal-suppression-defauts.json` |

## Réversibilité

```bash
python3 tools/supprimer_defauts.py             # simulation, n'écrit rien
python3 tools/supprimer_defauts.py --apply
python3 tools/supprimer_defauts.py --rollback  # restaure depuis .sauvegarde-defauts/
```

`.sauvegarde-defauts/` est exclu de Git.
