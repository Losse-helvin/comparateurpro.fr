#!/usr/bin/env python3
"""Aligne une landing page ajoutee dans le depot sur les regles du site.

Applique a un nouveau dossier (ex. `vehicules-de-societe/`) exactement ce que les
revisions des 10 et 11/11 ont applique aux 146 autres LP :

  1. formId au format [a-z][14 chiffres][a-z], genere de facon deterministe
     (sha256 du chemin) puis enregistre dans les registres :
        ANALYSE/data/registre-formid.json
        tests/registre-formid.json
        ANALYSE/data/url-formid.json
  2. tracking et GTM sans consentement : Consent Mode V2 -> granted,
     GTM-53SH7D7F present, capture URL sans condition (comme les 135 pages)
  3. suppression des valeurs par defaut (champ cache source/categorie vide,
     `source:` vide dans UBE_CONFIG)
  4. module mobile-ux.js copie et reference
  5. aucune regression fonctionnelle : seuls les blocs qui ECRIVENT une valeur par
     defaut sont touches, pas la logique du formulaire

Usage :
    python3 tools/aligner_lp.py --dossier vehicules-de-societe            # simulation
    python3 tools/aligner_lp.py --dossier vehicules-de-societe --apply
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import shutil
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
GTM = "GTM-53SH7D7F"

RX_FORMID = re.compile(r"^[a-z]\d{14}[a-z]$")


def form_id_pour(dossier: str, pris: set[str]) -> str:
    """Identifiant deterministe : sha256 du chemin. Rejouable, donc stable."""
    h = hashlib.sha256(("comparateurpro:" + dossier).encode()).hexdigest()
    n = int(h, 16)
    rang = 0
    while True:
        corps = (n + rang * 7919) % 10**14
        candidat = f"{chr(97 + n % 26)}{corps:014d}{chr(97 + (n // 26) % 26)}"
        if candidat not in pris:
            return candidat
        rang += 1


def lire(p: Path) -> str:
    # newline="" : on preserve les fins de ligne d'origine (CRLF des pages Webflow)
    with p.open(encoding="utf-8", errors="ignore", newline="") as f:
        return f.read()


def ecrire(p: Path, txt: str) -> None:
    p.write_text(txt, encoding="utf-8", newline="")


# --------------------------------------------------------------- HTML
def patch_html(txt: str, form_id: str, mobile: bool) -> tuple[str, list[str]]:
    acts = []

    # Consent Mode : denied -> granted (5 signaux), comme les 135 pages revisees
    def consent(m):
        bloc = m.group(0)
        n = bloc.count("'denied'")
        if not n:
            return bloc
        acts.append(f"Consent Mode : {n} signal(aux) denied -> granted")
        return bloc.replace("'denied'", "'granted'")

    txt = re.sub(r"gtag\('consent',\s*'default',\s*\{.*?\}\);", consent, txt, flags=re.S)

    # GTM present ?
    if GTM not in txt:
        loader = (
            "  <!-- Google Tag Manager -->\n"
            "  <script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':"
            "new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],"
            "j=d.createElement(s),dl=l!='dataLayer'?'&l='+l:'';j.async=true;"
            "j.src='https://www.googletagmanager.com/gtm.js?id='+i+dl;"
            "f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','" + GTM + "');</script>\n"
            "  <!-- End Google Tag Manager -->\n"
        )
        txt = txt.replace("</head>", loader + "</head>", 1)
        noscript = (
            '  <noscript><iframe src="https://www.googletagmanager.com/ns.html?id=' + GTM + '"'
            ' height="0" width="0" style="display:none;visibility:hidden"></iframe></noscript>\n'
        )
        txt = re.sub(r"(<body[^>]*>\s*)", lambda m: m.group(1) + noscript, txt, count=1)
        acts.append("GTM ajoute (loader + noscript)")

    # valeurs par defaut : champs caches source / categorie
    def vide_input(m):
        tag = m.group(0)
        nom = re.search(r'name="([^"]*)"', tag)
        val = re.search(r'value="([^"]*)"', tag)
        if not nom or not val or nom.group(1) not in ("source", "categorie"):
            return tag
        if val.group(1) == "":
            return tag
        acts.append(f"champ cache {nom.group(1)} : {val.group(1)!r} -> vide")
        return tag[: val.start(1)] + tag[val.end(1):]

    txt = re.sub(r"<input\b[^>]*>", vide_input, txt, flags=re.I)

    def vide_attr(m):
        acts.append(f"attribut {m.group(1)} : {m.group(2)!r} -> vide")
        return f'{m.group(1)}=""'

    txt = re.sub(r'(data-(?:source|categorie))="([^"]*)"', vide_attr, txt)

    # module mobile
    if mobile and "mobile-ux.js" not in txt:
        txt = txt.replace("</body>", '  <script src="mobile-ux.js" defer></script>\n</body>', 1)
        acts.append("module mobile-ux.js reference")

    return txt, acts


# --------------------------------------------------------------- handler
def patch_handler(txt: str, form_id: str) -> tuple[str, list[str]]:
    acts = []

    # formId
    nouveau, n = re.subn(r"formId:\s*'[^']*'", f"formId: '{form_id}'", txt, count=1)
    if n and nouveau != txt:
        ancien = re.search(r"formId:\s*'([^']*)'", txt).group(1)
        acts.append(f"formId : {ancien} -> {form_id}")
        txt = nouveau

    # source par defaut
    def source_vide(m):
        if m.group(2) == "":
            return m.group(0)
        acts.append(f"source par defaut {m.group(2)!r} -> vide")
        return "source: ''"

    txt = re.sub(r"(source:\s*)'([^']*)'", lambda m: source_vide(m), txt, count=1)

    # tracking sans consentement
    remplacements = [
        (r"function analyticsGranted\(\)\s*\{\s*return preferences\.analytics === true;\s*\}",
         "function analyticsGranted() { return true; }",
         "analyticsGranted() -> true"),
        (r"function marketingGranted\(\)\s*\{\s*return preferences\.marketing === true;\s*\}",
         "function marketingGranted() { return true; }",
         "marketingGranted() -> true"),
        (r"function trackingGranted\(\)\s*\{\s*return analyticsGranted\(\) \|\| marketingGranted\(\);\s*\}",
         "function trackingGranted() { return true; }",
         "trackingGranted() -> true"),
        (r"function trackingKeyGranted\(key\)\s*\{[^}]*\}",
         "function trackingKeyGranted() { return true; }",
         "trackingKeyGranted() -> true"),
        (r"    if \(!analyticsGranted\(\)\) return '';\n", "", "garde de consentement sur la categorie retiree"),
        (r"if \(input\.value === '' \|\| \(k === 'source' && input\.value === 'SOURCE PAR DEFAUT'\)\)",
         "if (input.value === '')", "valeur litterale 'SOURCE PAR DEFAUT' neutralisee"),
        (r"localStorage\.setItem\('source', \(data\.source \|\| ''\) \+ ' TYP'\);",
         "localStorage.setItem('source', (data.source || ''));", "suffixe ' TYP' retire"),
        (r"categorieCode:\s*'[^']*',\s*(//[^\n]*)?\n", "", "categorieCode supprime"),
        (r"initialCategory \|\| ''", "''", "repli initialCategory retire"),
        (r" \|\| textValue\('categorie'\)", "", "repli textValue('categorie') retire"),
    ]
    for motif, remplacement, libelle in remplacements:
        nouveau, n = re.subn(motif, remplacement, txt)
        if n:
            txt = nouveau
            acts.append(libelle)

    if "initialCategory" in txt:
        txt = re.sub(r"\n\s*var initialCategory = categoryField \?[^\n]*\n", "\n", txt)
        if "initialCategory" not in txt:
            acts.append("variable initialCategory supprimee")

    return txt, acts


# --------------------------------------------------------------- registres
def maj_registres(dossier: str, form_id: str, categorie: int, libelle: str, apply: bool):
    reg_p = ROOT / "ANALYSE" / "data" / "registre-formid.json"
    reg = json.loads(lire(reg_p))
    avant = reg.get(dossier, {}).get("formId")
    reg[dossier] = {"formId": form_id, "categorie": categorie, "libelle": libelle}
    if apply:
        ecrire(reg_p, json.dumps(reg, ensure_ascii=False, indent=1))
        ecrire(ROOT / "tests" / "registre-formid.json", json.dumps(reg, ensure_ascii=False, indent=1))

    inv_p = ROOT / "ANALYSE" / "data" / "url-formid.json"
    inv = json.loads(lire(inv_p))
    url = f"https://{dossier}.lp.comparateurpro.fr/"
    if not any(x["dossier"] == dossier for x in inv):
        inv.append({"url": url, "form_id": form_id, "dossier": dossier, "titre": libelle})
        if apply:
            ecrire(inv_p, json.dumps(inv, ensure_ascii=False, indent=1))
    return avant, len(reg), len(inv)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--dossier", required=True)
    ap.add_argument("--apply", action="store_true")
    ap.add_argument("--form-id", default="")
    ap.add_argument("--categorie", type=int, default=138,
                    help="code metier pour information seulement (plus envoye par defaut)")
    ap.add_argument("--libelle", default="")
    args = ap.parse_args()

    base = ROOT / args.dossier
    if not base.is_dir():
        print(f"dossier absent : {args.dossier}")
        return 1
    index, handler = base / "index.html", base / "lead-handler.js"
    if not index.exists() or not handler.exists():
        print("index.html ou lead-handler.js manquant")
        return 1

    reg = json.loads(lire(ROOT / "ANALYSE" / "data" / "registre-formid.json"))
    pris = {v["formId"] for k, v in reg.items() if k != args.dossier}
    form_id = args.form_id or form_id_pour(args.dossier, pris)
    if not RX_FORMID.match(form_id):
        print(f"formId hors format : {form_id}")
        return 1
    if form_id in pris:
        print(f"formId deja utilise : {form_id}")
        return 1

    libelle = args.libelle or json.loads(lire(ROOT / "ANALYSE" / "data" / "url-formid.json"))
    if isinstance(libelle, list):
        titre = next((x.get("titre") for x in libelle if x["dossier"] == args.dossier), "") or args.dossier
    else:
        titre = args.dossier

    print(f"dossier   : {args.dossier}")
    print(f"formId    : {form_id}  ({'fourni' if args.form_id else 'genere, sha256 du chemin'})")

    h_txt = lire(index)
    h_new, h_acts = patch_html(h_txt, form_id, mobile=(base / "mobile-ux.js").exists())
    j_txt = lire(handler)
    j_new, j_acts = patch_handler(j_txt, form_id)

    print(f"\nindex.html (+{len(h_acts)} action(s))")
    for a in h_acts:
        print("   -", a)
    print(f"lead-handler.js (+{len(j_acts)} action(s))")
    for a in j_acts:
        print("   -", a)

    avant, nreg, ninv = maj_registres(args.dossier, form_id, args.categorie, titre, args.apply)
    print(f"\nregistre : {args.dossier} {'absent -> ajoute' if avant is None else avant + ' -> ' + form_id}"
          f"  ({nreg} entrees)")
    print(f"inventaire : {ninv} entrees")

    if args.apply:
        ecrire(index, h_new)
        ecrire(handler, j_new)
        src_mobile = ROOT / "tools" / "mobile-ux.js"
        if src_mobile.exists() and not (base / "mobile-ux.js").exists():
            shutil.copy2(src_mobile, base / "mobile-ux.js")
            print("mobile-ux.js copie")
        print("\nAPPLIQUE")
    else:
        print("\nsimulation — relancer avec --apply")
    return 0


if __name__ == "__main__":
    sys.exit(main())
