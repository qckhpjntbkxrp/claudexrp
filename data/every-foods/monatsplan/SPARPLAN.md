# Optimierung auf Preis und Nährstoffdichte

Ziel war ~150 € im Monat für zwei Personen. Hier die Rechnung und die ehrliche
Antwort, wo die Grenze liegt.

## Ergebnis

| Variante | Spanne | Mitte | kcal/Person/Tag | kcal je € |
|---|---:|---:|---:|---:|
| Ausgangsplan (Excel, unverändert) | 388–732 € | 505 € | 2155 | 256 |
| **Sparplan, alle Nährstoffziele erhalten** | **174–336 €** | **255 €** | 2135 (99 %) | **503** |
| 150-€-Variante, mit Abstrichen | 142–272 € | 207 € | 2015 (94 %) | 585 |

**Die Nährstoffdichte je Euro verdoppelt sich** — 503 statt 256 kcal je Euro, bei
praktisch unveränderter Energie und ohne einen einzigen kritischen Nährstoffträger
zu streichen.

**150 € sind erreichbar, aber nur als unteres Ende der gekürzten Variante** — also
mit konsequentem Aktionskauf *und* den Abstrichen unten. Der Mittelwert der
Sparversion liegt bei 255 €, der der gekürzten bei 207 €. Wer 150 € als festen
Monatswert plant, plant zu knapp.

## Was den Preis halbiert — ohne Nährstoffverlust

**1. Die Rotationsgruppen ernst nehmen.** Der Plan schreibt in Zeile 2 selbst:
*„pro Einkauf 2–3 Vertreter wechseln"*. Die Monatsliste kaufte alle Vertreter jeden
Monat — 8 Hülsenfrüchte, 9 Getreide, 10 Nüsse, 6 Pilze, 8 Früchte. Reduziert auf
je 3–4 Vertreter, **Gesamtmenge unverändert**, aber die billigsten Träger.

**2. Redundanz bei den Teuersten streichen.** Tempeh (12–19 €/kg), Seitan, Halloumi,
Bergkäse und Kimchi decken dieselben Nährstoffe wie Eier, Joghurt und Sauerkraut —
zum drei- bis fünffachen Preis. Gruppe D fällt von 84 € auf 24 €.

**3. TK statt frisch, wo es gleichwertig ist.** Spinat TK kostet 2 €/kg statt 8 €/kg
für Frischspinat, Beeren TK 5,75 statt 12–26 €. Der Saisonkalender sagt zu TK-Beeren
selbst *„nährstofflich gleichwertig"*. Vogerlsalat (10–19 €/kg) und Rucola fallen weg.

**4. Kalorien aus den billigsten Trägern holen.** Vollkornmehl kostet **0,44 € je
1000 kcal**, Haferflocken 0,49 €, Nudeln 0,71 € — Weisskraut dagegen 7,60 €, Äpfel
4,52 €. Deshalb steigen im Sparplan Mehl, Hafer, Nudeln und Hülsenfrüchte deutlich
an, während teures Wasser-Gemüse und Obst sinken. Brot selbst backen statt TK-Brot
kaufen spart allein 5 €.

**5. Pilze auf Champignons reduzieren.** Austernpilze, Shiitake frisch und
Kräuterseitlinge kosten 10–26 €/kg für denselben Beta-Glucan-Effekt wie Champignons
zu 4–7,50 €. Gruppe K fällt von 28 € auf 5 €. Getrocknete Shiitake bleiben — sie sind
mit 2 €/Monat der Vitamin-D2-Hebel.

## Was bewusst bleibt

Diese Posten sind teuer, aber im Plan durch nichts ersetzbar — sie decken laut
Nährstoff-Check die kritischen Punkte:

| Position | Kosten/Monat | Warum |
|---|---:|---|
| Algenöl EPA/DHA | 12,75 € | eine der zwei echten Lücken, keine Lebensmittelquelle |
| Vitamin D3 | 6,30 € | zweite echte Lücke, Okt–Mrz keine Eigensynthese |
| Kürbiskerne | 4,20 € | wichtigste Zinkquelle |
| Leinsamen + Leinöl | 4,95 € | ALA, billigste Omega-3-Quelle |
| Paranüsse | 3,17 € | Selen, CH/AT-Böden sind selenarm |
| Jodsalz | 0,13 € | im Alpenraum nicht optional |
| Zitrusfrüchte | 5,40 € | Vitamin C trägt die Eisenaufnahme aus Hülsenfrüchten |

## Was die 150-€-Variante zusätzlich kostet — nicht in Geld

- **Algenöl fällt ganz weg.** Damit ist EPA/DHA offen. Das ist der teuerste einzelne
  Posten und gleichzeitig der, den der Nährstoff-Check ausdrücklich als nicht über
  Lebensmittel ersetzbar bezeichnet. **Das ist die schmerzhafteste Streichung.**
- **Eier von 40 auf 24, Skyr und Joghurt halbiert.** B12 wird damit knapp — bei
  ovo-lacto war es vorher „meist ausreichend", jetzt ist es Beobachtungsfall.
- **Kein Tofu, keine Champignons, keine TK-Beeren, keine Butter, weniger Zitrus.**
  Weniger Vitamin C zur Eisenmahlzeit heisst schlechtere Eisenaufnahme — genau der
  Hebel, den die Komplementärpaare als *„wichtigster Hebel der ganzen Liste"* führen.
- Energie fällt auf 94 % des Solls.

**Empfehlung:** die volle Sparversion nehmen und beim Einkauf konsequent auf Aktionen
gehen. Damit landest du realistisch bei **174–210 €** und behältst alle Nährstoffziele.
Die 150 € sind erreichbar, kosten aber genau die zwei Dinge, die dein eigener Plan als
nicht verhandelbar markiert hat.

## Dateien

- [einkauf-spar-2p.txt](einkauf-spar-2p.txt) — Sparplan, alle Nährstoffziele erhalten
- [einkauf-spar-150-2p.txt](einkauf-spar-150-2p.txt) — gekürzte Variante

Neu rechnen: `python3 data/every-foods/tools/sparplan.py`
