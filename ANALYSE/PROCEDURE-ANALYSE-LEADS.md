# Analyse de la feuille Google Sheets de leads — procédure

> **Statut au 9 novembre 2026** : la feuille `1hR_97nzusxCKG03wB-k1zRUOcikRREtnwSBXeqzfScQ`
> **n'est pas accessible** par l'agent — Google renvoie une page de connexion
> (`accounts.google.com/signin`), ce qui signifie qu'elle n'est pas partagée en lecture publique
> (« Tout le monde disposant du lien ») ou que l'accès est restreint au domaine.
>
> Le seul connecteur Google disponible dans cette session est **Google Docs**, qui ne lit pas les
> Sheets. Il faut donc soit ouvrir le partage, soit exporter la feuille en CSV.

## Comment débloquer l'analyse (3 options, par ordre de simplicité)

### Option A — Partager en lecture (le plus rapide)
Dans la feuille : **Partager** → **Accès général** → **Tout le monde disposant du lien** → rôle
**Lecteur**. Prévenir que la feuille contient des données personnelles réelles : préférer une
**copie anonymisée** pour l'analyse.

### Option B — Exporter et déposer le fichier
`Fichier → Télécharger → Valeurs séparées par des virgules (.csv)`, puis déposer le fichier dans
le dépôt sous `ANALYSE/data/leads-export.csv` (⚠️ cette option fait entrer des données personnelles
dans Git : **anonymiser d'abord** — supprimer nom, prénom, téléphone, e-mail).

### Option C — Décrire les colonnes
Si aucune donnée ne peut sortir, il suffit de me donner **la liste des en-têtes de colonnes**.
Je peux alors écrire le script d'analyse et vous le faire tourner localement.

## Ce qu'il faut vérifier en priorité (dans cet ordre)

### 1. La feuille est-elle complète ? (le point le plus important)

La règle métier est : *tout lead de la feuille est aussi dans le CRM*. La question inverse n'est
pas tranchée : **tout lead du CRM est-il dans la feuille ?**

| Résultat | Interprétation |
|---|---|
| Volumes identiques (feuille ≈ CRM) | chaîne saine, la feuille est un bon miroir |
| Feuille < CRM | des `formId` ne sont pas routés vers le script Sheets → leads invisibles dans la feuille |
| Feuille > CRM | incohérence inverse : à creuser côté CRM |

### 2. Quelles pages produisent réellement des leads ?

Croiser la colonne `form_id` (ou `source`) de la feuille avec les 146 pages du dépôt :

- les pages du **statut A** (84) doivent apparaître ;
- les pages du **statut C** (37, formulaire non marqué) : **apparaissent-elles ?**
  - **Oui** → un mécanisme historique capte bien, mon audit statique est trop strict, il faut
    l'identifier (probablement un gestionnaire dans `script.js`, comme sur `solutions-agv-amr`) ;
  - **Non** → ces pages perdent effectivement des leads. C'est la priorité n°1.
- les pages du **statut D** (23, sans formulaire) ne doivent **pas** apparaître.

### 3. Quelles colonnes de traçabilité sont réellement remplies ?

Le `lead-handler.js` envoie potentiellement : `source`, `categorie`, `utm_*`, `ltm_*`, `gclid`,
`gbraid`, `wbraid`, `fbclid`, `msclkid`, `ttclid`, `page_url`, `page_referrer`, `user_agent`,
`langue`, `telephone_verifie`, `civilite`, `ville`, `solution`, `enjeu`, `question_1..3`,
`reponse_1..3`, `autre_info_fj`, `website` (honeypot), `id_lead`.

À mesurer :
- **taux de remplissage par colonne** → révèle ce qui ne fonctionne pas en vrai
  (ex. si `gclid` est vide à 100 % alors que le trafic est payant, le tracking est cassé) ;
- **`telephone_verifie`** : quelle proportion de `oui` ? → mesure l'impact réel de l'idée 3 du plan
  d'optimisation (« la vérification SMS est un péage ») ;
- **`website`** (honeypot) : des valeurs non vides ? → du spam passe ;
- **`enjeu` / `solution`** : troncature à 500 caractères ? → perte d'information dans le CRM ;
- **`source`** : proportion de `LP …` (source de secours) vs vraie campagne → mesure la perte
  d'attribution (risque F3 du mémoire).

### 4. Détecter les doublons

Un lead peut être envoyé deux fois (double clic, reprise après erreur). Le `lead-handler.js` a une
garde `sending`, mais **aucune déduplication serveur**. Compter les `id_lead` dupliqués et les
couples (téléphone, jour) identiques donne le taux de doublons réel.

### 5. Détecter la fraude et les formulaires de test

Compter les leads par : téléphone identique, nom suspect (`test`, `aaa`, `azerty`), domaine e-mail
jetable, `website` rempli.

## Script d'analyse à exécuter (à créer quand les données seront accessibles)

```python
#!/usr/bin/env python3
"""Analyse de la feuille de leads — à lancer une fois l'export CSV disponible.
Usage : python3 ANALYSE/scripts/analyser_leads.py ANALYSE/data/leads-export.csv
Aucune donnée n'est écrite ailleurs que dans ANALYSE/data/rapport-leads.md (agrégats only)."""
import csv, sys
from collections import Counter, defaultdict
from pathlib import Path

def main(path):
    rows = list(csv.DictReader(Path(path).open(encoding='utf-8', newline='')))
    print(f"{len(rows)} leads · {len(rows[0])} colonnes")
    # 1. remplissage par colonne
    fill = {c: sum(1 for r in rows if (r.get(c) or '').strip()) for c in rows[0]}
    for c, n in sorted(fill.items(), key=lambda kv: -kv[1]):
        print(f"  {c:24} {n:6}/{len(rows)} ({n/len(rows)*100:5.1f} %)")
    # 2. répartition par form_id / source
    for key in ('form_id', 'source', 'telephone_verifie'):
        if key in rows[0]:
            print(f"\n-- {key} --")
            for v, n in Counter((r.get(key) or '(vide)').strip() for r in rows).most_common(20):
                print(f"   {v:40} {n:6}")
    # 3. doublons
    if 'id_lead' in rows[0]:
        ids = Counter(r['id_lead'] for r in rows if r.get('id_lead'))
        print(f"\nDoublons d'id_lead : {sum(v-1 for v in ids.values() if v>1)}")
    if 'telephone' in rows[0]:
        tel = Counter(r['telephone'] for r in rows if r.get('telephone'))
        print(f"Téléphones en doublon : {sum(v-1 for v in tel.values() if v>1)}")

if __name__ == '__main__':
    main(sys.argv[1])
```

## En attendant l'accès : ce qui est déjà acquis

L'information « **un lead dans la feuille = un lead dans le CRM** » suffit à lever les deux risques
majeurs de mon analyse :

- ❌ ~~« On ne sait pas si un lead arrive réellement »~~ → **il arrive** ;
- ❌ ~~« Le CORS de l'API SMS est peut-être cassé »~~ → **il fonctionne** sur les domaines en service.

Le risque résiduel est désormais **le cas dégradé** (Sheets répond OK, CRM en échec) et les
**nouveaux domaines** (CORS à retester à chaque déploiement).

---

*Procédure établie le 9 novembre 2026. La feuille n'étant pas accessible, aucune donnée de lead
n'a été lue ni analysée dans cette session.*
