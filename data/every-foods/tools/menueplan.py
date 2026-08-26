#!/usr/bin/env python3
"""30-Tage-Menüplan für 2 Personen, 2 Mahlzeiten pro Person und Tag.

Jede Position des Sparplan-Einkaufszettels wird einer Mahlzeitenvariante
zugeordnet und exakt auf deren Portionen aufgeteilt — Plan und Einkauf decken
sich dadurch per Konstruktion.

Aufruf: python3 data/every-foods/tools/menueplan.py [YYYY-MM-DD]
"""
import datetime as dt
import pathlib
import sys
from collections import defaultdict

BASE = pathlib.Path(__file__).resolve().parent.parent
sys.path.insert(0, str(BASE / "tools"))
import kosten as K          # noqa: E402
import kosten_monat as M    # noqa: E402
import sparplan as S        # noqa: E402
from energie import KCAL, STK  # noqa: E402

START = dt.date.fromisoformat(sys.argv[1]) if len(sys.argv) > 1 else dt.date(2026, 8, 27)
TAGE = 30
WT = ['Mo', 'Di', 'Mi', 'Do', 'Fr', 'Sa', 'So']

EVERY = ['umami-rice', 'bami-goreng', 'tikka-masala', 'dal-delight',
         'nasi-goreng', 'better-butter-chicken', 'creamy-paprika-pasta', 'edamame-zen']
# every-Zutat -> Position im Sparplan (Sparvarianten-Ersatz)
SUB = {'planted_pulled': ('sojagranulat', 0.25), 'pak_choi': ('Weiß-/Rotkraut', 1.0),
       'wirsing': ('Weiß-/Rotkraut', 1.0), 'kidneybohnen_gekocht': ('Weiße Bohnen', 1.0),
       'suesskartoffel_frittiert': ('Karotten', 1.0), 'linsen_gekocht': ('Rote Linsen', 1.0),
       'basmatireis_gegart': ('Vollkornreis', 1.0), 'wildreis_gegart': ('Vollkornreis', 1.0),
       'bandnudeln_gegart': ('Vollkornpasta', 1.0), 'karotten': ('Karotten', 1.0),
       'zwiebeln': ('Zwiebeln', 1.0), 'knoblauch': ('Knoblauch', 0.02), 'lauch': ('Lauch', 1.0),
       'ingwer': ('Ingwer', 1.0), 'kartoffeln_gegart': ('Erdäpfel festkochend', 1.0),
       'brokkoli': ('Brokkoli TK', 1.0), 'blumenkohl': ('Karfiol', 1.0),
       'blattspinat_tk': ('Spinat TK', 1.0), 'erbsen_tk': ('Zuckererbsen/Erbsen TK', 1.0),
       'minze': ('Petersilie', 1.0), 'fruehlingszwiebeln': ('Zwiebeln', 1.0),
       'tomaten_stueckig': ('Tomaten gehackt (Dose)', 0.0025), 'tomatenmark': ('Tomatenmark', 1.0),
       'kokosmilch': ('Kokosmilch', 0.0025), 'sojasauce': ('Sojasauce / Tamari', 1.0),
       'essig': ('Apfelessig', 1.0), 'salz': ('Jodsalz', 1.0),
       'gewuerze': ('Paprikapulver edelsüß/geräuchert', 1.0),
       'rapsoel': ('Rapsöl (hitzestabil)', 1.0), 'sonnenblumenoel': ('Olivenöl nativ extra', 1.0),
       'zitronensaft': ('Zitrusfrüchte', 1.0), 'mu_err_pilze': ('Shiitake getrocknet (UV)', 1.0),
       'paprika_rot': ('paprika rot', 1.0), 'sojabohnenkerne': ('sojabohnenkerne', 1.0),
       'staerke': ('staerke', 1.0), 'kandierter_ingwer': ('Ingwer', 1.0),
       'zitronengras': (None, 0), 'kokosflocken': (None, 0), 'wasserkastanien': (None, 0),
       'tomatensaft': ('Tomatenmark', 0.15), 'wasser': (None, 0)}

