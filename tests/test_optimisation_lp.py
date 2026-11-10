import sys
import unittest
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from audit_identifiants_lp import inventory


class Page(HTMLParser):
    def __init__(self):
        super().__init__()
        self.lang = ''
        self.h1 = 0
        self.descriptions = []

    def handle_starttag(self, tag, attrs):
        a = dict(attrs)
        if tag == 'html':
            self.lang = a.get('lang', '')
        if tag == 'h1':
            self.h1 += 1
        if tag == 'meta' and a.get('name', '').lower() == 'description':
            self.descriptions.append(a.get('content', ''))


class OptimisationLPTests(unittest.TestCase):
    def test_copies_mobile_identiques_au_modele(self):
        rows, _ = inventory()
        model = (ROOT / 'tools/mobile-ux.js').read_bytes()
        for row in rows:
            if row['statut'] != 'conforme':
                continue
            module = ROOT / row['dossier'] / 'mobile-ux.js'
            if module.exists():
                with self.subTest(page=row['dossier']):
                    self.assertEqual(module.read_bytes(), model)

    def test_langue_et_description_des_pages_ciblees(self):
        rows, _ = inventory()
        for row in rows:
            if row['statut'] != 'conforme':
                continue
            page = Page()
            page.feed((ROOT / row['dossier'] / 'index.html').read_text(encoding='utf8'))
            with self.subTest(page=row['dossier']):
                self.assertEqual(page.lang, 'fr')
                self.assertTrue(any(page.descriptions))

    def test_titres_corriges(self):
        for dossier in ('alfaromeo-tonale', 'energie', 'assurance-multirisques', 'assurance/multirisques'):
            page = Page()
            page.feed((ROOT / dossier / 'index.html').read_text(encoding='utf8'))
            with self.subTest(page=dossier):
                self.assertEqual(page.h1, 1)


if __name__ == '__main__':
    unittest.main()
