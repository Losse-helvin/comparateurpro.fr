#!/usr/bin/env python3
"""
Génère ANALYSE/fiches/<site>.md : une fiche mémoire par dossier de landing page.
S'appuie sur ANALYSE/data/inventaire.json produit par inventaire_exhaustif.py.

Usage : python3 ANALYSE/scripts/generer_fiches.py
"""
from __future__ import annotations

import json
import re
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = json.loads((ROOT / 'ANALYSE' / 'data' / 'inventaire.json').read_text(encoding='utf-8'))
OUT = ROOT / 'ANALYSE' / 'fiches'
OUT.mkdir(parents=True, exist_ok=True)

# --- familles fonctionnelles (regroupement métier) ---------------------------
FAMILLES = [
    ('Référence technique', lambda s: s in ('LP_reference', 'vehicules-utilitaires')),
    ('Wrappers iframe', lambda s: s in ('assurance-consultant-societe-conseil-v2',
                                        'assurance-consultants-societe-conseil',
                                        'assurance-consultants-societe-conseil - Copie',
                                        'assurance-estheticiennes-instituts-beaute',
                                        'typ-categories', 'typ-categ')),
    ('Pages légales / site vitrine', lambda s: s in ('mentions-legales',
                                                    'politique-de-confidentialite-donnees-personnelles',
                                                    'site-assurances', 'accueil')),
    ('TIP / formulaires', lambda s: s.startswith('typ-')),
    ('Assurance', lambda s: s.startswith(('assurance', 'rc-pro-consultant'))),
    ('Remerciement', lambda s: s.startswith('remerciement')),
    ('Récompense / avantages salariés', lambda s: s.startswith(('edenred', 'ticket-restaurant',
                                                               'celebrez', 'une-rentree', 'too-good'))),
    ('Énergie', lambda s: s.startswith(('energie', 'primagaz', 'panneaux', 'form-panneaux',
                                       'intuis'))),
    ('Télécom / monétique', lambda s: s.startswith(('acces-internet', 'paritel', 'cartes-carburant'))),
    ('Flotte / géolocalisation / sécurité', lambda s: s.startswith(('geolocalisation', 'geo', 'suivi',
                                                                   'securite', 'solutions', 'radius',
                                                                   'still', 'nettoyage', 'sauvie'))),
    ('Automobile / utilitaire', lambda s: s.startswith(('renault', 'nissan', 'mercedes', 'hyundai',
                                                       'toyota', 'lexus', 'volvo', 'voiture', 'fiat',
                                                       'mitsubishi', 'dacia', 'alfa', 'ayvens', 'canal',
                                                       'ecomobility', 'automobile', 'vehicules'))),
    ('Outils / divers', lambda s: s.startswith(('form', 'formulaire', 'template', 'sage', 'site'))),
]