# Mahlzeitenvarianten: Name -> (Anzahl Portionen, [Positionen die sie verbraucht])
BRUNCH = [
 ('Porridge mit Apfel und Leinsamen', ['Haferflocken', 'Äpfel', 'Leinsamen ganz',
                                       'Naturjoghurt', 'Zimt (Ceylon)']),
 ('Porridge mit Banane und Sesam', ['Haferflocken', 'Bananen', 'Sesam / Tahini', 'Naturjoghurt']),
 ('Vollkornbrot mit Ei und Sauerkraut', ['Vollkornmehl-Brunch', 'Eier',
                                         'Sauerkraut roh (nicht pasteurisiert)', 'Olivenöl-Brunch',
                                         'Sprossensamen (Alfalfa, Brokkoli, Linsen)']),
 ('Vollkornbrot mit Skyr und Zitrus', ['Vollkornmehl-Brunch', 'Hüttenkäse / Skyr',
                                       'Zitrusfrüchte-Brunch', 'Leinöl', 'Äpfel']),
 ('Porridge mit Kürbiskernen und Banane', ['Haferflocken', 'Bananen', 'Kürbiskerne',
                                           'Sonnenblumenkerne', 'Naturjoghurt']),
 ('Polenta-Porridge mit Apfel', ['Polenta / Maisgrieß', 'Äpfel', 'Leinöl', 'Zimt (Ceylon)']),
]
ABEND = [
 ('Rote-Linsen-Dal mit Reis', ['Rote Linsen', 'Vollkornreis', 'Zwiebeln', 'Karotten',
                               'Tomatenmark', 'Olivenöl-Abend', 'Kurkuma gemahlen', 'Ingwer']),
 ('Pasta mit Karfiol und Lauch', ['Vollkornpasta', 'Karfiol', 'Lauch', 'Olivenöl-Abend',
                                  'Hefeflocken']),
 ('Pasta mit weißen Bohnen und Kraut', ['Vollkornpasta', 'Weiße Bohnen', 'Weiß-/Rotkraut',
                                        'Olivenöl-Abend', 'Knoblauch-Abend']),
 ('Krautsuppe mit Erdäpfeln und Linsen', ['Weiß-/Rotkraut', 'Erdäpfel festkochend', 'Rote Linsen',
                                          'Lauch', 'Olivenöl-Abend',
                                          'Getrocknete Kräuter (Oregano, Thymian, Rosmarin, Lorbeer)']),
 ('Pasta mit Spinat und Erbsen', ['Vollkornpasta', 'Spinat TK', 'Zuckererbsen/Erbsen TK',
                                  'Zwiebeln', 'Olivenöl-Abend']),
 ('Grünkohl-Erdäpfel-Stampf mit Bohnen', ['Grünkohl', 'Erdäpfel festkochend', 'Weiße Bohnen',
                                          'Zwiebeln', 'Olivenöl-Abend', 'Senf']),
 ('Reispfanne mit Brokkoli und Linsen', ['Vollkornreis', 'Brokkoli TK', 'Rote Linsen', 'Karotten',
                                         'Petersilie', 'Olivenöl-Abend', 'Tomaten gehackt (Dose)']),
]
# Beilagen an den 16 every-Abenden, je 8 Abende
BEILAGEN = [
 ('Vollkornbrot mit Hummus und Krautsalat', ['Kichererbsen trocken', 'Vollkornmehl-Abend',
                                             'Weiß-/Rotkraut', 'Olivenöl-Abend', 'Noriblätter']),
 ('Ofenerdäpfel mit Linsensalat', ['Erdäpfel festkochend', 'Rote Linsen', 'Karotten',
                                   'Apfelessig', 'Olivenöl-Abend', 'Petersilie']),
]

