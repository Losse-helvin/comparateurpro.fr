#!/usr/bin/env python3
"""
Inventaire exhaustif des landing pages du dépôt comparateurpro.fr
------------------------------------------------------------------
Analyse 100 % statique (aucun réseau, aucune exécution JS) de chaque dossier
de premier niveau contenant un index.html.

Produit :
  ANALYSE/data/inventaire.json   -> données brutes complètes par page
  ANALYSE/data/inventaire.csv    -> tableau plat pour tableur
  ANALYSE/data/orphelins.json    -> médias non référencés / références cassées
  ANALYSE/data/synthese.md       -> tableau de synthèse markdown

Usage :
  python3 ANALYSE/scripts/inventaire_exhaustif.py
"""
from __future__ import annotations

import csv
import hashlib
import json
import re
import sys
from collections import Counter
from datetime import date
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import unquote, urlsplit

ROOT = Path(__file__).resolve().parents[2]
OUT = ROOT / 'ANALYSE' / 'data'
OUT.mkdir(parents=True, exist_ok=True)

MEDIA_EXT = {'.jpg', '.jpeg', '.png', '.webp', '.avif', '.gif', '.svg', '.mp4', '.webm'}
FONT_EXT = {'.woff2', '.woff', '.ttf', '.otf', '.eot'}

# Hôtes internes au groupe (ne sont pas des fuites vers un tiers)
INTERNAL_HOST_RE = re.compile(
    r'([a-z0-9-]+\.)*(comparateurpro\.fr|hellolead\.(pro|preprod\.fr)|hellodevis\.com)'
)


class Parser(HTMLParser):
    """Extrait tout ce qui est utile d'un index.html de landing page."""

    def __init__(self) -> None:
        super().__init__(convert_charrefs=True)
        self.forms: list[dict] = []
        self.form: dict | None = None
        self.scripts: list[dict] = []
        self.script: dict | None = None
        self.iframes: list[str] = []
        self.refs: set[str] = set()          # src/href internes à vérifier en local
        self.ext_hosts: set[str] = set()     # hôtes absolus appelés
        self.h1: list[str] = []
        self.h2: int = 0
        self.h3: int = 0
        self.title: str = ''
        self.meta_description: str = ''
        self.canonical: str = ''
        self.lang: str = ''
        self.gtm: set[str] = set()
        self.ga: set[str] = set()
        self.pixels: set[str] = set()
        self._in = ''
        self._buf: list[str] = []
        self._capture: str | None = None
        self.link_styles: list[str] = []
        self.comments: list[str] = []

    # --- helpers -----------------------------------------------------------
    def _attr(self, a: dict) -> None:
        pass

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        self._in = tag
        if tag in ('h1', 'title'):
            self._buf = []
        if tag == 'form':
            self.form = {
                'id': a.get('id') or '',
                'name': a.get('name') or '',
                'class': a.get('class') or '',
                'marker': a.get('data-ubepro-lead'),
                'action': a.get('action') or '',
                'fields': [],
            }
            self.forms.append(self.form)
        elif tag in ('input', 'select', 'textarea') and self.form is not None:
            self.form['fields'].append({
                'tag': tag,
                'name': a.get('name') or '',
                'type': (a.get('type') or '').lower(),
                'required': 'required' in a or a.get('required') == 'required',
                'hidden': a.get('type') == 'hidden',
            })
        elif tag == 'script':
            self.script = {'src': a.get('src') or '', 'text': '', 'type': a.get('type') or '',
                           'async': 'async' in a, 'defer': 'defer' in a}
            self.scripts.append(self.script)
        elif tag == 'iframe':
            self.iframes.append(a.get('src') or '')
        elif tag == 'h1':
            self._capture = 'h1'
        elif tag == 'h2':
            self.h2 += 1
        elif tag == 'h3':
            self.h3 += 1
        elif tag == 'title':
            self._capture = 'title'
        elif tag == 'html':
            self.lang = a.get('lang') or ''
        elif tag == 'meta':
            if (a.get('name') or '').lower() == 'description':
                self.meta_description = a.get('content') or ''
        elif tag == 'link':
            rel = (a.get('rel') or '').lower()
            href = a.get('href') or ''
            if rel == 'canonical':
                self.canonical = href
            elif rel == 'stylesheet' and href:
                self.link_styles.append(href)
            if href:
                self._register_ref(href)
        if tag in ('script', 'img', 'video', 'source', 'audio', 'link', 'iframe'):
            for key in ('src', 'href', 'data-src', 'poster'):
                if a.get(key):
                    self._register_ref(a[key])

    def handle_endtag(self, tag):
        if tag == 'script' and self.script is not None:
            self.script = None
        elif tag == 'form':
            self.form = None
        elif tag in ('h1', 'title') and self._capture == tag:
            txt = re.sub(r'\s+', ' ', ' '.join(self._buf)).strip()
            if tag == 'title':
                self.title = txt
            else:
                self.h1.append(txt)
            self._capture = None

    def handle_data(self, data):
        if self.script is not None:
            self.script['text'] += data
            return
        txt = data
        if self._capture:
            self._buf.append(txt)
        # détection d'IDs dans les scripts inline sera faite après coup
        for gid in re.findall(r'GTM-[A-Z0-9]{4,}', txt):
            self.gtm.add(gid)
        for gid in re.findall(r'G-[A-Z0-9]{8,}', txt):
            self.ga.add(gid)
        for gid in re.findall(r'AW-\d{6,}', txt):
            self.pixels.add(gid)
        for pid in re.findall(r'\b\d{13,16}\b', txt) if 'facebook' in txt.lower() else []:
            self.pixels.add('FB-' + pid)

    def handle_comment(self, data):
        self.comments.append(data)
        for gid in re.findall(r'GTM-[A-Z0-9]{4,}', data):
            self.gtm.add(gid + ' (commentaire)')

    # --- références --------------------------------------------------------
    def _register_ref(self, raw: str) -> None:
        if not raw or raw.startswith(('#', 'data:', 'javascript:', 'mailto:', 'tel:')):
            return
        parts = urlsplit(raw)
        if parts.scheme in ('http', 'https'):
            if parts.hostname:
                self.ext_hosts.add(parts.hostname)
            return
        if parts.scheme:
            return
        p = unquote(parts.path)
        if p:
            self.refs.add(p.lstrip('/'))


