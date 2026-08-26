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

| Gericht | Portion | kcal | Eiweiss | KH | Fett | ges. FS | Ballast. | Salz | g Protein/100 kcal |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|
| [Bami Goreng](dishes/bami-goreng.md) | 450 g | 468 | 27,0 g | 56,7 g | 12,2 g | 1,4 g | 10,8 g | 3,3 g | 5,8 |
| [Better Butter Chicken](dishes/better-butter-chicken.md) | 500 g | 470 | 24,0 g | 50,0 g | 18,0 g | 11,0 g | 9,0 g | 3,5 g | 5,1 |

Alle Werte pro Portion aus der offiziellen Nährwerttabelle. **Achtung:** die
Portionsgrösse variiert (450 g / 500 g) — für faire Vergleiche ggf. auf 100 g
normalisieren.

## Status

- **2 / 16** Gerichte des Protein Bundles erfasst
- Offen: Preis pro Gericht, Zuordnung „ist im Protein Bundle enthalten"

## Konventionen

- **Nährwerte:** immer die offizielle Tabelle als Quelle, nicht die Badges oben auf
  der Produktseite — die weichen teils ab (siehe Bami Goreng). Abweichungen unter
  `## Notes` dokumentieren.
- **Portionsgrösse** in `portion_g` festhalten — sie variiert je Gericht (bisher
  450 g und 500 g) und verzerrt Portionsvergleiche.
- **Abschnitts-Überschriften** normalisieren: `## Zutaten` = vollständige Deklaration,
  `## Hauptzutaten` = die hervorgehobenen Komponenten. Auf den Produktseiten sind
  diese beiden Labels nicht konsistent vergeben.
- **Allergene** aus den GROSSGESCHRIEBENEN Zutaten ableiten.
- **`in_protein_bundle`:** `ja` / `nein` / `unbekannt`.
- **Slug** = Handle aus der Produkt-URL (`/products/<slug>`).

## Neues Gericht hinzufügen

Text von der Produktseite hier in den Chat einfügen — Reihenfolge egal, Rohtext genügt.
Daraus entsteht `dishes/<slug>.md` nach dem Muster von `bami-goreng.md`, und die
Vergleichstabelle oben wird nachgeführt.