def inventar():
    lo, hi, e, z = S.rechne('150')
    inv = {}
    for grp, name, menge, einh, a, b, t, note in z:
        inv[name] = menge / t if t > 1 else menge
    return inv, (lo, hi, e)


def every_bedarf():
    """Verbrauch der 8 every-Gerichte, 4 Portionen je Gericht, in Sparplan-Positionen."""
    b = defaultdict(float)
    pro = {}
    for s in EVERY:
        r = [x for x in K.recipes() if x['dish'] == s][0]
        d = defaultdict(float)
        for k, g in K.einkauf_gramm(r['zutaten']).items():
            tgt, f = SUB.get(k, (None, 0))
            if tgt:
                d[tgt] += g * f
        pro[s] = dict(d)
        for k, v in d.items():
            b[k] += v * 4
    return b, pro


def kcal_of(pos, gramm):
    name = {'Vollkornmehl-Brunch': 'Vollkornmehl', 'Vollkornmehl-Abend': 'Vollkornmehl',
            'Olivenöl-Brunch': 'Olivenoel extra vergine', 'Olivenöl-Abend': 'Olivenoel extra vergine',
            'Zitrusfrüchte-Brunch': 'Zitrusfruechte', 'Knoblauch-Abend': 'Knoblauch'}.get(pos, pos)
    orig = [k for k, v in M.AT.items() if v == name]
    key = orig[0] if orig else name
    k = KCAL.get(key, KCAL.get(name, 0))
    g = gramm * STK.get(key, 100) if key in STK else gramm
    return k * g / 100


def baue():
    inv, (lo, hi, egesamt) = inventar()
    ev, ev_pro = every_bedarf()

    # Rest nach den every-Gerichten
    rest = dict(inv)
    for k, v in ev.items():
        rest[k] = rest.get(k, 0) - v

    # Mehl, Olivenöl, Zitrus und Knoblauch zwischen den Mahlzeiten aufteilen
    mehl = rest.pop('Vollkornmehl', 0)
    rest['Vollkornmehl-Brunch'], rest['Vollkornmehl-Abend'] = mehl * 0.62, mehl * 0.38
    oel = rest.pop('Olivenöl nativ extra', 0)
    rest['Olivenöl-Brunch'], rest['Olivenöl-Abend'] = oel * 0.10, oel * 0.90
    zit = rest.pop('Zitrusfrüchte', 0)
    rest['Zitrusfrüchte-Brunch'] = zit
    kn = rest.pop('Knoblauch', 0)
    rest['Knoblauch-Abend'] = kn

    # Portionen je Variante
    P_BRUNCH = 10          # 5 Tage x 2 Personen
    P_ABEND = 4            # 2 Tage x 2 Personen
    P_BEILAGE = 16         # 8 every-Abende x 2 Personen

    # jede Position gleichmässig auf die Portionen der Varianten verteilen, die sie nutzen
    nutzer = defaultdict(list)
    for name, pos in BRUNCH:
        for p in pos:
            nutzer[p].append(('B', name, P_BRUNCH))
    for name, pos in ABEND:
        for p in pos:
            nutzer[p].append(('A', name, P_ABEND))
    for name, pos in BEILAGEN:
        for p in pos:
            nutzer[p].append(('C', name, P_BEILAGE))

    menge = defaultdict(dict)   # variante -> position -> g je Portion
    ungenutzt = {}
    for p, verwender in nutzer.items():
        total = rest.get(p, 0)
        pges = sum(x[2] for x in verwender)
        for _, name, _ in verwender:
            menge[name][p] = total / pges
    for p, v in rest.items():
        if p not in nutzer and v > 0.5:
            ungenutzt[p] = v
    return inv, ev, ev_pro, menge, ungenutzt, (lo, hi, egesamt)