def read(path: Path) -> str:
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except OSError:
        return ''


def config_value(code: str, key: str) -> str:
    m = re.search(r'\b' + re.escape(key) + r"\s*[:=]\s*['\"]([^'\"]*)['\"]", code)
    return m.group(1) if m else ''


def analyse_site(folder: Path) -> dict:
    index = folder / 'index.html'
    html = read(index)
    p = Parser()
    try:
        p.feed(html)
    except Exception as exc:  # HTML très abîmé : on garde ce qui a été lu
        p.ext_hosts.add(f'ERREUR-PARSE:{exc.__class__.__name__}')

    # IDs détectés dans les scripts / textes
    for s in p.scripts:
        blob = s['src'] + ' ' + s['text']
        p.gtm.update(re.findall(r'GTM-[A-Z0-9]{4,}', blob))
        p.ga.update(re.findall(r'G-[A-Z0-9]{8,}', blob))
        p.pixels.update(re.findall(r'AW-\d{6,}', blob))
        if 'googletagmanager' in blob:
            p.pixels.add('GTM-chargeur')

    # --- fichiers du dossier
    files = [f for f in folder.rglob('*') if f.is_file()]
    sizes = {f: f.stat().st_size for f in files}
    total = sum(sizes.values())
    media = [f for f in files if f.suffix.lower() in MEDIA_EXT]
    fonts = [f for f in files if f.suffix.lower() in FONT_EXT]
    videos = [f for f in files if f.suffix.lower() in {'.mp4', '.webm'}]
    md_docs = [f for f in files if f.suffix.lower() == '.md']
    scripts_js = [f for f in files if f.suffix.lower() == '.js']
    css = [f for f in files if f.suffix.lower() == '.css']

    # --- modules de capture
    handler_f = folder / 'lead-handler.js'
    sms_f = folder / 'verification-sms.js'
    handler = read(handler_f)
    sms = read(sms_f)
    order = [unquote(urlsplit(s['src']).path).lstrip('./') for s in p.scripts if s['src']]
    handler_loaded = any(o.endswith('lead-handler.js') for o in order)
    sms_loaded = any(o.endswith('verification-sms.js') for o in order)

    leads = [f for f in p.forms if f['marker'] == '1']
    phone_forms = [f for f in p.forms if any(
        (x['type'] == 'tel') or re.match(r'^(telephone|phone|mobile|tel)', x['name'].lower().replace('-', '').replace('_', '').replace(' ', ''))
        for x in f['fields'] if not x['hidden'] and x['name'])]

    # --- références médias
    refs = set()
    for r in p.refs:
        refs.add(r)
        refs.add(str(Path(folder.name) / r))
    for c in css:
        css_txt = read(c)
        for u in re.findall(r'url\(\s*[\'"]?([^\'")]+)[\'"]?\s*\)', css_txt):
            u = u.strip()
            if u.startswith(('data:', 'http', '//', '#')):
                continue
            refs.add(u.lstrip('/'))
    missing = []
    for r in sorted(p.refs):
        cand = folder / r
        if not cand.exists() and not (folder / Path(r).name).exists():
            # tolérance : fichier présents dans img/ ou fonts/
            if not any((folder / sub / r).exists() for sub in ('img', 'fonts', 'css', 'js', 'videos')):
                if not r.endswith('/') and '.' in Path(r).name:
                    missing.append(r)
    ref_names = {Path(u).name.lower() for u in refs}
    ref_names.update({Path(u).name.lower() for u in p.refs})
    orphans = [str(f.relative_to(folder)) for f in media
               if f.name.lower() not in ref_names
               and not any(f.stem.lower() in rn for rn in ref_names)]

    # --- rapport(s) fournis
    rapport = ''
    for name in ('RAPPORT-MODIFICATIONS.md', 'RAPPORT-INTEGRATION.md', 'rapport-site.md'):
        if (folder / name).is_file():
            rapport += f'{name} '
    rapport_dates = sorted(set(re.findall(r'20\d\d-\d\d-\d\d', '\n'.join(read(f) for f in md_docs))))

    # --- robots / sitemap
    robots = read(folder / 'robots.txt').strip()
    sitemap = read(folder / 'sitemap.xml').strip()

    # --- empreinte pour doublons
    digest = hashlib.md5(html.encode('utf-8', 'replace')).hexdigest()

    # --- hôtes externes
    ext = sorted(h for h in p.ext_hosts if not INTERNAL_HOST_RE.fullmatch(h or ''))

    # --- SEO
    h1 = [h for h in p.h1 if h]
    seo_flags = []
    if not h1:
        seo_flags.append('aucun H1')
    elif len(h1) > 1:
        seo_flags.append(f'{len(h1)} H1')
    if not p.title:
        seo_flags.append('titre absent')
    if not p.meta_description:
        seo_flags.append('meta description absente')
    if p.lang and not p.lang.startswith('fr'):
        seo_flags.append(f'lang="{p.lang}"')
    if not p.canonical:
        seo_flags.append('canonical absente')
    if not robots:
        seo_flags.append('robots.txt absent')
    if not sitemap:
        seo_flags.append('sitemap.xml absent')

    # --- sécurité / conformité rapides
    sec = []
    if re.search(r'(api[_-]?key|secret|token)\s*[:=]\s*[\'"][A-Za-z0-9_\-]{16,}', html + handler + sms, re.I):
        sec.append('clé/secret en clair dans le code client')
    if 'http://' in html.replace('http://www.w3.org', '').replace('http://schema.org', ''):
        sec.append('ressource en http:// non sécurisée')
    if p.iframes:
        sec.append(f'{len(p.iframes)} iframe(s)')

    # --- contrôle documentaire : doc vs réalité du code
    doc_text = ''
    for f in md_docs:
        doc_text += read(f) + '\n'
    doc_conflits = []
    if doc_text:
        if re.search(r'(Aucune confirmation par code SMS|SMS est \*\*exclu|SMS.{0,20}exclue)', doc_text) and sms_loaded:
            doc_conflits.append('La doc affirme que la vérification SMS est exclue, '
                                'mais `verification-sms.js` est bien chargé par `index.html`.')
        if re.search(r'(H1.{0,40}(unique|seul)|un seul H1)', doc_text) and len([h for h in p.h1 if h]) != 1:
            doc_conflits.append(f'La doc affirme un H1 unique ; le HTML en contient {len([h for h in p.h1 if h])}.')
        documented_ids = set(re.findall(r'\bADW_[A-Z0-9_]{4,}\b', doc_text))
        real_id = config_value(handler, 'formId')
        if documented_ids and real_id and real_id not in documented_ids:
            doc_conflits.append(f'La doc cite {sorted(documented_ids)[:2]} ; le code utilise `{real_id}`.')
        if re.search(r'solutions-agv-amr-pro-v2-adw', doc_text) and folder.name != 'solutions-agv-amr-pro-v2-adw':
            doc_conflits.append('La doc se présente sous un nom de dossier qui n\'existe pas '
                                '(`solutions-agv-amr-pro-v2-adw`).')
        if 'TNS_CONFIG' in doc_text and 'TNS_CONFIG' not in handler and handler:
            doc_conflits.append('La doc parle de `TNS_CONFIG` ; le handler de ce dossier n\'en contient pas.')

    return {
        'site': str(folder.relative_to(ROOT)),
        'doc_conflits': doc_conflits,
        'chemin': str(folder.relative_to(ROOT)),
        'html_octets': len(html.encode('utf-8')),
        'fichiers': len(files),
        'octets_total': total,
        'mo_total': round(total / 1024 / 1024, 2),
        'nb_images': len(media),
        'mo_images': round(sum(sizes[f] for f in media) / 1024 / 1024, 2),
        'nb_polices': len(fonts),
        'nb_videos': len(videos),
        'nb_js': len(scripts_js),
        'nb_css': len(css),
        'nb_md': len(md_docs),
        'rapports': rapport.strip(),
        'dates_doc': rapport_dates,
        'title': p.title,
        'lang': p.lang,
        'h1': h1,
        'nb_h1': len(h1),
        'nb_h2': p.h2,
        'meta_description': p.meta_description,
        'canonical': p.canonical,
        'seo_flags': seo_flags,
        'gtm': sorted(g for g in p.gtm if not g.endswith(')')),
        'ga4': sorted(p.ga),
        'ads': sorted(x for x in p.pixels if x.startswith('AW-')),
        'nb_formulaires': len(p.forms),
        'nb_formulaires_marques': len(leads),
        'nb_formulaires_telephone': len(phone_forms),
        'nb_champs_lead': len(leads[0]['fields']) if leads else 0,
        'lead_handler': bool(handler),
        'lead_handler_charge': handler_loaded,
        'lead_handler_octets': len(handler.encode('utf-8')),
        'lead_handler_version': config_value(handler, 'VERSION'),
        'form_id': config_value(handler, 'formId'),
        'form_name': config_value(handler, 'formName'),
        'crm_url': config_value(handler, 'leadApiUrl'),
        'crm_mode': config_value(handler, 'leadApiMode'),
        'source_secours': config_value(handler, 'source'),
        'sheet_url': config_value(handler, 'googleScriptUrl'),
        'public_landing_path': config_value(handler, 'publicLandingPath'),
        'handler_api': sorted(set(re.findall(r'\.(initLead|initForm|sendCrm|sendToGoogleSheets|getTrackingPayload|lirePreferences|preview|googleSheetPreview|inspect)\b', handler))),
        'sms_module': bool(sms),
        'sms_charge': sms_loaded,
        'sms_octets': len(sms.encode('utf-8')),
        'ordre_modules_ok': (order.index('lead-handler.js') < order.index('verification-sms.js'))
                            if ('lead-handler.js' in order and 'verification-sms.js' in order) else False,
        'scripts_charges': order,
        'iframes': p.iframes,
        'hotes_externes': ext,
        'robots': bool(robots),
        'sitemap': bool(sitemap),
        'md5_index': digest,
        'references_cassees': missing[:25],
        'nb_references_cassees': len(missing),
        'nb_orphelins': len(orphans),
        'orphelins': orphans[:25],
        'securite': sec,
        'scripts_inline': sum(1 for s in p.scripts if s['text'].strip()),
    }