# --- notes d'expertise ciblées (rédigées à la main) --------------------------
NOTES = {
    'LP_reference': """Cette LP est la **référence fonctionnelle du dépôt**. Son `lead-handler.js` (40 Ko) et son
`verification-sms.js` (14,5 Ko) sont les modèles copiés-partout ailleurs. Toute évolution du contrat
CRM / Sheets / SMS doit partir d'ici puis être propagée. Elle n'a volontairement ni `robots.txt`
ni `sitemap.xml` et son titre est « Véhicules de société » alors que le dossier s'appelle
`LP_reference` : ne pas s'y fier pour l'indexation.""",
    'vehicules-utilitaires': """Variante de `LP_reference` (35 Ko d'écart dans `script.js`, 3 Ko dans `style.css`).
C'est une des deux pages « modèles » avec le même `formId` de référence `ADW_LP_VEHICULES_DE_SOCIETE`.
Absence de `robots.txt` / `sitemap.xml` : à trancher avant mise en ligne.""",
    'assurance-tns': """Bonne élève documentaire : `RAPPORT-MODIFICATIONS.md` (5,2 Ko) + 4 documents dans `docs/`
(analyse fonctionnelle, configuration CRM/Sheets/GTM, vérification SMS, embed Webflow) + `Code.gs`.
C'est le **patron de documentation** à répliquer sur les 137 autres dossiers.
Défaut résiduel : 9 balises `<h1>` dans le HTML (héritage Webflow, cf. rapport).""",
    'assurance-tns-pro-v2-adw': """Sous-produit de `assurance-tns` (même engine, `formId` distinct).
Contient un fichier de vérification Google Search Console (`google1560e922014e5a8e.html`)
qui n'existe nulle part ailleurs : preuve d'une mise en ligne réelle de ce dossier.""",
    'agriculteur': """Version « fonctionnelle » de l'assurance agriculteur (avec `docs/` complet et `Code.gs`),
distincte de `assurance-agriculteur`, `assurance-agriculteur-v2` et `assurance/agriculteur`.
⚠ **Collision de `formId`** avec `assurance-agriculteur` : `ADW_LP_ASSURANCE_AGRICULTEUR`. Les deux
dossiers enverront des leads impossibles à distinguer côté CRM. `sitemap.xml` présent mais pas de
`style.css` à la racine : vérifier que la feuille est bien chargée.""",
    'assurance-agriculteur': """LP historique de l'assurance agriculteur. Partiellement intégrée
(`RAPPORT-INTEGRATION.md`) mais **aucun formulaire marqué** `data-ubepro-lead="1"` dans le HTML :
le module de capture n'est donc pas raccroché. Collision de `formId` avec `agriculteur`.""",
    'assurance-agriculteur-v2': """⚠ **Page amputée** : `index.html` fait 7,9 Ko et ne contient **aucune balise
`<form>`**, alors que le dossier pèse 6,2 Mo et charge un `script.js` de 1,5 Mo. Le formulaire a disparu
lors d'une édition. Contient pourtant 9 `<h1>` et le conteneur `GTM-53SH7D7F`. À restaurer d'urgence
ou à retirer du lot.""",
    'assurance-consultant-societe-conseil-v2': """**Wrapper iframe** (2,9 Ko) qui embarre `https://www.ubepro.com/assurance-consultant-conseil-v2/`.
Apporte le pont `bridge.js` (consentement + URL parente + relais SMS) et `GTM-53SH7D7F`.
Pourtant ce dossier pèse 5,9 Mo et sa racine 1,6 Mo : un `script.js` de 1,5 Mo et les polices sont
chargés **pour rien**, la page ne les utilise pas. Suppression = ~5,5 Mo gagnés.""",
    'assurance-consultants-societe-conseil': """Wrapper iframe **identique au caractère près** à
`assurance-consultant-societe-conseil-v2/index.html` (même `md5`). C'est un doublon pur.
C'est aussi la page que ciblent 7 tests de `tests/lead-reference.test.cjs`, écrits pour une vraie LP
avec formulaire : d'où les **7 échecs** de la suite (`w.smsVerification` indéfini). `lead-handler.js`
et `verification-sms.js` sont présents dans le dossier mais **jamais chargés** par le HTML.""",
    'assurance-consultants-societe-conseil - Copie': """⚠ Dossier système « Copie » committé par erreur. Espace dans le nom → casse toute
automatisation en ligne de commande et toute URL propre. Non listé dans `ordre-sites.txt`.
`formId` identique à l'original. À supprimer.""",
    'assurance-multirisques': """Doublon partiel de `assurance/multirisques` (versions différentes, pas identiques).
À fusionner ou à documenter : deux LP concurrentes pour la même offre brouillent l'attribution.""",
    'assurance-iard-v2': """⚠ **17 balises `<h1>`** dans une seule page — record du dépôt. Héritage direct de
l'export Webflow (titres stylés en `h1`). Impact SEO réel. Formulaires présents mais non marqués.""",
    'energie': """Famille énergie en double : `energie` (intégrée, 8,7 Mo) et `energie-v2` (7,5 Mo, formulaire
sans marqueur de capture). Décider laquelle est la version de production.""",
    'energie-v2': """Formulaire présent mais **non marqué** `data-ubepro-lead` : la capture standard ne
s'applique pas. `GTM-WMVZJKS` présent. Version « propre » graphiquement, capture à raccorder.""",
    'geolocalisation': """Famille en triple : `geolocalisation` (intégrée), `geolocalisation-v2` (formulaire non
marqué, `GTM-WMVZJKS`), `geolocalisation-de-flotte` (intégrée) et `geo` (page de contenu).
Quatre dossiers, une seule offre commerciale.""",
    'geolocalisation-v2': """11 Mo pour 3 063 caractères de texte. ~90 % du poids est un `script.js`
Webflow de 1,5 Mo + un lot d'images quasi toutes inutilisées.""",
    'ticket-restaurant': """Famille ticket-restaurant = 5 dossiers quasi identiques (`ticket-restaurant`,
`ticket-restaurant-`, `ticket-restaurant-v2`, `ticket-restaurant-septembre`,
`ticket-restaurant-septembre-btp`) pour ~36 Mo, plus 5 dossiers « remerciement » (~39 Mo).
Le suffixe `-` final est une anomalie de nommage à corriger.""",
    'ticket-restaurant-': """⚠ Nom de dossier terminant par un tiret (`ticket-restaurant-`) : erreur de saisie.
`robots.txt` et `sitemap.xml` pointent vers un domaine qui n'a pas ce tiret.""",
    'canal': """Dossier le plus lourd du dépôt (28,5 Mo) : vidéos `videos/` embarquées. Aucun formulaire marqué,
aucun `lead-handler.js` : c'est une page de présentation pure. Si la vidéo est le cœur du message,
envisager un hébergement externe (YouTube/Vimeo) plutôt que 20 Mo dans Git.""",
    'lexus-lbx-2': """21,9 Mo. Version 2 de `lexus-lbx` (11 Mo). Les deux coexistent ; la v2 embarque plus de
médias. Aucun des deux n'a de `robots.txt`... si, la v2 en a un. Vérifier laquelle est annoncée.""",
    'canal': """28,5 Mo : le plus gros dossier du dépôt, essentiellement des vidéos (`videos/`).
Aucun `lead-handler.js`, aucune capture : page vitrine.""",
    'solutions-agv-amr': """Dossier technique « solutions AGV/AMR » (robotique industrielle). Deux formulaires HTML
mais **aucun marqué** ; `lead-handler.js` pourtant présent (13,5 Mo de dossier).
C'est la source du schéma Google Sheets « AGV/AMR » (`solution` / `enjeu`) utilisé par toutes les LP
d'assurance : ne pas casser `docs/Code.gs`.""",
    'site': """Page « site » sans formulaire ni capture. Rôle ambigu avec `site-assurances` et `accueil`.
Candidat à la suppression ou à la fusion.""",
    'site-assurances': """Site vitrine multi-pages (7 pages HTML, 63 Ko d'index) — le seul dossier du dépôt
avec une vraie arborescence de contenu. `README.md` explique comment le lancer
(`python3 -m http.server 4000`). Aucun lien vers les LP du dépôt : c'est un univers séparé.""",
    'accueil': """Porte d'entrée `accueil.lp.comparateurpro.fr`. Un formulaire, aucune capture marquée,
GTM absent, `rapport-site.md` signale 0 H1. Page la plus stratégique et la moins équipée.""",
    'template-2': """Dossier « template » : squelette Webflow réutilisable. 24 médias orphelins, formulaire non
marqué, aucun GTM. Sert de gabarit — à sortir du périmètre de production.""",
    'formulaire': """Deux dossiers proches : `formulaire` et `formulaire-globale`. Le second est intégré
(handler + GTM), le premier est une page de contenu sans capture. Risque de confusion.""",
    'securite-professionnels': """27 médias orphelins et 29 polices pour une seule page : illustration typique de
l'export Webflow « tout compris » où 80 % des actifs ne sont jamais affichés.""",
    'assurance-estheticiennes-instituts-beaute': """Page **parente iframe** : charge
`../assurance-estheticiennes-institut-beaute/` dans un cadre. C'est le mécanisme d'embarquement
historique (avant les wrappers `bridge.js`). Attention : chemin relatif, donc dépend de la
profondeur de déploiement.""",
    'assurance-estheticiennes-institut-beaute': """Page **enfant** iframée par
`assurance-estheticiennes-instituts-beaute`. Formulaire présent mais non marqué ; c'est le cas
« spécial » traité par `tests/estheticiennes-original.test.cjs`.""",
    'typ-categories': """Contient 6 iframes pointant vers les pages « thank you » de la famille `typ-formulaires`.
Un vrai routeur de tunnels, sans capture propre. Très fragile : tout repose sur des chemins relatifs
`../typ-formulaires-…`.""",
    'typ-formulaires-caisses-thank-you-page': """Famille TIP (`typ-`) : 12 dossiers, 73 Mo, 5 avec capture.
Ces pages sont majoritairement des « thank you pages » et des formulaires de qualification, pas des LP
commerciales. Elles n'ont ni `robots.txt` ni `sitemap.xml` dans certains cas.""",
    'remerciement-ticket-restaurant': """Page de remerciement : **5 dossiers `remerciement*` = 39 Mo, 0 capture**.
Ce sont des destinations post-conversion, donc sans formulaire — normal — mais elles représentent
quand même 39 Mo et devraient être allégées au même titre que les LP.""",
    'nissan-juke': """15,7 Mo. Le `rapport-site.md` d'origine signalait un hôte externe `htpps`
(faute de frappe d'un `https:`) : trace d'un bug d'extraction corrigé depuis, mais elle illustre
la nécessité de relire les rapports automatiques.""",
    'edenred-kadeos': """L'un des 9 dossiers signalés « ressource en `http://` non sécurisée » par mon
audit : contenu mixte, bloqué par les navigateurs récents pour les ressources actives.""",
}


