# Nachbau-Rezepte

Für jedes der 17 Bundle-Gerichte eine Zutatenliste **mit Grammangaben pro Portion**,
so gewählt, dass die Nährwerte möglichst nah an der Deklaration von every Foods liegen.

## Dateien

```
rezepte/
├── zutaten-db.yaml     Nährwerte je 100 g + vorgeschlagenes Lidl-Produkt
└── <slug>.yaml         ein Rezept je Gericht, Mengen in Gramm
```

Prüfen und nachjustieren:

```bash
python3 data/every-foods/tools/check_recipe.py            # alle Rezepte durchrechnen
python3 data/every-foods/tools/check_recipe.py umami-rice # einzeln
python3 data/every-foods/tools/tune_recipe.py  umami-rice # Mengen automatisch anpassen
```

`tune_recipe.py` verändert nur die unter `levers:` gelisteten Zutaten und hält das
Gesamtgewicht exakt auf der Portionsgrösse. Zusätzlich gelten Schranken: Lever dürfen
zwischen dem 0,55- und 1,8-fachen ihres Ausgangswerts wandern, alle übrigen Zutaten nur
zwischen 0,85 und 1,15 — sonst optimiert der Tuner Zutaten aus dem Rezept heraus.

Die Kommentare hinter den Mengen vergleichen den **deklarierten** Prozentanteil von
every Foods mit dem Anteil im Rezept. Wo beide auseinandergehen, war die Nährwert-Nähe
wichtiger als der exakte Anteil.

## Zur Lidl-Zuordnung — wichtig

Die Spalte `lidl:` in `zutaten-db.yaml` nennt **Lidl-Eigenmarken aus Erfahrungswissen**,
nicht aus dem aktuellen Sortiment: die Session hat keinen Netzzugriff auf lidl.at.
**Verfügbarkeit und exakte Nährwerte im Markt gegenprüfen** und bei Bedarf die Zeile
anpassen — jedes Produkt hängt an genau einer Stelle.

Ebenso stammen die Nährwerte je 100 g aus Standard-Lebensmitteltabellen, nicht von der
Packung. Sie sind für den Zweck genau genug, ersetzen aber kein Etikett.

## Toleranzen

`check_recipe.py` meldet eine Abweichung erst, wenn sie **relativ** (kcal/Makros 10 %,
Zucker/Ballaststoffe 20 %, ges. Fettsäuren 25 %, Salz 15 %) **und absolut** relevant
ist — bei 0,9 g gesättigten Fettsäuren sagt eine Prozentangabe nichts aus.

**15 von 17 Rezepten liegen vollständig in der Toleranz.** Zwei nicht:

| Gericht | Abweichung | Grund |
|---|---|---|
| Smoky Lentil Stew | Ballaststoffe −30 % | 22 g Ballaststoffe bei 374 kcal und 10 g Fett sind aus den deklarierten Zutaten nicht gleichzeitig darstellbar |
| Dal Delight | Eiweiss −12 %, Ballaststoffe +20 % | deklariertes Eiweiss-zu-Ballaststoff-Verhältnis (1,47) liegt über dem von gekochten Hülsenfrüchten (1,1–1,2) |

Beides ist in der jeweiligen Rezeptdatei dokumentiert. Es sind keine Rechenfehler,
sondern Hinweise darauf, dass die every-Deklaration mehr Ballaststoffe bzw. Protein
ausweist, als die genannten Zutaten nach Standardwerten hergeben.

## Kosten

`preise-lidl.yaml` hält je Zutat den geschätzten Kilopreis, die übliche
Packungsgrösse und einen **Kauffaktor** — Gramm Einkaufsware je Gramm im Rezept.
Der Faktor rechnet Trockenware hoch (157 g gekochte Nudeln = 63 g Trockennudeln,
Faktor 0,40) und Putzverlust ein (Lauch 1,30).

```bash
python3 data/every-foods/tools/kosten.py            # Kosten je Gericht
python3 data/every-foods/tools/kosten.py --liste    # Einkaufsliste in Packungen
python3 data/every-foods/tools/kosten.py --plan     # Umfang des Erstkaufs
```

Stand der Schätzung: **ø 1,59 € Zutatenkosten je Portion**, Spanne 0,82 €
(Brilliant Bolognese) bis 2,27 € (Teriyaki Wok). Alle 17 Gerichte je einmal:
**27,02 €**.

Der erste Einkauf kostet mehr, weil Packungen ganz gekauft werden: **rund 153 €**,
davon **126 € Vorrat**, der für weitere Durchgänge reicht. Ab dem zweiten Durchgang
zählen nur noch die verbrauchten Zutaten.

### Vergleich mit dem Bundle

Annahme: 16er-Box zu **10,— je Gericht = 160,— je Box**.

| | Kosten | ø je Gericht | €/100 g Protein |
|---|---:|---:|---:|
| every Protein Bundle, 16 Gerichte | 160,00 € | 10,00 € | 42,51 € |
| Nachbau, dieselben 16 Gerichte | 25,37 € | 1,59 € | 6,74 € |

**Ersparnis 134,63 € je Box, Faktor 6,3.** Selbst der erste Einkauf in ganzen
Packungen (152,98 €, inkl. 126 € Vorrat) liegt unter dem Preis einer einzigen Box.

### Wie viele Gerichte lohnen sich beim Erstkauf?

