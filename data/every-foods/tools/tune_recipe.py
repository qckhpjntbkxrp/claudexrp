#!/usr/bin/env python3
"""Passt die als `levers` markierten Mengen eines Rezepts an, bis die Nährwerte
möglichst nah an der Deklaration des Originalgerichts liegen. `wasser` gleicht
das Gesamtgewicht aus.

Aufruf:  python3 data/every-foods/tools/tune_recipe.py <slug> [<slug> ...]
"""
import pathlib
import sys

import yaml

BASE = pathlib.Path(__file__).resolve().parent.parent
DB = yaml.safe_load((BASE / "rezepte" / "zutaten-db.yaml").read_text())
KEYS = ["kcal", "protein_g", "carbs_g", "sugar_g", "fat_g",
        "saturated_fat_g", "fiber_g", "salt_g"]
# Gewichtung: kcal und die drei Makros zählen am meisten
W = [3.0, 3.0, 3.0, 1.5, 3.0, 1.0, 1.5, 2.0]


def totals(z):
    t = [0.0] * 8
    for k, g in z.items():
        for i, v in enumerate(DB[k]["nutri"]):
            t[i] += v * g / 100
    return t


def cost(z, target):
    t = totals(z)
    return sum(w * ((t[i] - float(target[KEYS[i]])) / float(target[KEYS[i]])) ** 2
               for i, w in enumerate(W))


# Grenzen: Lever dürfen deutlich wandern, alle anderen Zutaten nur leicht —
# sonst optimiert der Tuner Zutaten aus dem Rezept heraus.
LEVER_MIN, LEVER_MAX = 0.55, 1.8
FIX_MIN, FIX_MAX = 0.85, 1.15


def tune(z, target, levers, portion, rounds=400):
    z = dict(z)
    start = dict(z)

    def within(cand):
        for k, v in cand.items():
            if k == "wasser" or start.get(k, 0) == 0:
                continue
            lo, hi = (LEVER_MIN, LEVER_MAX) if k in levers else (FIX_MIN, FIX_MAX)
            if not (start[k] * lo - 1e-6 <= v <= start[k] * hi + 1e-6):
                return False
        return True

    for _ in range(rounds):
        improved = False
        for lev in levers:
            for step in (4.0, 1.0, 0.25):
                for sign in (1, -1):
                    cand = dict(z)
                    cand[lev] = round(max(0.0, cand.get(lev, 0.0) + sign * step), 2)
                    # Gesamtgewicht exakt halten: erst Wasser, dann die übrigen
                    # Nicht-Lever-Zutaten proportional nachziehen.
                    rest_keys = [k for k in cand if k not in levers]
                    diff = portion - sum(cand.values())
                    if "wasser" in cand and cand["wasser"] + diff >= 0:
                        cand["wasser"] = round(cand["wasser"] + diff, 2)
                    elif rest_keys:
                        pool = sum(cand[k] for k in rest_keys)
                        if pool <= 0:
                            continue
                        f = (pool + diff) / pool
                        if f <= 0:
                            continue
                        for k in rest_keys:
                            cand[k] = round(cand[k] * f, 2)
                    if abs(sum(cand.values()) - portion) > 0.6:
                        continue
                    if not within(cand):
                        continue
                    if cost(cand, target) < cost(z, target) - 1e-9:
                        z, improved = cand, True
        if not improved:
            break
    return z


def main(slugs):
    for slug in slugs:
        rp = BASE / "rezepte" / f"{slug}.yaml"
        r = yaml.safe_load(rp.read_text())
        fm = yaml.safe_load((BASE / "dishes" / f"{r['dish']}.md").read_text().split("---", 2)[1])
        levers = r.get("levers") or [k for k in r["zutaten"] if k != "wasser"]
        z = tune(r["zutaten"], fm["per_portion"], levers, fm["portion_g"])
        text = rp.read_text()
        for k, v in z.items():
            v_out = int(v) if float(v).is_integer() else v
            old = [ln for ln in text.splitlines() if ln.strip().startswith(f"{k}:")]
            if old:
                head, _, tail = old[0].partition(":")
                comment = tail.split("#", 1)
                new = f"{head}: {v_out}" + (f"      # {comment[1].strip()}" if len(comment) > 1 else "")
                text = text.replace(old[0], new)
        rp.write_text(text)
        print(f"{slug}: getunt")


if __name__ == "__main__":
    main(sys.argv[1:])
