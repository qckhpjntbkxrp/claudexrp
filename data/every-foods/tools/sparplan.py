#!/usr/bin/env python3
"""Kostenoptimierte Varianten des Monatsplans (2 Personen), mit Energie- und
Kostenrechnung. Erzeugt data/every-foods/monatsplan/einkauf-spar-2p.txt.

Aufruf: python3 data/every-foods/tools/sparplan.py [voll|150]
"""
import pathlib
import sys

BASE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "tools"))
import kosten_monat as M  # noqa: E402

sys.path.insert(0, str(BASE / "tools"))
from energie import kcal  # noqa: E402

ZIEL_KCAL = 2155 * 60  # wie der Original-Lagerplan liefert

# (Name, Menge, Einheit, Intervallteiler, Gruppe, Begruendung)
BASIS = [
 ('Rote Linsen', 2500, 'g', 1, 'A', 'Hauptprotein, Eisen, Folat'),
 ('Kichererbsen trocken', 2500, 'g', 1, 'A', 'Protein, Folat'),
 ('Weisse Bohnen', 1000, 'g', 1, 'A', 'Rotation'),
 ('Kefen / Erbsen TK', 1000, 'g', 1, 'A', 'gruene Portion'),
 ('Haferflocken', 4000, 'g', 1, 'B', 'billigste Kalorie mit Beta-Glucan'),
 ('Vollkornmehl', 4000, 'g', 1, 'B', 'Brot selbst backen - guenstigste Energie ueberhaupt'),
 ('Vollkornpasta', 3000, 'g', 1, 'B', ''),
 ('Vollkornreis', 2500, 'g', 1, 'B', ''),
 ('Polenta / Maisgriess', 1500, 'g', 1, 'B', 'Rotation, billig'),
 ('Kuerbiskerne', 300, 'g', 1, 'C', 'wichtigste Zinkquelle - bleibt'),
 ('Leinsamen ganz', 300, 'g', 1, 'C', 'ALA - bleibt, frisch schroten'),
 ('Sonnenblumenkerne', 200, 'g', 1, 'C', 'Vitamin E'),
 ('Sesam / Tahini', 300, 'g', 1, 'C', 'Kalzium, Eisen'),
 ('Paranuesse', 100, 'g', 6, 'C', 'Selen - 3 EUR/Monat, unersetzbar'),
 ('Eier', 40, 'Stk', 1, 'D', 'B12 - billigste tierische Quelle'),
 ('Huettenkaese / Skyr', 1000, 'g', 1, 'D', 'Protein, Kalzium, B12'),
 ('Tofu natur', 500, 'g', 1, 'D', 'kalziumgefaellt kaufen'),
 ('Sauerkraut roh', 1000, 'g', 1, 'E', 'billigster Traeger lebender Kulturen'),
 ('Naturjoghurt', 2000, 'g', 1, 'E', 'Kulturen, Kalzium, B12'),
 ('Spinat TK', 1500, 'g', 1, 'F', '2 EUR/kg statt 8 fuer Frischspinat'),
 ('Federkohl / Gruenkohl', 500, 'g', 1, 'F', 'saisonal'),
 ('Petersilie', 200, 'g', 1, 'F', 'Vitamin C zur Eisenmahlzeit'),
 ('Weiss- / Rotkohl', 4000, 'g', 1, 'G', 'billigstes Gemuese, traegt die Menge'),
 ('Broccoli TK', 1500, 'g', 1, 'G', 'Sulforaphan ganzjaehrig'),
 ('Blumenkohl', 1000, 'g', 1, 'G', 'Rotation'),
 ('Kartoffeln festkochend', 8000, 'g', 1, 'H', 'Saettigung, resistente Staerke'),
 ('Ruebli', 3000, 'g', 1, 'H', 'Betacarotin, 1 EUR/kg'),
 ('Zwiebeln', 2000, 'g', 1, 'H', 'praebiotisch'),
 ('Randen', 1000, 'g', 1, 'H', 'Folat, Nitrat'),
 ('Kuerbis', 1500, 'g', 1, 'H', 'saisonal'),
 ('Knoblauch', 4, 'Stk', 1, 'I', 'Allicin'),
 ('Lauch', 1000, 'g', 1, 'I', 'Inulin'),
 ('Ingwer', 200, 'g', 1, 'I', ''),
 ('Aepfel', 3000, 'g', 1, 'J', 'billigstes Obst'),
 ('Bananen', 3000, 'g', 1, 'J', 'Kalium, billige Kalorie'),
 ('Beeren TK gemischt', 500, 'g', 1, 'J', 'Polyphenole - TK statt frisch'),
 ('Zitrusfruechte', 2000, 'g', 1, 'J', 'Vitamin C - traegt die Eisenaufnahme'),
 ('Champignons', 400, 'g', 1, 'K', 'Selen, Beta-Glucane'),
 ('Shiitake getrocknet (UV)', 100, 'g', 3, 'K', 'Vitamin D2, 2 EUR/Monat'),
 ('Olivenoel extra vergine', 1000, 'ml', 1, 'L', 'Hauptoel'),
 ('Rapsoel HOLL', 500, 'ml', 3, 'L', 'zum Erhitzen'),
 ('Leinoel', 250, 'ml', 1, 'L', 'ALA - nicht streichbar'),
 ('Butter', 125, 'g', 1, 'L', 'von 800 g reduziert'),
 ('Jodiertes Salz', 500, 'g', 6, 'M', 'Jod - im Alpenraum nicht optional'),
 ('Schwarzer Pfeffer ganz', 100, 'g', 6, 'M', 'Piperin fuer Curcumin'),
 ('Kurkuma gemahlen', 100, 'g', 3, 'M', ''),
 ('Paprika edelsuess/geraeuchert', 100, 'g', 6, 'M', ''),
 ('Senfkoerner', 80, 'g', 6, 'M', 'Myrosinase zum Kohl'),
 ('Getrocknete Kraeuter (Oregano, Thymian, Rosmarin, Lorbeer)', 200, 'g', 6, 'M', ''),
 ('Chiliflocken', 50, 'g', 6, 'M', ''),
 ('Zimt (Ceylon)', 60, 'g', 6, 'M', ''),
 ('Fenchelsamen', 60, 'g', 6, 'M', 'gegen Blaehungen'),
 ('Tomaten gehackt (Dose)', 6, 'Stk', 1, 'M', 'Lycopin'),
 ('Tomatenmark', 400, 'g', 1, 'M', ''),
 ('Sojasauce / Tamari', 500, 'ml', 3, 'M', ''),
 ('Apfelessig', 750, 'ml', 3, 'M', ''),
 ('Senf', 200, 'g', 3, 'M', 'Myrosinase'),
 ('Hefeflocken', 200, 'g', 3, 'M', 'B-Vitamine, Umami'),
 ('Nori-Blaetter', 50, 'g', 3, 'M', 'Jod-Zweitquelle'),
 ('Sprossensamen (Alfalfa, Broccoli, Linsen)', 300, 'g', 3, 'M', 'Wintergruen fast gratis'),
 ('Kokosmilch', 2, 'Stk', 1, 'M', 'fuer die every-Gerichte'),
 ('Algenoel (EPA/DHA)', 30, 'Kaps', 1, 'O', 'jeden 2. Tag - deckt die EPA/DHA-Luecke'),
 ('Vitamin D3 (vegan, Flechte)', 60, 'Kaps', 1, 'O', 'Okt-Mrz zwingend'),
]
EXTRA = [('_extra_paprika_rot', 1500, 'X', 'Paprika fuer die every-Gerichte, 4 Portionen'),
         ('_extra_staerke', 90, 'X', ''),
         ('_extra_sojabohnenkerne', 470, 'X', 'Edamame TK')]
