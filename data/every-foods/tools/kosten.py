#!/usr/bin/env python3
"""Rechnet die Zutatenkosten der Nachbau-Rezepte auf Basis geschätzter
Lidl-Österreich-Preise.

Aufruf:
  python3 data/every-foods/tools/kosten.py                # Kosten je Gericht
  python3 data/every-foods/tools/kosten.py --liste <slug> ...   # Einkaufsliste
"""
import pathlib
import sys
from collections import defaultdict

import yaml

BASE = pathlib.Path(__file__).resolve().parent.parent
REZ = BASE / "rezepte"
PREISE = yaml.safe_load((REZ / "preise-lidl.yaml").read_text())
DB = yaml.safe_load((REZ / "zutaten-db.yaml").read_text())


def recipes():
    for p in sorted(REZ.glob("*.yaml")):
        if p.name in ("zutaten-db.yaml", "preise-lidl.yaml"):
            continue
        yield yaml.safe_load(p.read_text())


def einkauf_gramm(zutaten):
    """Gramm Einkaufsware je Zutat (Trockenware/Putzverlust eingerechnet)."""
    return {k: g * PREISE[k]["kauf_faktor"] for k, g in zutaten.items() if g > 0}


def kosten(zutaten):
    return sum(g * PREISE[k]["eur_kg"] / 1000 for k, g in einkauf_gramm(zutaten).items())


def dish_name(slug):
    fm = yaml.safe_load((BASE / "dishes" / f"{slug}.md").read_text().split("---", 2)[1])
    return fm["name"], fm["per_portion"]["protein_g"], fm["per_portion"]["kcal"]


def tabelle():
    rows = []
    for r in recipes():
        name, prot, kcal = dish_name(r["dish"])
        c = kosten(r["zutaten"])
        rows.append((c, name, prot, kcal))
    rows.sort()
    print(f"{'Gericht':24} {'Kosten':>8} {'€/100 g Prot.':>14} {'€/1000 kcal':>12}")
    for c, name, prot, kcal in rows:
        print(f"{name:24} {c:7.2f} € {c/prot*100:13.2f} € {c/kcal*1000:11.2f} €")
    total = sum(r[0] for r in rows)
    print(f"\n{len(rows)} Gerichte, je eine Portion: {total:.2f} €  "
          f"(ø {total/len(rows):.2f} € pro Gericht)")


def liste(slugs):
    bedarf = defaultdict(float)
    for r in recipes():
        if slugs and r["dish"] not in slugs:
            continue
        for k, g in einkauf_gramm(r["zutaten"]).items():
            bedarf[k] += g
    gesamt_netto = gesamt_packung = 0.0
    print(f"{'Zutat':26} {'Bedarf':>9} {'Packung':>9} {'Stk':>4} {'zu zahlen':>10}   Lidl-Produkt")
    for k in sorted(bedarf, key=lambda x: -bedarf[x] * PREISE[x]["eur_kg"]):
        g = bedarf[k]
        if g < 0.5 or PREISE[k]["eur_kg"] == 0:
            continue
        pk = PREISE[k]["packung_g"]
        stk = max(1, -(-g // pk))
        netto = g * PREISE[k]["eur_kg"] / 1000
        pack = stk * pk * PREISE[k]["eur_kg"] / 1000
        gesamt_netto += netto
        gesamt_packung += pack
        print(f"{k:26} {g:7.0f} g {pk:7.0f} g {stk:4.0f} {pack:9.2f} €   {DB[k]['lidl'][:44]}")
    print(f"\nVerbrauchte Zutaten:            {gesamt_netto:8.2f} €")
    print(f"Einkauf in ganzen Packungen:    {gesamt_packung:8.2f} €")
    print(f"Rest bleibt im Vorrat:          {gesamt_packung - gesamt_netto:8.2f} €")


if __name__ == "__main__":
    if "--liste" in sys.argv:
        i = sys.argv.index("--liste")
        liste(set(sys.argv[i + 1:]))
    else:
        tabelle()
