import sys
import unittest
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from audit_identifiants_lp import inventory
from aligner_lp import patch_html


class IdentifiantsEtTrackingTests(unittest.TestCase):
    def test_pages_registre_et_identifiants_detectes(self):
        rows, registry = inventory()
        self.assertEqual({r['dossier'] for r in rows}, set(registry))
        self.assertEqual(len({item['formId'] for item in registry.values()}), len(registry))
        self.assertFalse([r for r in rows if r['statut'] in ('absent du registre', 'divergent')])

    def test_tracking_statique_vide(self):
        rows, _ = inventory()
        self.assertFalse([(r['dossier'], r['tracking_statique_non_vide']) for r in rows
                          if r['tracking_statique_non_vide']])

    def test_source_particuliere_sans_repli(self):
        script = (ROOT / 'assurance-estheticiennes-institut-beaute/script.js').read_text(encoding='utf-8')
        self.assertIn("source: '',", script)
        self.assertNotIn("source: 'LP CONSULTANTS'", script)

    def test_alignement_attribut_html_valide(self):
        html = '<html><head><!-- GTM-53SH7D7F --></head><body><form data-source="ADW" data-categorie="123"></form></body></html>'
        result, _ = patch_html(html, 'a12345678901234b', False)
        self.assertIn('data-source=""', result)
        self.assertIn('data-categorie=""', result)
        self.assertNotIn('==', result)


if __name__ == '__main__':
    unittest.main()