EXTRA_KCAL = {'paprika_rot': 31, 'staerke': 350, 'sojabohnenkerne': 122}
# Was in der 150-EUR-Variante zusaetzlich wegfaellt
CUT_150 = {'Algenoel (EPA/DHA)': 0, 'Eier': 24, 'Huettenkaese / Skyr': 500,
           'Tofu natur': 0, 'Beeren TK gemischt': 0, 'Champignons': 0,
           'Zitrusfruechte': 1000, 'Olivenoel extra vergine': 750, 'Butter': 0,
           'Naturjoghurt': 1000, 'Kuerbis': 0, 'Randen': 0}


def rechne(variante):
    lo = hi = 0.0
    e = 0.0
    zeilen = []
    for name, menge, einh, t, grp, note in BASIS:
        if variante == '150' and name in CUT_150:
            menge = CUT_150[name]
            if menge == 0:
                continue
        a, b = M.preis(name, menge, einh)
        lo += a / t
        hi += b / t
        e += kcal(name, menge, einh) / t
        zeilen.append((grp, M.AT.get(name, name), menge, einh, a / t, b / t, t, note))
    for name, menge, grp, note in EXTRA:
        a, b = M.preis(name, menge, 'g')
        lo += a
        hi += b
        e += EXTRA_KCAL[name.replace('_extra_', '')] * menge / 100
        zeilen.append((grp, name.replace('_extra_', '').replace('_', ' '), menge, 'g', a, b, 1, note))
    return lo, hi, e, zeilen


