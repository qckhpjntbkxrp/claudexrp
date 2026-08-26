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

| Gericht | Portion | kcal | Eiweiss | KH | Fett | ges. FS | Ballast. | Salz | % Energie aus Protein | Label |
|---|---:|---:|---:|---:|---:|---:|---:|---:|---:|---|
| [Bami Goreng](dishes/bami-goreng.md) | 450 g | 468 | 27,0 g | 56,7 g | 12,2 g | 1,4 g | 10,8 g | 3,3 g | 23,1 % | High Protein |
| [Better Butter Chicken](dishes/better-butter-chicken.md) | 500 g | 470 | 24,0 g | 50,0 g | 18,0 g | 11,0 g | 9,0 g | 3,5 g | 20,4 % | High Protein |
| [Brilliant Bolognese](dishes/brilliant-bolognese.md) | 500 g | 520 | 20,0 g | 81,0 g | 10,5 g | 1,5 g | 10,0 g | 2,8 g | 15,4 % | Proteinquelle |
| [Chili sin Carne](dishes/chili-sin-carne.md) | 450 g | 446 | 24,8 g | 49,5 g | 13,1 g | 1,8 g | 15,3 g | 3,9 g | 22,2 % | High Protein |
| [Nasi Goreng](dishes/nasi-goreng.md) | 450 g | 527 | 25,7 g | 57,2 g | 18,9 g | 5,0 g | 11,7 g | 3,4 g | 19,5 % | Proteinquelle |
| [Umami Rice](dishes/umami-rice.md) | 450 g | 424 | **27,9 g** | 59,4 g | 5,9 g | 1,4 g | 10,8 g | 3,2 g | **26,3 %** | High Protein |
| [Edamame Zen](dishes/edamame-zen.md) | 450 g | 423 | 20,3 g | 67,1 g | 5,4 g | 0,9 g | 11,3 g | 2,7 g | 19,1 % | Proteinquelle |
| [Creamy Paprika Pasta](dishes/creamy-paprika-pasta.md) | 450 g | 446 | 21,2 g | 50,4 g | 15,8 g | 11,3 g | 8,6 g | 2,8 g | 19,0 % | Proteinquelle |
| [Smoky Lentil Stew](dishes/smoky-lentil-stew.md) | 450 g | **374** | 23,9 g | 34,7 g | 10,4 g | 0,9 g | **22,1 g** | **2,3 g** | 25,5 % | High Protein |

Alle Werte pro Portion aus der offiziellen Nährwerttabelle. **Achtung:** die
Portionsgrösse variiert (450 g / 500 g) — für faire Vergleiche ggf. auf 100 g
normalisieren.

## Status

- **9** Gerichte erfasst — davon **1 bestätigt** im Protein Bundle
- Offen: Preis pro Gericht, Zuordnung „ist im Protein Bundle enthalten"

### Hinweis zur Bundle-Zuordnung

Das Protein Bundle wirbt mit **ø 23 g Protein pro Gericht**.

**Das Label taugt nicht als Filter.** „Proteinquelle" und „High Protein" sind
EU-Nährwertclaims auf Basis des **Energieanteils**, nicht der absoluten Menge:

| Claim | Bedingung |
|---|---|
| Proteinquelle | ≥ 12 % der Energie aus Protein |
| High Protein | ≥ 20 % der Energie aus Protein |

Die Rechnung (`Protein_g × 4 / kcal`) geht bei allen erfassten Gerichten exakt auf —
siehe Spalte in der Vergleichstabelle. Deshalb trägt **Nasi Goreng mit 25,7 g Protein
nur „Proteinquelle"** (19,5 %, knapp unter der Schwelle), während **Better Butter
Chicken mit 24,0 g „High Protein"** trägt (20,4 %): das fettreichere Gericht hat mehr
Gesamtenergie. Für die Bundle-Frage zählt die **absolute Proteinmenge**.

**Bestätigte Bundle-Gerichte** (Nährwerte tauchen in den Suchergebnissen zur
Bundle-Seite auf):

- Chili sin Carne — 24,8 g / 446 kcal / 49,5 g KH / 13,1 g Fett

**Noch nicht zugeordnetes Bundle-Fragment:** 23,4 g Protein / 491 kcal / 51,3 g KH /
19,4 g Fett. Passt zu keinem bisher erfassten Gericht — beim Einpflegen neuer
Gerichte gegenprüfen.

## Konventionen

- **Nährwerte:** immer die offizielle Tabelle als Quelle, nicht die Badges oben auf
  der Produktseite. Die Protein-Badges weichen bisher bei 2 von 3 Gerichten ab
  (Bami Goreng 25 statt 27 g, Brilliant Bolognese 18 statt 20 g). Abweichungen unter
  `## Notes` dokumentieren.
- **Offensichtlich falsche Seiteninhalte** nicht übernehmen, sondern unter `## Notes`
  festhalten — bei Brilliant Bolognese listet die Seite Hauptzutaten, die in keiner
  Zutatenliste stehen und den Labels widersprechen.
- **Tags gegen die Zutatenliste prüfen — sie sind unzuverlässig.** Bisher 4 von 8
  Gerichten betroffen: „ohne Zwiebeln" bzw. „ohne Paprika" trotz Zwiebelpulver und
  gemahlener Paprika im planted.pulled (Better Butter Chicken, Nasi Goreng), bei
  **Umami Rice** sogar trotz **8 % roter Paprika als deklarierter Hauptzutat**, und
  bei **Creamy Paprika Pasta** „nicht scharf" trotz Chili, Cayenne und einer
  Beschreibung, die mit „feiner Schärfe" wirbt. Nie als Allergen- oder
  Unverträglichkeitsfilter verwenden.
- **`contains_planted_pulled`** und **`protein_source`** mitführen. Als Erklärung für
  die Tag-Fehler reicht planted.pulled aber **nicht**: Smoky Lentil Stew enthält keines,
  ist „ohne Zwiebeln" getaggt und führt **Zwiebelpulver direkt in der Zutatenliste**.
  Die Filter-Logik ist generell fehlerhaft, nicht nur bei Unterzutaten.
- **Nährwert-Badges gegen die Tabelle rechnen** (`100-g-Wert × Portion/100`). Bisher
  zwei echte Fehler statt Rundung: Bami Goreng und Brilliant Bolognese beim Protein,
  **Smoky Lentil Stew bei den Kalorien** (Badge 384, Tabelle 374).
- **Spurenhinweise** in `allergen_traces` erfassen, getrennt von `allergens`.
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