`--plan` beantwortet das. Der Erstkauf ist von Vorratsposten dominiert (Öl, Miso,
Nüsse, Gewürze) — die zahlt man einmal, egal wie viel gekocht wird. Entscheidend ist
deshalb **nicht die Anzahl der Gerichte, sondern die Portionen je Gericht**.

| Szenario | Erstkauf | Portionen | €/Portion | vs. Bundle |
|---|---:|---:|---:|---:|
| 4 Gerichte × 1 Portion | 43,72 € | 4 | 10,93 € | **−3,72 €** |
| 6 Gerichte × 1 Portion | 59,76 € | 6 | 9,96 € | ±0 |
| 16 Gerichte × 1 Portion | 126,47 € | 16 | 7,90 € | +33,53 € |
| **8 Gerichte × 4 Portionen** | **92,91 €** | **32** | **2,90 €** | **+227,09 €** |
| 16 Gerichte × 4 Portionen | 182,37 € | 64 | 2,85 € | +457,63 € |

**Unter 6 Gerichten lohnt sich der Erstkauf nicht** — da ist die Box billiger.
Ab 4 Portionen je Gericht fällt der Portionspreis auf rund 2,90 € und bleibt dort;
mehr Gerichtsvielfalt bringt dann kaum noch etwas, sie kostet nur zusätzliche
Vorratsposten.

**Sesame Fried Rice ist der teuerste Zugang: +26,51 €** allein für Pistazien, Mandeln,
roten Reis, Sesamöl und Miso — Zutaten, die kein anderes Gericht nutzt. Als 17. Gericht
hebt es den Portionspreis wieder an. Genau deshalb ist es der richtige Kandidat, wenn
aus 17 Gerichten eine 16er-Box werden soll.

### Vorrat gering halten

Vollständig durchgerechnet über alle 24.310 Achterkombinationen: **die kostenminimale
Auswahl ist zugleich die vorratsärmste** — es gibt keinen Zielkonflikt, dieselben acht
Gerichte gewinnen bei beiden Zielen. Das Selektieren ist damit ausgereizt; die
wirksamen Hebel sind zwei andere:

**1. Mehr Portionen je Gericht.** Der Vorratsanteil fällt mit jeder zusätzlichen
Portion, weil die Packungen dieselben bleiben:

| Portionen | Mahlzeiten | Einkauf | Vorrat | Anteil | €/Mahlzeit |
|---:|---:|---:|---:|---:|---:|
| 2 | 16 | 70,13 € | 44,10 € | 63 % | 4,38 € |
| 4 | 32 | 89,19 € | 37,13 € | 42 % | 2,79 € |
| 6 | 48 | 112,52 € | 34,44 € | 31 % | 2,34 € |
| 8 | 64 | 135,75 € | 31,64 € | 23 % | 2,12 € |

**2. Ein Gericht weniger.** Dal Delight streichen senkt den Vorrat von 37,13 € auf
**30,37 €** bei praktisch gleichem Preis je Mahlzeit (2,80 statt 2,79 €) — es bringt
Linsen, Kidney- und schwarze Bohnen, Süsskartoffelwürfel und Spinat mit, die kein
anderes der acht Gerichte nutzt. Liste dafür: **[einkauf-7x4.md](einkauf-7x4.md)**.

Der grösste Einzelrest ist ohnehin kein Verlust: Rapsöl (2,46 €), Sonnenblumenöl
(2,04 €), Kartoffeln, Zwiebeln, Basmatireis — Grundvorrat, den man weiterverwendet.
Ärgerlich sind nur die Spezialposten, allen voran **schwarze Bohnen: 24 g gebraucht
von 500 g gekauft** (1,72 € Rest). Wer bei Dal Delight bleiben will, ersetzt sie am
einfachsten durch mehr Kidneybohnen — nährwertlich fast deckungsgleich, spart eine
ganze Packung.

Eine fertige Liste für dieses Szenario liegt in
**[einkauf-8x4.md](einkauf-8x4.md)** — nach Ladenbereich sortiert, mit Packungszahlen.
Die Auswahl der 8 Gerichte ist per Tauschsuche kostenoptimiert (89,19 € statt 92,91 €
bei rein gieriger Wahl) und kommt trotzdem auf **ø 24,2 g Protein je Portion**.

Ab dem zweiten Durchgang zählen nur noch die verbrauchten Zutaten: **rund 1,60–1,75 €
je Portion**, unabhängig vom Umfang.

Fair bleibt der Vergleich nur mit dem Aufwand: 16 Gerichte kochen, portionieren und
einfrieren dauert realistisch 4–6 Stunden. Die Ersparnis entspricht damit einem
impliziten Stundenlohn von **22–34 €**. Nicht eingerechnet sind Energie, Gefrierdosen
und der Umstand, dass every schockgefrostet liefert.

**Die Preise sind Schätzungen**, nicht von lidl.at abgerufen — dieselbe Einschränkung
wie bei den Produktnamen. Eine Zeile in `preise-lidl.yaml` korrigieren, Skript neu
laufen lassen.

## Personalisierung

Alle Rezepte sind **ohne Kümmel, Kreuzkümmel und Koriander** ausgeführt (siehe
[meine-auswahl.md](../meine-auswahl.md)). Da diese Gewürze in Mengen unter 1 g
vorkommen, ändert das an den Nährwerten nichts. Bei **Paprika Thai Ragout** stecken
beide in der Thai-Paste — die muss dafür selbst angesetzt werden.
