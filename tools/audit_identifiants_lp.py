#!/usr/bin/env python3
"""Inventaire reproductible des index et identifiants locaux, sans modification des LP.

Le registre doit être comparé au PDF séparément. Un identifiant détecté n'est pas
une preuve de réception CRM, et l'absence d'un handler n'implique pas un défaut :
certaines pages sont des étapes, des iframes ou des remerciements.
"""
import csv
import json
import re
import sys
from html.parser import HTMLParser
from pathlib import Path
from urllib.parse import urlsplit

ROOT = Path(__file__).resolve().parent.parent
REGISTRE = ROOT / 'ANALYSE/data/registre-formid.json'


class Page(HTMLParser):
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.forms = []
        self.scripts = []
        self.iframes = []
        self.tracking_values = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form':
            self.forms.append(attrs)
        if tag == 'script' and attrs.get('src'):
            self.scripts.append(attrs['src'])
        if tag == 'iframe' and attrs.get('src') and 'googletagmanager.com/ns.html' not in attrs['src']:
            self.iframes.append(attrs['src'])
        if tag == 'input' and attrs.get('type', '').lower() == 'hidden':
            name = (attrs.get('name') or '').lower()
            if (name in {'source', 'categorie', 'category', 'gclid', 'fbclid', 'msclkid', 'gbraid', 'wbraid', 'ttclid'}
                    or name.startswith(('utm_', 'ltm_'))) and attrs.get('value'):
                self.tracking_values.append(name)
        for key in ('data-source', 'data-categorie'):
            if attrs.get(key):
                self.tracking_values.append(key)


def inventory(root=ROOT):
    reg = json.loads((root / 'ANALYSE/data/registre-formid.json').read_text(encoding='utf-8'))
    pages = sorted(root.glob('*/index.html')) + sorted(root.glob('*/*/index.html'))
    rows = []
    for path in sorted(pages):
        directory = path.parent.relative_to(root).as_posix()
        page = Page()
        page.feed(path.read_text(encoding='utf-8', errors='replace'))
        expected = reg.get(directory, {}).get('formId', '')
        ids = []
        for form in page.forms:
            if form.get('data-form-id'):
                ids.append(('html', form['data-form-id']))
        for src in page.scripts:
            local = urlsplit(src)
            if local.scheme or local.netloc:
                continue
            script = path.parent / local.path
            if script.is_file() and script.name in ('lead-handler.js', 'script.js'):
                content = script.read_text(encoding='utf-8', errors='replace')
                ids.extend((script.name, m) for m in re.findall(r"\bformId\s*:\s*['\"]([a-z]\d{14}[a-z])['\"]", content))
        unique = sorted({value for _, value in ids})
        status = 'absent du registre' if not expected else ('non détecté' if not unique else ('conforme' if unique == [expected] else 'divergent'))
        rows.append({'dossier': directory, 'form_id_pdf_registre': expected, 'form_id_detectes': ', '.join(unique),
                     'emplacements': ', '.join(sorted({place for place, _ in ids})), 'statut': status,
                     'formulaires_html': len(page.forms), 'formulaires_marques': sum(f.get('data-ubepro-lead') == '1' for f in page.forms),
                     'iframes_hors_gtm': len(page.iframes), 'tracking_statique_non_vide': ', '.join(page.tracking_values)})
    return rows, reg


def main():
    rows, _ = inventory()
    writer = csv.DictWriter(sys.stdout, fieldnames=rows[0].keys(), delimiter=';', lineterminator='\n')
    writer.writeheader()
    writer.writerows(rows)


if __name__ == '__main__':
    main()
