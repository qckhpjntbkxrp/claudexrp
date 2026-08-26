#!/usr/bin/env python3
"""Monatsliste für 2 Personen: Lagerplan + every-Gerichte, mit Preisspanne.

Aufruf:  python3 data/every-foods/tools/kosten_monat.py [Portionen-je-Gericht]
Erzeugt data/every-foods/monatsplan/einkauf-monat-2p.txt und gibt die Summen aus.
"""
import pathlib
import sys
from collections import defaultdict

import openpyxl
import yaml

BASE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "tools"))
import kosten as K  # noqa: E402

XL = sys.argv[2] if len(sys.argv) > 2 else \
    "/root/.claude/uploads/d72a7f3f-eb58-5e54-9fb8-001dad2deb9b/e32d5950-Lagerplan_vegetarisch_2P.xlsx"
P = int(sys.argv[1]) if len(sys.argv) > 1 else 6
MP = BASE / "monatsplan"
AT = yaml.safe_load((MP / "at-begriffe.yaml").read_text())
PREIS = yaml.safe_load((MP / "preise-at.yaml").read_text())

BEST = {'bami-goreng', 'better-butter-chicken', 'creamy-paprika-pasta', 'dal-delight',
        'edamame-zen', 'nasi-goreng', 'tikka-masala', 'umami-rice'}
MAP = {'karotten': 'Ruebli', 'zwiebeln': 'Zwiebeln', 'knoblauch': 'Knoblauch', 'lauch': 'Lauch',
       'ingwer': 'Ingwer', 'kartoffeln_gegart': 'Kartoffeln festkochend', 'brokkoli': 'Broccoli TK',
       'blumenkohl': 'Blumenkohl', 'blattspinat_tk': 'Spinat TK', 'erbsen_tk': 'Kefen / Erbsen TK',
       'suesskartoffel_frittiert': 'Suesskartoffeln', 'wirsing': 'Wirz', 'minze': 'Petersilie',
       'fruehlingszwiebeln': 'Schalotten', 'linsen_gekocht': 'Berglinsen',
       'kidneybohnen_gekocht': 'Kidneybohnen', 'basmatireis_gegart': 'Vollkornreis',
       'wildreis_gegart': 'Vollkornreis', 'bandnudeln_gegart': 'Vollkornpasta',
       'tomaten_stueckig': 'Tomaten gehackt (Dose)', 'tomatenmark': 'Tomatenmark',
       'kokosmilch': 'Kokosmilch', 'sojasauce': 'Sojasauce / Tamari', 'essig': 'Apfelessig',
       'salz': 'Jodiertes Salz', 'gewuerze': 'Paprika edelsuess/geraeuchert',
       'rapsoel': 'Rapsoel HOLL', 'sonnenblumenoel': 'Olivenoel extra vergine',
       'zitronensaft': 'Zitrusfruechte', 'mu_err_pilze': 'Shiitake getrocknet (UV)'}
EXTRA = {'paprika_rot': 'Paprika rot', 'pak_choi': 'Pak Choi (oder Wirsing aus dem Plan)',
         'planted_pulled': 'Veganes Pulled/Sojaschnetzel (oder Rauchtofu aus dem Plan)',
         'sojabohnenkerne': 'Edamame TK', 'wasserkastanien': 'Wasserkastanien (Dose)',
         'staerke': 'Speisestärke', 'kandierter_ingwer': 'Ingwer kandiert',
         'zitronengras': 'Zitronengras (Paste/TK)', 'kokosflocken': 'Kokosraspeln',
         'tomatensaft': 'Tomatensaft'}
SEK = {'A': 'TROCKENWARE - HÜLSENFRÜCHTE', 'B': 'TROCKENWARE - GETREIDE', 'C': 'NÜSSE & SAMEN',
       'D': 'KÜHLREGAL - PROTEIN', 'E': 'KÜHLREGAL - FERMENTIERTES', 'F': 'GEMÜSE - DUNKELGRÜN',
       'G': 'GEMÜSE - KOHL', 'H': 'GEMÜSE - WURZEL & LAGER', 'I': 'GEMÜSE - AROMATEN',
       'J': 'OBST', 'K': 'PILZE', 'L': 'ÖLE & FETTE', 'M': 'WÜRZE & KONSERVEN',
       'N': 'TIEFKÜHL', 'O': 'DROGERIE / APOTHEKE'}
SEK_EXTRA = {'paprika_rot': 'GEMÜSE - KOHL', 'pak_choi': 'GEMÜSE - DUNKELGRÜN',
             'planted_pulled': 'KÜHLREGAL - PROTEIN', 'sojabohnenkerne': 'TIEFKÜHL',
             'wasserkastanien': 'WÜRZE & KONSERVEN', 'staerke': 'WÜRZE & KONSERVEN',
             'kandierter_ingwer': 'WÜRZE & KONSERVEN', 'zitronengras': 'WÜRZE & KONSERVEN',
             'kokosflocken': 'NÜSSE & SAMEN', 'tomatensaft': 'WÜRZE & KONSERVEN'}
