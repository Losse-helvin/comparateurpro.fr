import re
import sys
import unittest
import unicodedata
from html.parser import HTMLParser
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / 'tools'))
from audit_identifiants_lp import inventory


def normal(value):
    value = unicodedata.normalize('NFKD', value or '').encode('ascii', 'ignore').decode().lower()
    return re.sub(r'[^a-z0-9]', '', value)


class FormInputs(HTMLParser):
    def __init__(self):
        super().__init__()
        self.active = False
        self.inputs = []

    def handle_starttag(self, tag, attrs):
        attrs = dict(attrs)
        if tag == 'form':
            self.active = attrs.get('data-ubepro-lead') == '1' or bool(attrs.get('data-form-id'))
        if self.active and tag == 'input':
            self.inputs.append(attrs)

    def handle_endtag(self, tag):
        if tag == 'form':
            self.active = False


class ConfortFormulairesTests(unittest.TestCase):
    def test_claviers_et_autocompletion_des_champs_identifies(self):
        rows, _ = inventory()
        checked = 0
        for row in rows:
            if row['statut'] != 'conforme':
                continue
            page = FormInputs()
            page.feed((ROOT / row['dossier'] / 'index.html').read_text(encoding='utf8'))
            for field in page.inputs:
                if (field.get('type') or 'text').lower() in {'hidden', 'button', 'submit', 'radio', 'checkbox', 'number', 'password'}:
                    continue
                name = re.sub(r'\d+$', '', normal(field.get('name')))
                data = re.sub(r'\d+$', '', normal(field.get('data-name')))
                token = None
                if name in ('telephone', 'phone', 'tel', 'tlphone') or data in ('telephone', 'phone', 'tel'):
                    token = 'tel'
                elif name in ('codepostal', 'cp', 'zipcode', 'postalcode') or data in ('codepostal', 'postalcode'):
                    token = 'postal-code'
                elif name in ('prenom', 'prnom', 'firstname', 'givenname'):
                    token = 'given-name'
                elif name in ('nom', 'lastname', 'familyname'):
                    token = 'family-name'
                elif name in ('mail', 'email', 'courriel') or field.get('type') == 'email':
                    token = 'email'
                elif name in ('societe', 'entreprise', 'nomdelasociete', 'company', 'organisation', 'organization'):
                    token = 'organization'
                if not token:
                    continue
                checked += 1
                with self.subTest(page=row['dossier'], field=field.get('name')):
                    self.assertEqual(field.get('autocomplete'), token)
                    if token == 'tel':
                        self.assertEqual(field.get('inputmode'), 'tel')
                    if token == 'postal-code':
                        self.assertEqual(field.get('inputmode'), 'numeric')
        self.assertGreater(checked, 400)

    def test_explication_sms_sur_les_modules_charges(self):
        rows, _ = inventory()
        count = 0
        for row in rows:
            if row['statut'] != 'conforme':
                continue
            directory = ROOT / row['dossier']
            html = (directory / 'index.html').read_text(encoding='utf8')
            module = directory / 'verification-sms.js'
            if module.is_file() and 'verification-sms.js' in html:
                with self.subTest(page=row['dossier']):
                    self.assertIn('numéro mobile français (06 ou 07)', module.read_text(encoding='utf8'))
                count += 1
        self.assertEqual(count, 87)
        custom = ROOT / 'assurance-estheticiennes-institut-beaute/script.js'
        self.assertIn('numéro mobile français (06 ou 07)', custom.read_text(encoding='utf8'))


if __name__ == '__main__':
    unittest.main()
