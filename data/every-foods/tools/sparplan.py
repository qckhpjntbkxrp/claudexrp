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
 ('Weisse Bohnen', 1300, 'g', 1, 'A', 'Rotation; ersetzt die Kidneybohnen in Dal Delight'),
 ('Kefen / Erbsen TK', 1000, 'g', 1, 'A', 'grüne Portion'),
 ('Haferflocken', 4000, 'g', 1, 'B', 'billigste Kalorie mit Beta-Glucan'),
 ('Vollkornmehl', 4000, 'g', 1, 'B', 'Brot selbst backen — günstigste Energie überhaupt'),
 ('Vollkornpasta', 3000, 'g', 1, 'B', ''),
 ('Vollkornreis', 2500, 'g', 1, 'B', ''),
 ('Polenta / Maisgriess', 1500, 'g', 1, 'B', 'Rotation, billig'),
 ('Kuerbiskerne', 300, 'g', 1, 'C', 'wichtigste Zinkquelle'),
 ('Leinsamen ganz', 300, 'g', 1, 'C', 'ALA — frisch schroten'),
 ('Sonnenblumenkerne', 200, 'g', 1, 'C', 'Vitamin E'),
 ('Sesam / Tahini', 300, 'g', 1, 'C', 'Kalzium, Eisen'),
 ('Paranuesse', 100, 'g', 6, 'C', 'Selen — unersetzbar'),
 ('Eier', 40, 'Stk', 1, 'D', 'B12 — billigste tierische Quelle'),
 ('Huettenkaese / Skyr', 1000, 'g', 1, 'D', 'Protein, Kalzium, B12'),
 ('Tofu natur', 500, 'g', 1, 'D', 'kalziumgefällt kaufen'),
 ('Sauerkraut roh', 1000, 'g', 1, 'E', 'billigster Träger lebender Kulturen'),
 ('Naturjoghurt', 2000, 'g', 1, 'E', 'Kulturen, Kalzium, B12'),
 ('Spinat TK', 1500, 'g', 1, 'F', '2 €/kg statt 8 für Frischspinat'),
 ('Federkohl / Gruenkohl', 500, 'g', 1, 'F', 'saisonal'),
 ('Petersilie', 200, 'g', 1, 'F', 'Vitamin C zur Eisenmahlzeit'),
 ('Weiss- / Rotkohl', 4000, 'g', 1, 'G', 'billigstes Gemüse, trägt die Menge'),
 ('Broccoli TK', 1500, 'g', 1, 'G', 'Sulforaphan ganzjährig'),
 ('Blumenkohl', 1000, 'g', 1, 'G', 'Rotation'),
 ('Kartoffeln festkochend', 8000, 'g', 1, 'H', 'Sättigung, resistente Stärke'),
 ('Ruebli', 3000, 'g', 1, 'H', 'Betacarotin, 1 EUR/kg'),
 ('Zwiebeln', 2000, 'g', 1, 'H', 'präbiotisch'),
 ('Randen', 1000, 'g', 1, 'H', 'Folat, Nitrat'),
 ('Kuerbis', 1500, 'g', 1, 'H', 'saisonal'),
 ('Knoblauch', 4, 'Stk', 1, 'I', 'Allicin'),
 ('Lauch', 1000, 'g', 1, 'I', 'Inulin'),
 ('Ingwer', 200, 'g', 1, 'I', ''),
 ('Aepfel', 3000, 'g', 1, 'J', 'billigstes Obst'),
 ('Bananen', 3000, 'g', 1, 'J', 'Kalium, billige Kalorie'),
 ('Beeren TK gemischt', 500, 'g', 1, 'J', 'Polyphenole — TK statt frisch'),
 ('Zitrusfruechte', 2000, 'g', 1, 'J', 'Vitamin C — trägt die Eisenaufnahme'),
 ('Champignons', 400, 'g', 1, 'K', 'Selen, Beta-Glucane'),
 ('Shiitake getrocknet (UV)', 100, 'g', 3, 'K', 'Vitamin D2'),
 ('Olivenoel extra vergine', 1000, 'ml', 1, 'L', 'Hauptoel'),
 ('Rapsoel HOLL', 500, 'ml', 3, 'L', 'zum Erhitzen'),
 ('Leinoel', 250, 'ml', 1, 'L', 'ALA — nicht streichbar'),
 ('Butter', 125, 'g', 1, 'L', 'von 800 g reduziert'),
 ('Jodiertes Salz', 500, 'g', 6, 'M', 'Jod — im Alpenraum nicht optional'),
 ('Schwarzer Pfeffer ganz', 100, 'g', 6, 'M', 'Piperin für Curcumin'),
 ('Kurkuma gemahlen', 100, 'g', 3, 'M', ''),
 ('Paprika edelsuess/geraeuchert', 200, 'g', 3, 'M', 'Hauptgewürz der every-Gerichte'),
 ('Senfkoerner', 80, 'g', 6, 'M', 'Myrosinase zum Kohl'),
 ('Getrocknete Kraeuter (Oregano, Thymian, Rosmarin, Lorbeer)', 200, 'g', 6, 'M', ''),
 ('Chiliflocken', 50, 'g', 6, 'M', ''),
 ('Zimt (Ceylon)', 60, 'g', 6, 'M', ''),
 ('Fenchelsamen', 60, 'g', 6, 'M', 'gegen Blähungen'),
 ('Tomaten gehackt (Dose)', 6, 'Stk', 1, 'M', 'Lycopin'),
 ('Tomatenmark', 400, 'g', 1, 'M', ''),
 ('Sojasauce / Tamari', 500, 'ml', 2, 'M', 'die every-Gerichte brauchen viel davon'),
 ('Apfelessig', 750, 'ml', 3, 'M', ''),
 ('Senf', 200, 'g', 3, 'M', 'Myrosinase'),
 ('Hefeflocken', 200, 'g', 3, 'M', 'B-Vitamine, Umami'),
 ('Nori-Blaetter', 50, 'g', 3, 'M', 'Jod-Zweitquelle'),
 ('Sprossensamen (Alfalfa, Broccoli, Linsen)', 300, 'g', 3, 'M', 'Wintergrün fast gratis'),
 ('Kokosmilch', 3, 'Stk', 1, 'M', 'für die every-Gerichte'),
 ('Algenoel (EPA/DHA)', 30, 'Kaps', 1, 'O', 'jeden 2. Tag — deckt die EPA/DHA-Lücke'),
 ('Vitamin D3 (vegan, Flechte)', 60, 'Kaps', 1, 'O', 'Okt–Mrz zwingend'),
]
EXTRA = [('_extra_paprika_rot', 1500, 'X', 'Paprika für die every-Gerichte'),
         ('_extra_sojagranulat', 360, 'X', 'Proteinträger der every-Gerichte, rehydriert 1:3'),
         ('_extra_staerke', 90, 'X', ''),
         ('_extra_sojabohnenkerne', 500, 'X', 'Edamame TK')]
