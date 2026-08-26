# every Foods — Gerichte-Datenbank

Manuell übertragene Produktdaten von [everyfoods.ch](https://everyfoods.ch).
Die Session hat keinen Netzzugriff auf die Domain (Egress-Proxy blockt sie), deshalb
werden die Daten per Copy-Paste aus dem Browser eingepflegt.

## Struktur

```
data/every-foods/
├── README.md            ← diese Datei: Index, Konventionen, Vergleichstabelle
└── dishes/
    └── <slug>.md        ← ein File pro Gericht, YAML-Frontmatter + Fliesstext
```

Jedes Gericht hat **YAML-Frontmatter** (maschinenlesbar: Nährwerte, Tags, Allergene)
und darunter **Markdown** (Beschreibung, Zutaten, Zubereitung, Hauptzutaten, Notes).
Damit lässt sich später ohne Umbau eine Tabelle, ein Vergleich oder ein Export bauen.

## Vergleich

| Gericht | kcal | Eiweiss | KH | Fett | Ballast. | Salz | g Protein/100 kcal |
|---|---:|---:|---:|---:|---:|---:|---:|
| [Bami Goreng](dishes/bami-goreng.md) | 468 | 27,0 g | 56,7 g | 12,2 g | 10,8 g | 3,3 g | 5,8 |

Alle Werte pro Portion (450 g Packung), aus der offiziellen Nährwerttabelle.

## Status

- **1 / 16** Gerichte des Protein Bundles erfasst
- Offen: Preis pro Gericht, Zuordnung „ist im Protein Bundle enthalten"

## Konventionen

- **Nährwerte:** immer die offizielle Tabelle als Quelle, nicht die Badges oben auf
  der Produktseite — die weichen teils ab (siehe Bami Goreng). Abweichungen unter
  `## Notes` dokumentieren.
- **Portionsgrösse** in `portion_g` festhalten; falls ≠ 450 g, beim Vergleichen beachten.
- **Allergene** aus den GROSSGESCHRIEBENEN Zutaten ableiten.
- **`in_protein_bundle`:** `ja` / `nein` / `unbekannt`.
- **Slug** = Handle aus der Produkt-URL (`/products/<slug>`).

## Neues Gericht hinzufügen

Text von der Produktseite hier in den Chat einfügen — Reihenfolge egal, Rohtext genügt.
Daraus entsteht `dishes/<slug>.md` nach dem Muster von `bami-goreng.md`, und die
Vergleichstabelle oben wird nachgeführt.