TEILER = {'Quartal': 3, 'Halbjahr': 6}


def fmt(m, e):
    if e == 'g' and m >= 1000:
        return f"{m/1000:.1f}".rstrip('0').rstrip('.').replace('.', ',') + " kg"
    if e == 'ml' and m >= 1000:
        return f"{m/1000:.0f} l"
    return f"{m:.0f} {e}"


def eur(x):
    return f"{x:.2f}".replace('.', ',')


def preis(name, menge, einheit):
    lo, hi = PREIS[name]
    f = menge / 1000 if einheit in ('g', 'ml') else menge
    return lo * f, hi * f


def main():
    wb = openpyxl.load_workbook(XL, data_only=True)
    lager = [dict(gruppe=r[0], name=r[1], menge=float(r[2]), einheit=r[3], intervall=r[4])
             for r in wb['Lagerbestand'].iter_rows(min_row=5, values_only=True)
             if r[0] and r[1] and r[2] is not None]

    bedarf = defaultdict(float)
    for r in K.recipes():
        if r['dish'] not in BEST:
            continue
        for k, g in K.einkauf_gramm(r['zutaten']).items():
            bedarf[k] += g * P
    nutzung = defaultdict(float)
    for k, g in bedarf.items():
        if k in MAP:
            nutzung[MAP[k]] += g

    monat, selten = defaultdict(list), defaultdict(list)
    s_lo = s_hi = q_lo = q_hi = 0.0
    for L in lager:
        sek = SEK[L['gruppe'].split(' - ')[0].strip()]
        menge, mark = L['menge'], ""
        if L['name'] in nutzung:
            anteil = nutzung[L['name']] / menge * 100 if L['einheit'] == 'g' else 0
            if anteil > 100:
                menge = nutzung[L['name']]
                mark = f"  [Plan {fmt(L['menge'], L['einheit'])} reicht nicht, every braucht {anteil:.0f} %]"
            elif anteil:
                mark = f"  [every: {anteil:.0f} %]"
            else:
                mark = "  [every nutzt davon]"
        lo, hi = preis(L['name'], menge, L['einheit'])
        name = AT.get(L['name'], L['name'])
        t = TEILER.get(L['intervall'])
        if t:
            q_lo += lo / t
            q_hi += hi / t
            selten[sek].append(f"{name} - {fmt(menge, L['einheit'])} - {eur(lo)}-{eur(hi)} EUR"
                               f"  [{L['intervall']}, pro Monat {eur(lo/t)}-{eur(hi/t)}]{mark}")
        else:
            s_lo += lo
            s_hi += hi
            monat[sek].append(f"{name} - {fmt(menge, L['einheit'])} - {eur(lo)}-{eur(hi)} EUR{mark}")

    extra = defaultdict(list)
    for k, g in sorted(bedarf.items(), key=lambda x: -x[1]):
        if k in MAP or g < 0.5 or k not in EXTRA:
            continue
        lo, hi = preis('_extra_' + k, g, 'g')
        s_lo += lo
        s_hi += hi
        extra[SEK_EXTRA[k]].append(f"{EXTRA[k]} - {fmt(g, 'g')} - {eur(lo)}-{eur(hi)} EUR")

    out = ["MONATS-EINKAUF  2 PERSONEN  (Österreich)",
           f"Lagerplan vegetarisch + 8 every-Gerichte à {P} Portionen = {8*P} Mahlzeiten",
           f"Erwartete Kosten: {eur(s_lo)}-{eur(s_hi)} EUR pro Monat",
           f"dazu anteilig Quartals- und Halbjahresposten: {eur(q_lo)}-{eur(q_hi)} EUR",
           f"Summe im Schnitt: {eur(s_lo+q_lo)}-{eur(s_hi+q_hi)} EUR",
           "", "== JEDEN MONAT ==", ""]
    for sek in SEK.values():
        z = monat.get(sek, []) + extra.get(sek, [])
        if z:
            out += [sek] + z + [""]
    out += ["", "== NICHT JEDEN MONAT (Gebinde für Quartal/Halbjahr) ==", ""]
    for sek in SEK.values():
        if selten.get(sek):
            out += [sek] + selten[sek] + [""]
    (MP / "einkauf-monat-2p.txt").write_text("\n".join(out).rstrip() + "\n")
    print(f"Monatlich       {eur(s_lo)}-{eur(s_hi)} EUR")
    print(f"Vorrat anteilig {eur(q_lo)}-{eur(q_hi)} EUR")
    print(f"Gesamt          {eur(s_lo+q_lo)}-{eur(s_hi+q_hi)} EUR")
    print(f"pro Person/Tag  {eur((s_lo+q_lo)/60)}-{eur((s_hi+q_hi)/60)} EUR")


if __name__ == "__main__":
    main()
