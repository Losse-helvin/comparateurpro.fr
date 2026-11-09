# `ANALYSE/` — mémoire technique du dépôt `comparateurpro.fr`

Ce dossier contient l'analyse complète du dépôt réalisée le **9 novembre 2026**.
Il ne modifie **aucune** landing page : il observe, mesure et documente.

## Par où commencer

| Vous êtes… | Lisez |
|---|---|
| Décideur / responsable marketing | [`MEMOIRE-ANALYSE.md`](MEMOIRE-ANALYSE.md) — sections 1 et 9 |
| Développeur qui reprend le projet | [`MEMOIRE-ANALYSE.md`](MEMOIRE-ANALYSE.md) — sections 2, 3 et 5 |
| Responsable de la mise en production | [`REGISTRE-ACTIONS.md`](REGISTRE-ACTIONS.md) |
| Curieux du détail d'une page précise | [`fiches/<dossier>.md`](fiches/) |
| Celui qui reprend le travail dans 6 mois | [`JOURNAL-TRAVAIL.md`](JOURNAL-TRAVAIL.md) |

## Contenu

```
ANALYSE/
├── MEMOIRE-ANALYSE.md      le document de référence (état des lieux + plan d'action)
├── REGISTRE-ACTIONS.md     les actions décidables, avec critères de réussite
├── JOURNAL-TRAVAIL.md      chronologie, faits mesurés, hypothèses, erreurs corrigées
├── README.md               ce fichier
├── fiches/                 146 fiches : une par page du dépôt
├── data/
│   ├── inventaire.json     toutes les mesures, page par page (source de vérité)
│   ├── inventaire.csv      le même contenu, ouvrable dans un tableur
│   ├── stats.json          les chiffres de synthèse
│   ├── orphelins.json      médias non référencés + références cassées
│   └── doublons.csv        groupes de fichiers identiques (empreinte MD5)
└── scripts/
    ├── inventaire_exhaustif.py   mesure les 146 pages → data/
    ├── generer_fiches.py         produit fiches/ à partir de data/
    └── audit_poids.py            diagnostic de redondance (LECTURE SEULE)
```

## Reproduire l'analyse

Aucune dépendance externe : Python 3.9+ suffit.

```sh
# 1. Mesurer toutes les pages (≈ 1 s) → ANALYSE/data/
python3 ANALYSE/scripts/inventaire_exhaustif.py

# 2. (Re)générer les 146 fiches
python3 ANALYSE/scripts/generer_fiches.py

# 3. Diagnostic de redondance et de poids (≈ 3 s, lecture seule)
python3 ANALYSE/scripts/audit_poids.py
python3 ANALYSE/scripts/audit_poids.py --csv --gros-fichiers 5

# 4. Vérifier l'état du parc de capture (script existant du dépôt)
python3 tools/audit_fonctionnalites.py
```

## Les quatre statuts d'une page

Recalculés à chaque exécution du script n°1 :

| Statut | Critère | Nombre (9 nov. 2026) |
|---|---|---|
| **A** — capture standard complète | formulaire marqué + handler chargé + SMS chargé + bon ordre | **84** |
| **B** — modules présents, non chargés | fichiers là, `<script>` absent | **2** |
| **C** — formulaire non raccroché | `<form>` existe, `data-ubepro-lead="1"` absent | **37** |
| **D** — page sans formulaire | contenu, légale, remerciement, wrapper | **23** |

> Le chiffre à suivre dans le temps est celui du **statut C**. S'il ne baisse pas, rien n'avance
> réellement sur le plan commercial.

## Avertissement de méthode

Toutes les mesures sont **statiques** : lecture du HTML, du CSS et du JS. Aucune page n'a été
exécutée dans un navigateur, aucun appel réseau réel n'a été effectué vers le CRM, l'API SMS ou
Google. Les mentions « code détecté » ne valent donc **pas** preuve de fonctionnement en production.
Voir la section « Hypothèses et limites » du journal de travail.
