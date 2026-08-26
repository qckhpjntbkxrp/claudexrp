#!/usr/bin/env python3
"""Rechnet die Nachbau-Rezepte durch und vergleicht sie mit den Nährwerten,
die every Foods für das Originalgericht deklariert.

Aufruf:  python3 data/every-foods/tools/check_recipe.py [slug ...]
"""
import pathlib
import sys

import yaml

BASE = pathlib.Path(__file__).resolve().parent.parent
DB = yaml.safe_load((BASE / "rezepte" / "zutaten-db.yaml").read_text())
KEYS = ["kcal", "protein_g", "carbs_g", "sugar_g", "fat_g",
        "saturated_fat_g", "fiber_g", "salt_g"]
LABEL = ["kcal", "Eiweiss", "KH", "Zucker", "Fett", "ges.FS", "Ballast.", "Salz"]
# Toleranz je Kennzahl: kcal/Makros 10 %, Mikro-Positionen etwas grosszügiger
TOL = [0.10, 0.10, 0.10, 0.20, 0.10, 0.25, 0.20, 0.15]
# Untergrenze in Gramm: bei winzigen Absolutwerten ist die Prozentabweichung ohne Aussage
MIN_ABS = [15.0, 1.5, 2.0, 2.0, 1.2, 0.8, 1.5, 0.4]


def dish_target(slug):
    fm = yaml.safe_load((BASE / "dishes" / f"{slug}.md").read_text().split("---", 2)[1])
    return fm["name"], fm["per_portion"], fm["portion_g"]


def compute(zutaten):
    total = [0.0] * 8
    gramm = 0.0
    for key, g in zutaten.items():
        if key not in DB:
            raise SystemExit(f"Unbekannte Zutat: {key}")
        gramm += g
        for i, v in enumerate(DB[key]["nutri"]):
            total[i] += v * g / 100
    return total, gramm


def main(slugs):
    rez_dir = BASE / "rezepte"
    files = ([rez_dir / f"{s}.yaml" for s in slugs] if slugs
             else sorted(p for p in rez_dir.glob("*.yaml") if p.name != "zutaten-db.yaml"))
    worst = 0.0
    for f in files:
        r = yaml.safe_load(f.read_text())
        name, target, portion = dish_target(r["dish"])
        total, gramm = compute(r["zutaten"])
        print(f"\n{name}  —  Rezept {gramm:.0f} g / Original {portion} g")
        print(f"  {'':10} {'Rezept':>9} {'Original':>9} {'Abw.':>8}")
        for i, k in enumerate(KEYS):
            soll = float(target[k])
            ist = total[i]
            dev = (ist - soll) / soll if soll else 0.0
            out = abs(dev) > TOL[i] and abs(ist - soll) > MIN_ABS[i]
            flag = "  <-- ausserhalb Toleranz" if out else ""
            if out:
                worst = max(worst, abs(dev) - TOL[i])
            print(f"  {LABEL[i]:10} {ist:9.1f} {soll:9.1f} {dev*100:+7.1f}%{flag}")
        dg = (gramm - portion) / portion
        if abs(dg) > 0.03:
            print(f"  !! Gesamtgewicht weicht um {dg*100:+.1f}% ab")
    return 0 if worst <= 0 else 1


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
