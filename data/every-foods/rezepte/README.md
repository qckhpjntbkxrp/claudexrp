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

## Personalisierung

Alle Rezepte sind **ohne Kümmel, Kreuzkümmel und Koriander** ausgeführt (siehe
[meine-auswahl.md](../meine-auswahl.md)). Da diese Gewürze in Mengen unter 1 g
vorkommen, ändert das an den Nährwerten nichts. Bei **Paprika Thai Ragout** stecken
beide in der Thai-Paste — die muss dafür selbst angesetzt werden.
