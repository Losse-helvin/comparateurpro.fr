# Audit et corrections SEO, mobile et performance — LP avec form_id détecté

## Périmètre et limites

Périmètre : **88 pages** dont le contrôle statique `tools/audit_identifiants_lp.py` détecte un identifiant conforme au registre/PDF, dans le HTML ou un script local chargé, y compris les sous-dossiers. La détection n'est pas une preuve d'envoi effectif vers le CRM. Les 59 autres pages ne sont pas couvertes par cette intervention : elles nécessitent une qualification séparée, notamment pour les iframes et les formulaires intermédiaires. [Tableau par page, avant/après](data/audit-lp-formid-seo-mobile.csv).

L'audit lit le HTML et les fichiers locaux, et utilise des tests jsdom avec réseau simulé. **Pas de mesure Lighthouse ou Core Web Vitals, de vérification sur de vrais mobiles, d'analyse visuelle de tous les écrans, de test réseau ou de validation CRM en production.** Les estimations de poids des fichiers ne sont pas des temps de chargement. Les campagnes actives et les URL publiques doivent être confirmées.

## Corrections appliquées

### SEO

- Langue HTML : 27 déclarations `en` remplacées par `fr` sur des pages françaises ; 88/88 pages sélectionnées déclarent désormais `fr`.
- Descriptions : descriptions ajoutées aux trois pages qui n'en avaient pas (`LP_reference`, `vehicules-de-societe`, `vehicules-utilitaires`).
- Titres : conversion du titre visible existant en H1 sur `alfaromeo-tonale`, `energie`, `assurance-multirisques` et `assurance/multirisques`, sans modifier le texte et en conservant les classes. Une vérification visuelle demeure nécessaire sur les différents écrans.

| Indicateur statique | Avant | Après |
|---|---:|---:|
| Pages avec `lang="en"` | 27 | 0 |
| Pages sans description | 3 | 0 |
| Pages sans H1 | 76 | 72 |
| Pages avec plusieurs H1 | 2 | 2 |
| Pages sans viewport | 0 | 0 |

Les H1 restants n'ont pas été inventés ni générés automatiquement à partir du nom du dossier : un nombre important de pages sont des étapes de formulaire et leur structure nécessite une revue de contenu. Les deux pages à plusieurs H1 nécessitent aussi une revue sémantique et visuelle avant modification. Les URL canoniques diffèrent souvent des chemins du PDF précédent : arbitrer les URL réellement publiées et l'indexation avant toute réécriture.

### Responsive et fluidité

Dans les **81 pages sélectionnées qui chargent `mobile-ux.js`**, le module pouvait considérer une confirmation masquée par une feuille CSS comme visible, afficher prématurément « Votre demande est bien envoyée » et bloquer les liens. Il essayait aussi de modifier `Location.prototype`, ce qui n'est pas fiable selon les navigateurs. La fonctionnalité de barre et de blocage a été retirée, ainsi que son observateur et son intervalle périodique. Les confirmations et redirections d'origine des formulaires restent en place ; le module ne prolonge donc plus leur délai et ne propose plus les boutons « Continuer / Rester ». Les autres aides mobiles existantes sont conservées. Le modèle dans `tools/mobile-ux.js` est également mis à jour pour les futures copies.

Ce correctif supprime un risque de faux message et du travail JavaScript périodique, mais **ne prouve pas que les 81 pages sont visuellement responsive**. Les 7 autres pages du périmètre ne chargent pas ce module. Un test jsdom vérifie le cas d'un message masqué par CSS, l'absence de barre et de blocage des liens, ainsi que l'initialisation des aides tactiles.

### Chargement et éléments inutiles

Huit logos de partenaires situés dans la grille inférieure de `rc-pro-consultant-conseil-adw` utilisent désormais `loading="lazy"` et `decoding="async"` ; l'image de tête est laissée intacte. Les navigateurs décident du moment de chargement : aucun gain chiffré ne peut être garanti sans mesure.

Sur les pages sélectionnées qui chargent un `script.js` local, la somme des tailles non compressées de ces fichiers est d'environ **122,6 Mio** à travers les copies du dépôt ; les plus gros atteignent 2,8 Mio (`solutions-agv-amr`) et 2,2 Mio (`rc-pro-consultant-conseil-adw`). Ce n'est pas le volume téléchargé par une visite. Le script commun contient des parties Webflow et de formulaire : le supprimer ou le découper sans étude casserait potentiellement des conversions. L'analyse des doublons du dépôt estime environ 835 Mio de redondance, mais ces copies peuvent être nécessaires à des déploiements autonomes. **Aucun média, bundle ou dossier n'a été supprimé sans preuve d'inutilité.** L'ancien module mobile est maintenu hors périmètre sur les autres pages ; ne pas présumer qu'elles ont reçu la correction.

## Priorités restantes

1. **P0 — conversion :** tester sur une préproduction chaque famille de formulaire, ses étapes et redirections, l'API SMS et la réception réelle CRM/Sheets ; confirmer les `form_id` et la configuration des domaines. Le succès Sheets ne garantit pas la réception CRM en mode `no-cors`.
2. **P1 — responsive / accessibilité :** contrôler les 88 pages au clavier et dans des navigateurs réels aux largeurs 320, 375, 768, 1024 et desktop : débordement horizontal, focus, champs, erreurs, zoom iOS, étapes et messages. Vérifier les quatre H1 modifiés visuellement ; contrôler les libellés, contrastes et alternatives d'images. Les attributs et aides automatiques ne suffisent pas à garantir l'accessibilité.
3. **P1 — performance :** mesurer LCP, INP, CLS et poids réseau, sur mobile et connexion lente, par famille de pages et après consentement. Identifier les scripts, images et polices réellement chargés et le cache ; comparer avant/après. Optimiser d'abord les pages actives à fort trafic, en préservant les ressources critiques et le moteur de formulaire.
4. **P2 — SEO :** qualifier les pages indexables ; améliorer manuellement les 72 pages sans H1 et les 2 à H1 multiples si pertinent, revoir titres, descriptions, canonical, robots et sitemap selon les URL de production, sans indexer les étapes ou pages de remerciement par défaut.
5. **P1 — données et conformité :** l'audit précédent signale des valeurs `granted` par défaut dans Consent Mode. Vérifier avec le DPO et la configuration GTM les déclenchements effectifs ; ce travail ne modifie pas le consentement ni le tracking.

## Tests exécutés

- `python3 -m unittest discover -s tests -p 'test_*.py'` : **19/19** tests réussis, dont contrôle des identifiants, tracking, langue, descriptions, H1 ciblés et copies du module.
- `node --test tests/mobile-ux-regression.test.cjs tests/estheticiennes-original.test.cjs` : **9/9** tests ciblés réussis ; le test mobile a été relancé après correction du nettoyage jsdom.
- `node --test --test-name-pattern='(energie|alfaromeo|multirisques)' tests/*.test.cjs` : 32 entrées réussies, dont plusieurs sous-tests ciblés ; certains fichiers ne contenaient aucun test correspondant. Réseau simulé.
- `node --check` : **81/81** modules mobiles modifiés syntaxiquement valides. `git diff --check` : aucune erreur.
- La suite JavaScript complète n'a pas été exécutée dans cette intervention. Un échec historique du test d'un wrapper est documenté dans l'audit précédent ; ne pas en déduire l'état actuel de la suite complète.
