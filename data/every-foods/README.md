# every Foods — Gerichte-Datenbank

Manuell übertragene Produktdaten von [everyfoods.ch](https://everyfoods.ch).
Die Session hat keinen Netzzugriff auf die Domain (Egress-Proxy blockt sie), deshalb
werden die Daten per Copy-Paste aus dem Browser eingepflegt.

## Struktur

```
data/every-foods/
├── README.md            ← diese Datei: Index, Konventionen, Vergleichstabelle
├── dishes/
│   └── <slug>.md        ← ein File pro Gericht, YAML-Frontmatter + Fliesstext
├── rezepte/             ← Nachbau-Rezepte mit Grammangaben und Lidl-Produkten
├── tools/               ← check_claims.py, check_recipe.py, tune_recipe.py
└── meine-auswahl.md     ← persönliche Arbeitskopie (Personalisierung)
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
| [Paprika Thai Ragout](dishes/paprika-thai-ragout.md) | 500 g | 510 | 25,0 g | 66,5 g | 13,0 g | 1,0 g | 13,0 g | 2,4 g | 19,6 % | Proteinquelle |
| [Peanut Noodles](dishes/peanut-noodles.md) | 450 g | 491 | 20,3 g | 48,2 g | 23,4 g | 2,7 g | 8,1 g | 3,4 g | 16,5 % | Proteinquelle |
| [Peas & Love](dishes/peas-and-love.md) | 500 g | 545 | 22,0 g | 67,0 g | 18,5 g | 3,0 g | 11,5 g | 2,8 g | 16,1 % | Proteinquelle |
| [Sesame Fried Rice](dishes/sesame-fried-rice.md) | 400 g | **748** | 19,6 g | 80,8 g | 35,6 g | 4,8 g | 12,4 g | 3,0 g | **10,5 %** | *(kein Claim)* |

Alle Werte pro Portion aus der offiziellen Nährwerttabelle. **Achtung:** die
Portionsgrösse variiert (400 g / 450 g / 500 g) — für faire Vergleiche ggf. auf 100 g
normalisieren.

## Status

- **17 Gerichte erfasst, alle als Protein-Bundle-Gerichte bestätigt**
  (`in_protein_bundle: ja`)
- Offen: Preis pro Gericht

### Bundle-Zuordnung

Alle erfassten Gerichte gehören zum Protein Bundle. Das Bundle wird in Boxen zu
**12, 16 oder 20 Gerichten** verkauft — die 17 Gerichte sind also der Auswahlpool,
aus dem eine Box zusammengestellt wird, nicht der Inhalt einer einzelnen Box.

Beworben sind **ø 23 g Protein und ø 11 g Ballaststoffe pro Gericht**. Über alle 17:
**ø 23,3 g Protein**, **ø 11,7 g Ballaststoffe**, ø 500 kcal. Beide Versprechen sind
im Mittel eingehalten, streuen aber erheblich (Protein 19,6–27,9 g).

Zwei Gerichte waren schon vor der Bestätigung über Nährwertfragmente der Bundle-Seite
belegt: **Chili sin Carne** und **Tikka Masala**.

**Das Label taugt nicht als Filter.** „Proteinquelle" und „High Protein" sind
EU-Nährwertclaims auf Basis des **Energieanteils**, nicht der absoluten Menge:

| Claim | Bedingung |
|---|---|
| Proteinquelle | ≥ 12 % der Energie aus Protein |
| High Protein | ≥ 20 % der Energie aus Protein |

Die Rechnung (`Protein_g × 4 / kcal`) geht bei allen Gerichten auf. Deshalb trägt
**Nasi Goreng mit 25,7 g Protein nur „Proteinquelle"** (19,5 %), während **Better
Butter Chicken mit 24,0 g „High Protein"** trägt (20,4 %): das fettreichere Gericht
hat mehr Gesamtenergie. Nur 6 der 17 Bundle-Gerichte erfüllen den High-Protein-Claim (Umami Rice, Bami Goreng,
Teriyaki Wok, Smoky Lentil Stew, Chili sin Carne, Better Butter Chicken).
**Sesame Fried Rice** erreicht mit 10,5 % nicht einmal „Proteinquelle" und trägt als
einziges Bundle-Gericht gar keinen Protein-Claim.

**Rangliste nach Protein pro Portion:**

| # | Gericht | Protein | kcal | % Energie |
|---:|---|---:|---:|---:|
| 1 | Umami Rice | 27,9 g | 424 | 26,3 % |
| 2 | Bami Goreng | 27,0 g | 468 | 23,1 % |
| 2 | Teriyaki Wok | 27,0 g | 520 | 20,8 % |
| 4 | Nasi Goreng | 25,7 g | 527 | 19,5 % |
| 5 | Paprika Thai Ragout | 25,0 g | 510 | 19,6 % |
| 6 | Chili sin Carne | 24,8 g | 446 | 22,2 % |
| 7 | Better Butter Chicken | 24,0 g | 470 | 20,4 % |
| 8 | Dal Delight | 23,9 g | 491 | 19,4 % |
| 8 | Smoky Lentil Stew | 23,9 g | 374 | 25,5 % |
| 10 | Tikka Masala | 23,4 g | 491 | 19,1 % |
| 11 | Peas & Love | 22,0 g | 545 | 16,1 % |
| 12 | Creamy Paprika Pasta | 21,2 g | 446 | 19,0 % |
| 13 | Edamame Zen | 20,3 g | 423 | 19,1 % |
| 13 | Green Forest Bowl | 20,3 g | 599 | 13,5 % |
| 13 | Peanut Noodles | 20,3 g | 491 | 16,5 % |
| 16 | Brilliant Bolognese | 20,0 g | 520 | 15,4 % |
| 17 | Sesame Fried Rice | 19,6 g | 748 | 10,5 % |

Die 10 Gerichte ab 23 g liefern im Schnitt **25,3 g** — eine Bundle-Auswahl daraus
läge über dem beworbenen Wert.

**Bestes Protein pro Kalorie:** Umami Rice (6,6 g/100 kcal) und Smoky Lentil Stew
(6,4 g/100 kcal bei nur 374 kcal). **Schwächstes:** Sesame Fried Rice
(2,6 g/100 kcal bei 748 kcal).

**Salz ist die Schwachstelle der Reihe:** ø 3,1 g pro Portion, Spanne 2,25–3,92 g.
Ein einziges Gericht deckt im Schnitt **61 % der WHO-Tagesempfehlung** (5 g); zwei
Gerichte am Tag überschreiten sie zuverlässig.

## Datenqualität: regulierte Claims vs. Marketing-Tags

Die Tags auf den Produktseiten zerfallen in zwei Gruppen mit **gegensätzlicher
Zuverlässigkeit**:

**Regulierte Nährwertclaims — alle korrekt.** „Proteinquelle", „High Protein",
„Source of Fiber", „Hoher Ballaststoffgehalt", „fettarm", „arm an gesättigten
Fettsäuren", „zuckerarm" unterliegen VO (EG) Nr. 1924/2006. `tools/check_claims.py`
prüft sie gegen die erfassten Nährwerte:

```
$ python3 data/every-foods/tools/check_claims.py
74 Claims in 17 Gerichten geprüft.
Alle regulierten Nährwertclaims erfüllen ihre Schwellenwerte.
```

Bemerkenswert: die Ballaststoff-Claims stützen sich durchweg auf die **Alternativ-
schwelle pro 100 kcal** (≥ 1,5 bzw. ≥ 3 g/100 kcal), nicht auf die g/100-g-Schwelle —
über 100 g allein würde kein einziges Gericht den Claim tragen dürfen. Zulässig, aber
gut zu wissen, wenn man Ballaststoffe pro Portion vergleicht.

**Nicht regulierte Filter-Tags — unzuverlässig.** „ohne Zwiebeln", „ohne Paprika",
„nicht scharf", „ohne Zuckerzusatz" und „Wenig Kohlenhydrate" (letzteres kein
zugelassener EU-Claim) widersprechen bei **7 von 17 Gerichten** der eigenen
Zutatenliste. Siehe Konventionen unten.

Kurz: was der Gesetzgeber prüft, stimmt. Was das Marketing selbst vergibt, nicht.

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
- **Allergene** aus den GROSSGESCHRIEBENEN Zutaten ableiten. Erdnuss kommt sowohl
  als Zutat (Peanut Noodles, 8 %) wie als Spur (Paprika Thai Ragout) vor.
- **Tag-Synonyme:** dieselbe Aussage taucht in beiden Sprachen auf („Source of Fiber"
  / „Ballaststoffquelle"). Beim Erweitern von `check_claims.py` beide Schreibweisen
  eintragen.
- **`in_protein_bundle`:** `ja` / `nein` / `unbekannt`.
- **Slug** = Handle aus der Produkt-URL (`/products/<slug>`).

## Neues Gericht hinzufügen

Text von der Produktseite hier in den Chat einfügen — Reihenfolge egal, Rohtext genügt.
Daraus entsteht `dishes/<slug>.md` nach dem Muster von `bami-goreng.md`, und die
Vergleichstabelle oben wird nachgeführt.