def main() -> int:
    folders = sorted(p.parent for p in ROOT.glob('*/index.html'))
    # dossiers imbriqués d'un niveau (assurance/*) : ce sont de vraies LP aussi
    nested_folders = sorted(p.parent for p in ROOT.glob('*/*/index.html'))
    rows = [analyse_site(f) for f in folders + nested_folders]

    # doublons de page
    by_hash: dict[str, list[str]] = {}
    for r in rows:
        by_hash.setdefault(r['md5_index'], []).append(r['site'])
    dups = {h: v for h, v in by_hash.items() if len(v) > 1}
    for r in rows:
        r['doublon_de'] = [s for s in dups.get(r['md5_index'], []) if s != r['site']]

    nested = [str(f.relative_to(ROOT)) for f in nested_folders]

    (OUT / 'inventaire.json').write_text(json.dumps(rows, ensure_ascii=False, indent=1), encoding='utf-8')

    cols = ['site', 'mo_total', 'fichiers', 'nb_images', 'mo_images', 'html_octets', 'nb_h1', 'nb_h2',
            'gtm', 'ga4', 'nb_formulaires', 'nb_formulaires_marques', 'nb_champs_lead',
            'lead_handler', 'lead_handler_charge', 'lead_handler_version', 'form_id', 'crm_mode',
            'source_secours', 'sms_module', 'sms_charge', 'ordre_modules_ok', 'robots', 'sitemap',
            'nb_references_cassees', 'nb_orphelins', 'seo_flags', 'hotes_externes', 'doublon_de', 'dates_doc']
    with (OUT / 'inventaire.csv').open('w', newline='', encoding='utf-8') as fh:
        w = csv.writer(fh, delimiter=';')
        w.writerow(cols)
        for r in rows:
            w.writerow([' | '.join(r[c]) if isinstance(r[c], list) else r[c] for c in cols])

    orph = {r['site']: r['orphelins'] for r in rows if r['orphelins']}
    cass = {r['site']: r['references_cassees'] for r in rows if r['references_cassees']}
    (OUT / 'orphelins.json').write_text(
        json.dumps({'orphelins': orph, 'references_cassees': cass, 'nested': nested},
                   ensure_ascii=False, indent=1), encoding='utf-8')

    # --- synthèse chiffrée
    def nb(pred):
        return sum(1 for r in rows if pred(r))

    stats = {
        'date': date.today().isoformat(),
        'pages': len(rows),
        'octets': sum(r['octets_total'] for r in rows),
        'mo': round(sum(r['octets_total'] for r in rows) / 1024 / 1024, 1),
        'avec_gtm': nb(lambda r: bool(r['gtm'])),
        'avec_handler': nb(lambda r: r['lead_handler']),
        'handler_charge': nb(lambda r: r['lead_handler_charge']),
        'avec_sms': nb(lambda r: r['sms_module']),
        'sms_charge': nb(lambda r: r['sms_charge']),
        'ordre_ok': nb(lambda r: r['ordre_modules_ok']),
        'formulaire_marque': nb(lambda r: r['nb_formulaires_marques'] > 0),
        'avec_robots': nb(lambda r: r['robots']),
        'avec_sitemap': nb(lambda r: r['sitemap']),
        'avec_rapport': nb(lambda r: r['rapports']),
        'refs_cassees': sum(r['nb_references_cassees'] for r in rows),
        'orphelins': sum(r['nb_orphelins'] for r in rows),
        'sans_h1': nb(lambda r: r['nb_h1'] == 0),
        'multi_h1': nb(lambda r: r['nb_h1'] > 1),
        'hors_fr': nb(lambda r: r['lang'] and not r['lang'].startswith('fr')),
        'doublons': sum(len(v) for v in dups.values()),
    }
    (OUT / 'stats.json').write_text(json.dumps(stats, ensure_ascii=False, indent=1), encoding='utf-8')

    print(json.dumps(stats, ensure_ascii=False, indent=1))
    return 0


if __name__ == '__main__':
    sys.exit(main())