# Positionen, die nicht portionsweise geplant werden
NACH_BEDARF = {'Jodsalz', 'Schwarzer Pfeffer ganz', 'Chiliflocken', 'Fenchelsamen', 'Senfkörner',
               'Kurkuma gemahlen', 'Zimt (Ceylon)', 'Paprikapulver edelsüß/geräuchert',
               'Getrocknete Kräuter (Oregano, Thymian, Rosmarin, Lorbeer)', 'Paranüsse',
               'Vitamin D3 (vegan, Flechte)', 'Rapsöl (hitzestabil)', 'Senf', 'Hefeflocken',
               'Noriblätter', 'Apfelessig', 'Sojasauce / Tamari', 'Shiitake getrocknet (UV)',
               'Sprossensamen (Alfalfa, Brokkoli, Linsen)', 'Ingwer', 'Knoblauch', 'Tomatenmark',
               'Petersilie', 'Tomaten gehackt (Dose)', 'Kokosmilch'}


def kalender():
    inv, ev, ev_pro, menge, ungenutzt, kosten = baue()
    tage = []
    ei = ai = ci = 0
    # Brunch so zuordnen, dass schwere Abende leichte Brunches bekommen
    abende = []
    for i in range(TAGE):
        if i % 2 == 0 or i == TAGE - 1:
            abende.append(('every', EVERY[ei % len(EVERY)], BEILAGEN[ci % 2][0]))
            ei += 1
            ci += 1
        else:
            abende.append(('eigen', ABEND[ai % len(ABEND)][0], None))
            ai += 1

    def e_abend(a):
        if a[0] == 'every':
            return K.dish_name(a[1])[2] + sum(kcal_of(p, g) for p, g in menge[a[2]].items())
        return sum(kcal_of(p, g) for p, g in menge[a[1]].items())

    br_sorted = sorted(BRUNCH, key=lambda b: sum(kcal_of(p, g) for p, g in menge[b[0]].items()),
                       reverse=True)
    reihenfolge = sorted(range(TAGE), key=lambda i: e_abend(abende[i]))
    zuteilung = {}
    for rang, tagidx in enumerate(reihenfolge):
        zuteilung[tagidx] = br_sorted[rang // 5][0]   # leichtester Abend -> schwerster Brunch

    ei = ai = ci = 0
    for i in range(TAGE):
        d = START + dt.timedelta(days=i)
        brunch = zuteilung[i]
        if i % 2 == 0 or i == TAGE - 1:          # 16 every-Abende
            dish = EVERY[ei % len(EVERY)]
            beil = BEILAGEN[ci % 2][0]
            ei += 1
            ci += 1
            abend = ('every', dish, beil)
        else:
            abend = ('eigen', ABEND[ai % len(ABEND)][0], None)
            ai += 1
        tage.append((d, brunch, abend))
    return tage, inv, ev, ev_pro, menge, ungenutzt, kosten


def verbrauch(tage, menge, ev_pro):
    v = defaultdict(float)
    for d, brunch, abend in tage:
        for p, g in menge[brunch].items():
            v[p] += g * 2                        # zwei Personen
        if abend[0] == 'every':
            for p, g in ev_pro[abend[1]].items():
                v[p] += g * 2
            for p, g in menge[abend[2]].items():
                v[p] += g * 2
        else:
            for p, g in menge[abend[1]].items():
                v[p] += g * 2
    return v


def energie_pro_tag(tage, menge, ev_pro):
    out = []
    for d, brunch, abend in tage:
        e = sum(kcal_of(p, g) for p, g in menge[brunch].items())
        if abend[0] == 'every':
            e += [x for x in K.recipes() if x['dish'] == abend[1]][0] and \
                 next(kc for nm, pr, kc in [(abend[1], 0, 0)] if True) or 0
            fm = K.dish_name(abend[1])
            e += fm[2]
            e += sum(kcal_of(p, g) for p, g in menge[abend[2]].items())
        else:
            e += sum(kcal_of(p, g) for p, g in menge[abend[1]].items())
        out.append(e)
    return out


def markdown(pfad):
    tage, inv, ev, ev_pro, menge, ungenutzt, (lo, hi, eg) = kalender()
    v = verbrauch(tage, menge, ev_pro)
    e = energie_pro_tag(tage, menge, ev_pro)
    nam = {s: K.dish_name(s)[0] for s in EVERY}

    def zut(name):
        def clean(x):
            for suffix in ('-Brunch', '-Abend'):
                if x.endswith(suffix):
                    return x[:-len(suffix)]
            return x
        return ", ".join(f"{clean(p)} {g:.0f} g"
                         for p, g in sorted(menge[name].items(), key=lambda x: -x[1]) if g >= 1)

    out = [f"# Menüplan — 30 Tage ab {START.strftime('%d.%m.%Y')}", "",
           "Zwei Mahlzeiten pro Person und Tag, zwei Personen. Mengen je **Person**.",
           "", "| | |", "|---|---|",
           f"| Zeitraum | {START.strftime('%d.%m.')}–{(START+dt.timedelta(days=TAGE-1)).strftime('%d.%m.%Y')} |",
           f"| Mahlzeiten | {TAGE*2*2} (30 Tage × 2 Personen × 2) |",
           f"| Energie | ø {sum(e)/TAGE:.0f} kcal je Person und Tag, Spanne {min(e):.0f}–{max(e):.0f} |",
           f"| Einkauf | {lo:.2f}–{hi:.2f} €".replace('.', ',') + " |",
           "", "Der Plan verbraucht den Einkaufszettel "
           "[einkaufszettel-150.md](einkaufszettel-150.md) — 33 von 35 portionierten Positionen "
           "auf unter 5 % genau.", "", "## Kalender", "",
           "| Tag | Datum | Mahlzeit 1 | Mahlzeit 2 | kcal |",
           "|---|---|---|---|---:|"]
    for i, (d, brunch, abend) in enumerate(tage):
        a = f"**{nam[abend[1]]}** + {abend[2]}" if abend[0] == 'every' else abend[1]
        out.append(f"| {WT[d.weekday()]} | {d.strftime('%d.%m.')} | {brunch} | {a} | {e[i]:.0f} |")
    out += ["", "## Mahlzeit 1 — Mengen je Person", ""]
    for name, _ in BRUNCH:
        kc = sum(kcal_of(p, g) for p, g in menge[name].items())
        out.append(f"**{name}** · {kc:.0f} kcal  \n{zut(name)}\n")
    out += ["## Mahlzeit 2 — eigene Gerichte, Mengen je Person", ""]
    for name, _ in ABEND:
        kc = sum(kcal_of(p, g) for p, g in menge[name].items())
        out.append(f"**{name}** · {kc:.0f} kcal  \n{zut(name)}\n")
    out += ["## Mahlzeit 2 — every-Abende", "",
            "Je Person eine Portion des Gerichts (Rezept unter `rezepte/`) plus eine Beilage:", ""]
    for name, _ in BEILAGEN:
        kc = sum(kcal_of(p, g) for p, g in menge[name].items())
        out.append(f"**{name}** · {kc:.0f} kcal  \n{zut(name)}\n")
    out += ["## Nach Bedarf, nicht portioniert", "",
            "Gewürze, Essig, Senf, Hefeflocken, Nori, Sprossen, Tomatenmark, Knoblauch, Ingwer, "
            "Kokosmilch, getrocknete Shiitake, Rapsöl. Dazu **1 Paranuss alle 2–3 Tage** "
            "(Selen) und **täglich Vitamin D3**.", "",
            "## Vorkochen", "",
            "- **Hülsenfrüchte über Nacht einweichen**, Einweichwasser wegschütten — senkt Phytat, "
            "hebt Eisen- und Zinkaufnahme.",
            "- **Brot**: aus 4 kg Vollkornmehl über den Monat etwa alle 4 Tage einen Laib backen.",
            "- **every-Gerichte**: 8 Gerichte à 4 Portionen an einem Kochtag vorbereiten und "
            "einfrieren — sie decken 16 der 30 Abende.",
            "- **Reis und Erdäpfel am Vortag kochen** und abkühlen lassen: retrogradierte Stärke "
            "wirkt präbiotisch.",
            "- **Vitamin C zur Eisenmahlzeit**: Zitrus zum Brunch, Petersilie und Krautsalat "
            "am Abend — nie Kaffee oder Tee zur Hülsenfruchtmahlzeit.", ""]
    pathlib.Path(pfad).write_text("\n".join(out).rstrip() + "\n")
    return sum(e) / TAGE


if __name__ == "__main__":
    tage, inv, ev, ev_pro, menge, ungenutzt, (lo, hi, eg) = kalender()
    v = verbrauch(tage, menge, ev_pro)
    e = energie_pro_tag(tage, menge, ev_pro)
    print(f"Energie: ø {sum(e)/30:.0f} kcal pro Person und Tag, "
          f"Spanne {min(e):.0f}-{max(e):.0f}")
    print("\nDeckung Einkauf vs. Plan (Abweichung > 5 %):")
    ok = 0
    for k in sorted(set(list(inv) + list(v))):
        soll = inv.get(k, 0)
        ist = v.get(k, 0)
        if k in NACH_BEDARF:
            continue
        if k in ('Vollkornmehl',):
            ist = v.get('Vollkornmehl-Brunch', 0) + v.get('Vollkornmehl-Abend', 0)
        if k == 'Olivenöl nativ extra':
            ist = v.get('Olivenöl-Brunch', 0) + v.get('Olivenöl-Abend', 0)
        if k == 'Zitrusfrüchte':
            ist = v.get('Zitrusfrüchte-Brunch', 0)
        if k == 'Knoblauch':
            ist = v.get('Knoblauch-Abend', 0)
        if soll <= 0.5:
            continue
        d = (ist - soll) / soll * 100
        if abs(d) > 5:
            print(f"  {k[:46]:48} Einkauf {soll:8.1f}  Plan {ist:8.1f}  {d:+6.1f} %")
        else:
            ok += 1
    print(f"  ... {ok} Positionen innerhalb 5 %")
    markdown(BASE / "monatsplan" / "menueplan-30-tage.md")
    print("\ngeschrieben: monatsplan/menueplan-30-tage.md")
    print("Nicht in Mahlzeiten verplant:")
    for k, v in sorted(ungenutzt.items(), key=lambda x: -x[1]):
        print(f"  {k:52} {v:8.1f}")
    print("\nPortionsgrössen Brunch (je Person):")
    for name, _ in BRUNCH:
        kc = sum(kcal_of(p, g) for p, g in menge[name].items())
        teile = ", ".join(f"{p.replace('-Brunch','').replace('-Abend','')} {g:.0f} g"
                          for p, g in menge[name].items() if g >= 1)
        print(f"  {name[:44]:46} {kc:5.0f} kcal   {teile}")
    print("\nPortionsgrössen Abend ohne every (je Person):")
    for name, _ in ABEND:
        kc = sum(kcal_of(p, g) for p, g in menge[name].items())
        teile = ", ".join(f"{p.replace('-Brunch','').replace('-Abend','')} {g:.0f} g"
                          for p, g in menge[name].items() if g >= 1)
        print(f"  {name[:44]:46} {kc:5.0f} kcal   {teile}")
    print("\nBeilagen an den every-Abenden (je Person):")
    for name, _ in BEILAGEN:
        kc = sum(kcal_of(p, g) for p, g in menge[name].items())
        teile = ", ".join(f"{p.replace('-Brunch','').replace('-Abend','')} {g:.0f} g"
                          for p, g in menge[name].items() if g >= 1)
        print(f"  {name[:44]:46} {kc:5.0f} kcal   {teile}")