SEK = {'A': 'TROCKENWARE - HÜLSENFRÜCHTE', 'B': 'TROCKENWARE - GETREIDE', 'C': 'NÜSSE & SAMEN',
       'D': 'KÜHLREGAL - PROTEIN', 'E': 'KÜHLREGAL - FERMENTIERTES', 'F': 'GEMÜSE - DUNKELGRÜN',
       'G': 'GEMÜSE - KOHL', 'H': 'GEMÜSE - WURZEL & LAGER', 'I': 'GEMÜSE - AROMATEN',
       'J': 'OBST', 'K': 'PILZE', 'L': 'ÖLE & FETTE', 'M': 'WÜRZE & KONSERVEN',
       'O': 'DROGERIE / APOTHEKE', 'X': 'FÜR DIE every-GERICHTE'}


def eur(x):
    return f"{x:.2f}".replace('.', ',')


def fmt(m, e):
    if e == 'g' and m >= 1000:
        return f"{m/1000:.1f}".rstrip('0').rstrip('.').replace('.', ',') + " kg"
    if e == 'ml' and m >= 1000:
        return f"{m/1000:.0f} l"
    return f"{m:.0f} {e}"


def schreibe(variante, pfad):
    lo, hi, e, z = rechne(variante)
    out = ["SPAR-MONATSPLAN  2 PERSONEN  (Österreich)",
           f"Variante: {variante} - {eur(lo)}-{eur(hi)} EUR pro Monat, Mitte {eur((lo+hi)/2)} EUR",
           f"Energie: {e/60:.0f} kcal pro Person und Tag ({e/ZIEL_KCAL*100:.0f} % des Lagerplan-Solls)",
           f"Kalorien je Euro: {e/((lo+hi)/2):.0f} kcal - Ausgangsplan lag bei 256",
           ""]
    for grp, titel in SEK.items():
        zeilen = [x for x in z if x[0] == grp]
        if not zeilen:
            continue
        out += [titel]
        for _, name, menge, einh, a, b, t, note in zeilen:
            iv = f"  [alle {t} Monate]" if t > 1 else ""
            nt = f"  - {note}" if note else ""
            out.append(f"{name} - {fmt(menge, einh)} - {eur(a)}-{eur(b)} EUR{iv}{nt}")
        out += [""]
    pathlib.Path(pfad).write_text("\n".join(out).rstrip() + "\n")


for v in ('voll', '150'):
    lo, hi, e, z = rechne(v)
    print(f"{v:5}  {lo:6.0f}-{hi:6.0f} EUR  Mitte {(lo+hi)/2:6.0f}  "
          f"{e/60:5.0f} kcal/Person/Tag  ({e/ZIEL_KCAL*100:3.0f} %)  "
          f"{e/((lo+hi)/2):4.0f} kcal/EUR")
    schreibe(v, BASE / "monatsplan" / (f"einkauf-spar-2p.txt" if v == 'voll'
                                       else "einkauf-spar-150-2p.txt"))
