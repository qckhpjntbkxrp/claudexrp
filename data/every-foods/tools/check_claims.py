#!/usr/bin/env python3
"""Prüft die EU-Nährwertclaims (VO (EG) Nr. 1924/2006, Anhang) gegen die
erfassten Nährwerte und meldet Tags, die die Schwellen nicht erfüllen.

Aufruf:  python3 data/every-foods/tools/check_claims.py
"""
import pathlib
import sys

import yaml

DISHES = pathlib.Path(__file__).resolve().parent.parent / "dishes"

# claim -> (tag, prüffunktion). p = per_100g, port = per_portion, kcal = kcal/100 g
CLAIMS = {
    "Proteinquelle":                (lambda p, kcal: p["protein_g"] * 4 / kcal >= 0.12,
                                     "≥ 12 % der Energie aus Protein"),
    "High Protein":                 (lambda p, kcal: p["protein_g"] * 4 / kcal >= 0.20,
                                     "≥ 20 % der Energie aus Protein"),
    "Source of Fiber":              (lambda p, kcal: p["fiber_g"] >= 3 or p["fiber_g"] / kcal * 100 >= 1.5,
                                     "≥ 3 g/100 g oder ≥ 1,5 g/100 kcal"),
    # deutsche Variante desselben Claims, taucht ab Peanut Noodles auf
    "Ballaststoffquelle":           (lambda p, kcal: p["fiber_g"] >= 3 or p["fiber_g"] / kcal * 100 >= 1.5,
                                     "≥ 3 g/100 g oder ≥ 1,5 g/100 kcal"),
    "Hoher Ballaststoffgehalt":     (lambda p, kcal: p["fiber_g"] >= 6 or p["fiber_g"] / kcal * 100 >= 3,
                                     "≥ 6 g/100 g oder ≥ 3 g/100 kcal"),
    "fettarm":                      (lambda p, kcal: p["fat_g"] <= 3,
                                     "≤ 3 g Fett/100 g"),
    "arm an gesättigten Fettsäuren": (lambda p, kcal: p["saturated_fat_g"] <= 1.5
                                      and p["saturated_fat_g"] * 9 / kcal <= 0.10,
                                     "≤ 1,5 g/100 g und ≤ 10 % der Energie"),
    "zuckerarm":                    (lambda p, kcal: p["sugar_g"] <= 5,
                                     "≤ 5 g Zucker/100 g"),
    "Unter 500 kcal":               (lambda p, kcal: True,  # gegen die Portion geprüft, s. u.
                                     "< 500 kcal pro Portion"),
}


def load(path):
    text = path.read_text(encoding="utf-8")
    _, fm, _ = text.split("---", 2)
    return yaml.safe_load(fm)


def main():
    problems = []
    checked = 0
    for path in sorted(DISHES.glob("*.md")):
        d = load(path)
        p100, port = d["per_100g"], d["per_portion"]
        kcal = p100["kcal"]
        for tag in d.get("tags", []):
            if tag not in CLAIMS:
                continue
            checked += 1
            if tag == "Unter 500 kcal":
                ok = port["kcal"] < 500
            else:
                ok = CLAIMS[tag][0](p100, kcal)
            if not ok:
                problems.append((d["name"], tag, CLAIMS[tag][1]))

    print(f"{checked} Claims in {len(list(DISHES.glob('*.md')))} Gerichten geprüft.")
    if not problems:
        print("Alle regulierten Nährwertclaims erfüllen ihre Schwellenwerte.")
        return 0
    print(f"\n{len(problems)} Claim(s) verfehlen die Schwelle:")
    for name, tag, rule in problems:
        print(f'  {name}: „{tag}“ — verlangt {rule}')
    return 1


if __name__ == "__main__":
    sys.exit(main())