EXTRA_KCAL = {'paprika_rot': 31, 'staerke': 350, 'sojabohnenkerne': 122, 'sojagranulat': 345}
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


# Reihenfolge wie der Weg durch die Filiale, Tiefkuehl zuletzt
WALK = ['H', 'G', 'F', 'I', 'J', 'X', 'D', 'E', 'A', 'B', 'C', 'M', 'L', 'K', 'N', 'O']
TITEL = {'H': 'Gemüse — Wurzel & Lager', 'G': 'Gemüse — Kohl', 'F': 'Gemüse — Dunkelgrün',
         'I': 'Gemüse — Aromaten', 'J': 'Obst', 'X': 'Für die every-Gerichte',
         'D': 'Kühlregal — Protein', 'E': 'Kühlregal — Fermentiertes',
         'A': 'Trockenware — Hülsenfrüchte', 'B': 'Trockenware — Getreide',
         'C': 'Nüsse & Samen', 'M': 'Würze & Konserven', 'L': 'Öle & Fette',
         'K': 'Pilze', 'N': 'Tiefkühl', 'O': 'Drogerie / Apotheke'}


def markdown(variante, pfad):
    lo, hi, e, z = rechne(variante)
    def istTK(name):
        return name.endswith(' TK') or 'TK' in name.split()
    z = [(('N' if istTK(x[1]) else x[0]),) + x[1:] for x in z]
    mon = [x for x in z if x[6] == 1]
    iv = [x for x in z if x[6] > 1]
    mlo = sum(x[4] for x in mon)
    mhi = sum(x[5] for x in mon)
    out = ["# Einkaufszettel — Monat, 2 Personen",
           "",
           f"| | |",
           f"|---|---|",
           f"| **Monatseinkauf** | {eur(mlo)}–{eur(mhi)} € |",
           f"| Vorratsposten (anteilig) | {eur(lo-mlo)}–{eur(hi-mhi)} € |",
           f"| **Gesamt** | **{eur(lo)}–{eur(hi)} €** |",
           f"| Energie | {e/60:.0f} kcal pro Person und Tag |",
           f"| davon aus den 8 every-Gerichten | 32 Mahlzeiten |",
           "",
           "Preise sind Schätzungen für Lidl Österreich, keine abgerufenen Werte. "
           "Reihenfolge folgt dem Weg durch die Filiale, Tiefkühl zuletzt.",
           "",
           "> **Diese Variante spart am falschen Ende.** Gegenüber der vollen Sparversion "
           "(174–336 €) fehlen hier Algenöl, Tofu, Champignons, TK-Beeren und die Hälfte "
           "der Eier. Algenöl deckt laut Nährstoff-Check eine der zwei echten Lücken — "
           "wenn beim Einkauf Luft bleibt, ist das der erste Posten, der zurückkommt.",
           ""]
    for grp in WALK:
        zeilen = [x for x in mon if x[0] == grp]
        if not zeilen:
            continue
        s_lo = sum(x[4] for x in zeilen)
        s_hi = sum(x[5] for x in zeilen)
        out += [f"## {TITEL[grp]}  ·  {eur(s_lo)}–{eur(s_hi)} €", ""]
        for _, name, menge, einh, a, b, _t, note in zeilen:
            n = f"- [ ] **{name}** — {fmt(menge, einh)} · {eur(a)}–{eur(b)} €"
            out.append(n + (f"  \n      <sub>{note}</sub>" if note else ""))
        out += [""]
    out += ["---", "", "## Nicht jeden Monat", "",
            "Gebinde für Quartal oder Halbjahr — prüfen, ob noch vorhanden.", ""]
    for grp in WALK:
        zeilen = [x for x in iv if x[0] == grp]
        if not zeilen:
            continue
        out += [f"**{TITEL[grp]}**", ""]
        for _, name, menge, einh, a, b, t, note in zeilen:
            out.append(f"- [ ] {name} — {fmt(menge, einh)} · {eur(a*t)}–{eur(b*t)} € "
                       f"· reicht {t} Monate")
        out += [""]
    pathlib.Path(pfad).write_text("\n".join(out).rstrip() + "\n")


for v in ('voll', '150'):
    lo, hi, e, z = rechne(v)
    print(f"{v:5}  {lo:6.0f}-{hi:6.0f} EUR  Mitte {(lo+hi)/2:6.0f}  "
          f"{e/60:5.0f} kcal/Person/Tag  ({e/ZIEL_KCAL*100:3.0f} %)  "
          f"{e/((lo+hi)/2):4.0f} kcal/EUR")
    schreibe(v, BASE / "monatsplan" / ("einkauf-spar-2p.txt" if v == 'voll'
                                       else "einkauf-spar-150-2p.txt"))
markdown('150', BASE / "monatsplan" / "einkaufszettel-150.md")
