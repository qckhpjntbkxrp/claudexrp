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
| [Dal Delight](dishes/dal-delight.md) | 450 g | 491 | 23,9 g | 53,6 g | 16,7 g | **11,7 g** | 16,2 g | 3,4 g | 19,4 % | Proteinquelle |
| [Tikka Masala](dishes/tikka-masala.md) | 450 g | 491 | 23,4 g | 51,3 g | 19,4 g | 10,8 g | 8,6 g | 3,1 g | 19,1 % | Proteinquelle |
| [Teriyaki Wok](dishes/teriyaki-wok.md) | 500 g | 520 | 27,0 g | 64,0 g | 16,5 g | 2,0 g | 10,0 g | 3,4 g | 20,8 % | High Protein |
| [Green Forest Bowl](dishes/green-forest-bowl.md) | 450 g | **599** | 20,3 g | 44,1 g | **36,0 g** | 5,9 g | 9,5 g | 2,8 g | 13,5 % | Proteinquelle |

Alle Werte pro Portion aus der offiziellen Nährwerttabelle. **Achtung:** die
Portionsgrösse variiert (450 g / 500 g) — für faire Vergleiche ggf. auf 100 g
normalisieren.

## Status

- **13** Gerichte erfasst — davon **2 bestätigt** im Protein Bundle
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
- Tikka Masala — 23,4 g / 491 kcal / 51,3 g KH / 19,4 g Fett

Beide Fragmente aus der Bundle-Seite sind damit zugeordnet; weitere liegen nicht vor.

**Tikka Masala widerlegt die Label-Heuristik endgültig:** es trägt „Proteinquelle"
(19,1 % Energie aus Protein) und ist trotzdem nachweislich im Bundle. Für die
Zugehörigkeit zählt allein die **absolute Proteinmenge** — 23,4 g entsprechen exakt
dem beworbenen Schnitt von ø 23 g.

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
- **Nährwert-Badges gegen die Tabelle rechnen** (`100-g-Wert × Portion/100`).
  **6 von 13 Gerichten** haben echte Badge-Fehler jenseits der Rundung:

  | Gericht | betroffen | Badge | Tabelle |
  |---|---|---:|---:|
  | Bami Goreng | Protein | 25 g | 27,0 g |
  | Brilliant Bolognese | Protein | 18 g | 20,0 g |
  | Smoky Lentil Stew | Energie | 384 kcal | 374 kcal |
  | Dal Delight | Fett | 18 g | 16,65 g |
  | **Teriyaki Wok** | **alle vier** | 16,5 / 55 / 31 / 590 | 27,0 / 64,0 / 16,5 / 520 |
  | **Green Forest Bowl** | **alle vier** (400-g-Basis) | 18 / 42,2 / 32 / 532 | 20,25 / 44,1 / 36,0 / 599 |

  Bei Green Forest Bowl entstehen drei der vier Badge-Werte exakt aus
  `100-g-Wert × 4`, die Tabelle rechnet aber mit 450 g. Bei Teriyaki Wok stützt der
  Tag „High Protein" die Tabelle (20,8 % Energie) und schliesst die Badges aus (11,2 %).
- **Kaputte Tags in `tags_broken`** ablegen, nicht in `tags`: Dal Delight zeigt im
  Filter-UI die unübersetzten Platzhalter „ohne Recipe without Gluten" und
  „ohne Recipe without Soy".
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