def famille(site: str) -> str:
    site = site.split('/')[-1]
    for name, test in FAMILLES:
        if test(site):
            return name
    return 'Autres'


def bloc_verdict(r: dict) -> str:
    """Statut synthétique de la page."""
    if r['nb_formulaires_marques'] > 0 and r['lead_handler_charge'] and r['sms_charge'] and r['ordre_modules_ok']:
        return '✅ **Capture standard complète** (handler + SMS + ordre correct) — reste à valider la réception réelle.'
    if r['nb_formulaires'] == 0:
        return '⚪ **Page sans formulaire** (contenu, remerciement, légale ou wrapper).'
    if r['nb_formulaires_marques'] == 0:
        return '🔴 **Formulaire présent mais NON marqué** `data-ubepro-lead="1"` → aucune capture standard.'
    if r['lead_handler'] and not r['lead_handler_charge']:
        return '🟠 **Modules présents mais non chargés** par le HTML.'
    return '🟠 **Intégration incomplète** — voir la section Constats.'


def md(r: dict) -> str:
    site = r['site']
    court = site.split('/')[-1]
    L: list[str] = []
    imbrique = ' (dossier imbriqué)' if '/' in site else ''
    L.append(f"# Fiche — `{site}`{imbrique}")
    L.append('')
    L.append(f"> Famille : **{famille(site)}** · Mémoire d'analyse du 2026-11-09 · "
             f"source : `ANALYSE/scripts/inventaire_exhaustif.py`")
    L.append('')
    L.append('## Verdict')
    L.append('')
    L.append(bloc_verdict(r))
    L.append('')
    if r['doublon_de']:
        L.append(f"> ⚠️ **Doublon de page** : `index.html` identique à {', '.join('`'+x+'`' for x in r['doublon_de'])}.")
        L.append('')

    L.append('## Identité')
    L.append('')
    L.append('| Champ | Valeur |')
    L.append('|---|---|')
    L.append(f"| Dossier | `{r['chemin']}` |")
    L.append(f"| Titre HTML | {('« ' + r['title'] + ' »') if r['title'] else '*(absent)*'} |")
    L.append(f"| `lang` | `{r['lang'] or 'non déclaré'}` |")
    L.append(f"| Canonical | `{r['canonical'] or '*(absente)*'}` |")
    L.append(f"| Meta description | {(str(len(r['meta_description'])) + ' caractères') if r['meta_description'] else '*(absente)*'} |")
    L.append(f"| H1 | {r['nb_h1']} · H2 : {r['nb_h2']} |")
    if r['h1']:
        L.append(f"| Texte du 1er H1 | « {r['h1'][0][:120]} » |")
    L.append('')

    L.append('## Poids et actifs')
    L.append('')
    L.append('| Mesure | Valeur |')
    L.append('|---|---|')
    L.append(f"| Poids total du dossier | **{r['mo_total']} Mo** ({r['fichiers']} fichiers) |")
    L.append(f"| `index.html` | {r['html_octets'] / 1024:.1f} Ko |")
    L.append(f"| Images | {r['nb_images']} ({r['mo_images']} Mo) |")
    L.append(f"| Polices | {r['nb_polices']} |")
    if r['nb_videos']:
        L.append(f"| Vidéos | {r['nb_videos']} |")
    L.append(f"| JS / CSS | {r['nb_js']} / {r['nb_css']} |")
    L.append(f"| Médias jamais référencés | **{r['nb_orphelins']}** |")
    L.append(f"| Références locales cassées | {r['nb_references_cassees']} |")
    L.append('')
    if r['orphelins']:
        L.append(f"Médias orphelins (extrait) : {', '.join('`'+x+'`' for x in r['orphelins'][:8])}"
                 + (' …' if r['nb_orphelins'] > 8 else ''))
        L.append('')

    L.append('## Capture et tracking')
    L.append('')
    L.append('| Élément | État |')
    L.append('|---|---|')
    L.append(f"| Formulaires HTML | {r['nb_formulaires']} |")
    L.append(f"| Formulaires marqués `data-ubepro-lead` | **{r['nb_formulaires_marques']}** |")
    L.append(f"| Champs du formulaire principal | {r['nb_champs_lead']} |")
    L.append(f"| `lead-handler.js` présent / chargé | {'oui' if r['lead_handler'] else 'non'} / {'oui' if r['lead_handler_charge'] else 'non'} |")
    L.append(f"| `verification-sms.js` présent / chargé | {'oui' if r['sms_module'] else 'non'} / {'oui' if r['sms_charge'] else 'non'} |")
    L.append(f"| Ordre des modules correct | {'oui' if r['ordre_modules_ok'] else 'non'} |")
    L.append(f"| GTM | {', '.join('`'+g+'`' for g in r['gtm']) or '*(aucun)*'} |")
    if r['ga4']:
        L.append(f"| GA4 | {', '.join('`'+g+'`' for g in r['ga4'])} |")
    if r['ads']:
        L.append(f"| Google Ads | {', '.join('`'+g+'`' for g in r['ads'])} |")
    L.append(f"| `formId` CRM | `{r['form_id'] or '—'}` |")
    if r['form_name']:
        L.append(f"| `formName` | `{r['form_name']}` |")
    if r['crm_mode']:
        L.append(f"| Mode transport CRM | `{r['crm_mode']}` {'(réception non confirmable)' if r['crm_mode'] == 'nocors' else ''} |")
    if r['source_secours']:
        L.append(f"| Source de secours | `{r['source_secours']}` |")
    if r['lead_handler_version']:
        L.append(f"| Version du handler | `{r['lead_handler_version']}` |")
    if r['public_landing_path']:
        L.append(f"| `publicLandingPath` | `{r['public_landing_path']}` |")
    L.append('')

    L.append('## SEO, indexation et conformité')
    L.append('')
    L.append(f"- `robots.txt` : {'présent' if r['robots'] else '**absent**'} · `sitemap.xml` : {'présent' if r['sitemap'] else '**absent**'}")
    if r['seo_flags']:
        L.append(f"- Points d'attention : {' · '.join(r['seo_flags'])}")
    else:
        L.append('- Aucun point d\'attention SEO détecté par les contrôles automatiques.')
    if r['hotes_externes']:
        L.append(f"- Hôtes tiers encore appelés : {', '.join('`'+h+'`' for h in r['hotes_externes'])}")
    if r['iframes']:
        L.append(f"- Iframes : {', '.join('`'+i[:80]+'`' for i in r['iframes'])}")
    if r['securite']:
        L.append(f"- Sécurité : {' · '.join(r['securite'])}")
    L.append('')

    L.append('## Documentation présente')
    L.append('')
    L.append(f"- Fichiers Markdown : {r['nb_md']} — {r['rapports'] or '*(aucun rapport)*'}")
    if r['dates_doc']:
        L.append(f"- Date(s) citée(s) dans les rapports : {', '.join(r['dates_doc'])}")
    L.append('')

    if r.get('doc_conflits'):
        L.append('## ⚠️ Contradictions documentaires détectées')
        L.append('')
        L.append('Le dossier contient de la documentation qui **affirme le contraire de ce que fait le code**. '
                 'Ne pas s\'y fier ; la source de vérité est `index.html` et les fichiers JS.')
        L.append('')
        for c in r['doc_conflits']:
            L.append(f'- {c}')
        L.append('')

    if NOTES.get(court):
        L.append('## Constats d\'expertise')
        L.append('')
        L.append(NOTES[court])
        L.append('')

    L.append('## Actions recommandées')
    L.append('')
    acts = []
    if r['nb_formulaires_marques'] == 0 and r['nb_formulaires'] > 0:
        acts.append('Qualifier le formulaire : marquer `data-ubepro-lead="1"` ou documenter pourquoi il ne doit pas l\'être.')
    if r['nb_formulaires_marques'] > 0 and not r['lead_handler_charge']:
        acts.append('Charger `lead-handler.js` (et `verification-sms.js` après lui) dans le HTML.')
    if r['nb_orphelins'] > 5:
        acts.append(f'Supprimer ou déplacer les {r["nb_orphelins"]} médias jamais affichés (gain de poids direct).')
    if not r['robots']:
        acts.append('Ajouter un `robots.txt`.')
    if not r['sitemap']:
        acts.append('Ajouter un `sitemap.xml`.')
    if r['nb_h1'] > 1:
        acts.append(f'Ramener les {r["nb_h1"]} H1 à un seul (sans changer le design, via classes identiques).')
    if r['nb_h1'] == 0:
        acts.append('Créer un H1 unique porteur du mot-clé métier.')
    if not r['gtm']:
        acts.append('Décider si la page doit être trackée ; si oui, ajouter GTM après le Consent Mode.')
    if r['doublon_de']:
        acts.append('Supprimer le doublon (une seule page doit survivre).')
    if 'non sécurisée' in ' '.join(r['securite']):
        acts.append('Passer les ressources `http://` en `https://` (contenu mixte).')
    if not r['meta_description']:
        acts.append('Rédiger une meta description manuelle (ne pas laisser le générateur le faire).')
    if not acts:
        acts.append('Aucune action détectée par les contrôles automatiques. Action manuelle : valider en '
                    'recette la réception réelle CRM / Sheets / SMS et le déclenchement GTM sur le domaine final.')
    for a in acts:
        L.append(f'- [ ] {a}')
    L.append('')
    L.append('---')
    L.append('')
    L.append('*Fiche générée automatiquement à partir de mesures statiques ; les mentions « code détecté » '
             'ne valent pas preuve de fonctionnement en production.*')
    L.append('')
    return '\n'.join(L)


def main() -> None:
    for r in DATA:
        (OUT / f"{r['site'].replace('/', '__').replace(' ', '_')}.md").write_text(md(r), encoding='utf-8')
    print(f'{len(DATA)} fiches écrites dans {OUT.relative_to(ROOT)}')


if __name__ == '__main__':
    main()
