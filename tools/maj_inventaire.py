#!/usr/bin/env python3
"""Regenere l'inventaire URL -> form_id a partir des registres.

Produit, pour chaque dossier du registre :
  ANALYSE/data/url-formid.csv   (;)      — format de secours
  ANALYSE/data/url-formid.json  (utf-8)  — format de secours
  URL-formid-LP.xls             SpreadsheetML, 2 feuilles, lisible par Excel

L'inventaire est celui des LP publiees : les entrees dont le dossier n'a pas
d'index.html sont ecartees.

Usage : python3 tools/maj_inventaire.py
"""
import json
import re
from pathlib import Path
from xml.sax.saxutils import escape

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / "ANALYSE" / "data"
XLS = ROOT / "URL-formid-LP.xls"

RX_ID = re.compile(r"^[a-z]\d{14}[a-z]$")
RX_CANON = re.compile(r'<link\s+rel="canonical"\s+href="([^"]*)"')
RX_TITRE = re.compile(r"<title>([^<]*)</title>")


def collecte():
    """Conserve l'ordre existant de l'inventaire : les nouvelles LP sont ajoutees
    a leur place alphabetique, le reste ne bouge pas (diff minimal, relecture
    possible)."""
    reg = json.loads((DATA / "registre-formid.json").read_text("utf-8"))
    ancien = json.loads((DATA / "url-formid.json").read_text("utf-8"))
    inv = {x["dossier"]: x for x in ancien}
    ordre = [x["dossier"] for x in ancien]

    publiees = [d for d in reg if (ROOT / d / "index.html").exists()]
    nouvelles = sorted((d for d in publiees if d not in ordre),
                       key=lambda d: (inv.get(d, {}).get("url") or reg[d]["formId"]))

    # fusion : on garde l'ordre historique, en inserant les nouvelles entrees
    # selon leur URL pour ne pas tout decaler
    fusion = list(ordre)
    for d in nouvelles:
        url = (inv.get(d, {}).get("url") or "")
        pos = len(fusion)
        for i, autre in enumerate(fusion):
            if (inv.get(autre, {}).get("url") or "zzz") > url:
                pos = i
                break
        fusion.insert(pos, d)
    fusion = [d for d in fusion if d in publiees]

    lignes = []
    for dossier in fusion:
        meta = reg[dossier]
        index = ROOT / dossier / "index.html"
        html = index.read_text(encoding="utf-8", errors="ignore")
        canon = RX_CANON.search(html)
        titre = RX_TITRE.search(html)
        url = inv.get(dossier, {}).get("url") or (canon.group(1) if canon else "")
        lignes.append({
            "url": url,
            "form_id": meta["formId"],
            "dossier": dossier,
            "titre": inv.get(dossier, {}).get("titre") or (titre.group(1) if titre else ""),
            "canonical": canon.group(1) if canon else "",
            "poids": index.stat().st_size,
        })
    return lignes


def cellule(valeur, style=None):
    v = escape(str(valeur))
    s = f' ss:StyleID="{style}"' if style else ""
    return f'<Cell{s}><Data ss:Type="String">{v}</Data></Cell>'


def feuille(nom, entetes, lignes):
    out = [f'<Worksheet ss:Name="{escape(nom)}"><Table>']
    out.append("<Row>" + "".join(cellule(h, "entete") for h in entetes) + "</Row>")
    for l in lignes:
        out.append("<Row>" + "".join(cellule(c) for c in l) + "</Row>")
    out.append("</Table>")
    out.append('<WorksheetOptions xmlns="urn:schemas-microsoft-com:office:excel">'
               '<FreezePanes/><SplitHorizontal>1</SplitHorizontal><TopRowBottomPane>1</TopRowBottomPane>'
               '</WorksheetOptions></Worksheet>')
    return "".join(out)


def ecrit_xls(lignes):
    entetes = ["#", "URL de la landing page", "form_id", "Dossier", "Titre", "Poids index.html"]
    rows = [[i, l["url"] or "(a definir)", l["form_id"], l["dossier"], l["titre"], l["poids"]]
            for i, l in enumerate(lignes, 1)]

    ids = [l["form_id"] for l in lignes]
    doublons = sorted({i for i in ids if ids.count(i) > 1})
    hors_format = [l["dossier"] for l in lignes if not RX_ID.match(l["form_id"])]
    sans_url = [l["dossier"] for l in lignes if not l["url"]]

    controle = [
        ["Lignes", len(lignes)],
        ["form_id uniques", len(set(ids))],
        ["Doublons", ", ".join(doublons) or "aucun"],
        ["Hors format [a-z]14chiffres[a-z]", ", ".join(hors_format) or "aucun"],
        ["URL manquantes", ", ".join(sans_url) or "aucune"],
        ["Controle", "OK" if not doublons and not hors_format else "A CORRIGER"],
    ]

    xml = (
        '<?xml version="1.0" encoding="UTF-8"?>\n'
        '<?mso-application progid="Excel.Sheet"?>\n'
        '<Workbook xmlns="urn:schemas-microsoft-com:office:spreadsheet"'
        ' xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">\n'
        '<Styles>'
        '<Style ss:ID="entete"><Font ss:Bold="1" ss:Color="#FFFFFF"/>'
        '<Interior ss:Color="#1F3A5F" ss:Pattern="Solid"/></Style>'
        '</Styles>\n'
        + feuille("Inventaire", entetes, rows)
        + feuille("Controles", ["Controle", "Valeur"], controle)
        + "\n</Workbook>\n"
    )
    XLS.write_text(xml, encoding="utf-8")
    return doublons, hors_format, sans_url


def main():
    lignes = collecte()

    # CSV / JSON de secours
    import csv
    with (DATA / "url-formid.csv").open("w", encoding="utf-8-sig", newline="") as f:
        w = csv.writer(f, delimiter=";")
        w.writerow(["url", "form_id", "dossier", "titre"])
        for l in lignes:
            w.writerow([l["url"], l["form_id"], l["dossier"], l["titre"]])
    (DATA / "url-formid.json").write_text(
        json.dumps([{k: l[k] for k in ("url", "form_id", "dossier", "titre")} for l in lignes],
                   ensure_ascii=False, indent=1), encoding="utf-8")

    doublons, hors_format, sans_url = ecrit_xls(lignes)
    print(f"lignes            : {len(lignes)}")
    print(f"form_id uniques   : {len({l['form_id'] for l in lignes})}")
    print(f"doublons          : {len(doublons)}")
    print(f"hors format       : {len(hors_format)}")
    print(f"URL manquantes    : {len(sans_url)} {sans_url}")
    print(f"\necrit : URL-formid-LP.xls, ANALYSE/data/url-formid.csv, ANALYSE/data/url-formid.json")


if __name__ == "__main__":
    main()
