#!/usr/bin/env python3
"""
Diagnostic de redondance et de poids du dépôt — mode LECTURE SEULE par défaut.

Ne supprime rien. Produit un rapport de ce qui pourrait l'être.

Usage :
  python3 ANALYSE/scripts/audit_poids.py                # rapport
  python3 ANALYSE/scripts/audit_poids.py --csv          # + export CSV des groupes
  python3 ANALYSE/scripts/audit_poids.py --gros-fichiers 5   # fichiers > 5 Mo

Aucune suppression n'est automatisée volontairement : chaque doublon doit être
arbitré (deux copies identiques peuvent être deux déploiements légitimes).
"""
from __future__ import annotations

import argparse
import csv
import hashlib
from collections import defaultdict
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
IGNORE_DIRS = {'.git', 'ANALYSE', 'node_modules'}


def empreinte(path: Path, taille_max: int = 8 * 1024 * 1024) -> str:
    h = hashlib.md5()
    with path.open('rb') as fh:
        while chunk := fh.read(1024 * 256):
            h.update(chunk)
    return h.hexdigest()


def scanner():
    buckets: dict[str, list[Path]] = defaultdict(list)
    tailles: dict[str, int] = {}
    total = 0
    fichiers = 0
    for f in ROOT.rglob('*'):
        if not f.is_file() or any(p in IGNORE_DIRS for p in f.parts):
            continue
        try:
            t = f.stat().st_size
        except OSError:
            continue
        fichiers += 1
        total += t
        h = empreinte(f)
        buckets[h].append(f)
        tailles[h] = t
    return buckets, tailles, total, fichiers


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--csv', action='store_true')
    ap.add_argument('--gros-fichiers', type=int, default=0, metavar='MO')
    args = ap.parse_args()

    buckets, tailles, total, nb = scanner()
    dups = {h: v for h, v in buckets.items() if len(v) > 1}
    gaspillé = sum(tailles[h] * (len(v) - 1) for h, v in dups.items())

    print(f'Fichiers : {nb}')
    print(f'Poids    : {total / 1024 / 1024:.0f} Mo')
    print(f'Groupes de doublons : {len(dups)} ({sum(len(v) for v in dups.values())} fichiers)')
    print(f'Récupérable : {gaspillé / 1024 / 1024:.0f} Mo ({gaspillé / total * 100:.0f} %)')
    print()
    print('Top 15 des doublons les plus coûteux :')
    for h, v in sorted(dups.items(), key=lambda kv: -tailles[kv[0]] * len(kv[1]))[:15]:
        dossier = v[0].relative_to(ROOT).parts[0] if len(v[0].relative_to(ROOT).parts) > 1 else '—'
        print(f'  {tailles[h] / 1024:8.0f} Ko ×{len(v):3} = {tailles[h] * len(v) / 1024 / 1024:7.1f} Mo  '
              f'{v[0].name}  (ex. dans {dossier})')

    if args.gros_fichiers:
        seuil = args.gros_fichiers * 1024 * 1024
        print(f'\nFichiers > {args.gros_fichiers} Mo :')
        for f in sorted((x for x in ROOT.rglob('*') if x.is_file()
                         and not any(p in IGNORE_DIRS for p in x.parts)),
                        key=lambda x: -x.stat().st_size):
            if f.stat().st_size < seuil:
                break
            print(f'  {f.stat().st_size / 1024 / 1024:6.1f} Mo  {f.relative_to(ROOT)}')

    if args.csv:
        out = ROOT / 'ANALYSE' / 'data' / 'doublons.csv'
        with out.open('w', newline='', encoding='utf-8') as fh:
            w = csv.writer(fh, delimiter=';')
            w.writerow(['taille_ko', 'copies', 'poids_total_mo', 'fichier_modele', 'emplacements'])
            for h, v in sorted(dups.items(), key=lambda kv: -tailles[kv[0]] * len(kv[1])):
                w.writerow([round(tailles[h] / 1024), len(v),
                            round(tailles[h] * len(v) / 1024 / 1024, 2),
                            v[0].name,
                            ' | '.join(str(x.relative_to(ROOT)) for x in v[:6])])
        print(f'\n→ {out.relative_to(ROOT)}')
    return 0


if __name__ == '__main__':
    raise SystemExit(main())
