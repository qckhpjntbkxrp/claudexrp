# Echte Lidl-Österreich-Preise beschaffen

Die Preise in `preise-lidl.yaml` sind Schätzungen. Hier die Wege zu belastbaren
Werten, sortiert nach Aufwand und Verlässlichkeit.

## 1. Lidl Plus App — die beste Quelle

Die kostenlose **Lidl Plus App** archiviert jeden Kassenbon digital. Nach dem ersten
Einkauf hast du damit **exakte Preise für genau die Artikel, die du gekauft hast** —
inklusive Aktionsrabatt, mit Datum und Filiale. Kein anderer Weg liefert Realpreise
so präzise.

Die App hat ausserdem eine Artikelsuche und eine digitale Einkaufsliste.

**Vorgehen:** einmal einkaufen, dann Bon in der App durchgehen und die Werte in
`preise-lidl.yaml` eintragen. Ab dann rechnen alle Skripte mit echten Zahlen.

## 2. lidl.at Flugblatt — für Aktionen, nicht für Grundsortiment

[lidl.at/c/flugblatt/s10012330](https://www.lidl.at/c/flugblatt/s10012330) zeigt das
aktuelle Flugblatt online, wöchentlich neu.

**Einschränkung:** Lidl Österreich verkauft **keine Lebensmittel online**. Auf der
Website stehen nur Aktionsartikel mit Preis, nicht das Dauersortiment. Für Nudeln,
Reis, Öl und Konserven — also den Grossteil dieser Liste — findest du dort nichts.

## 3. Prospekt-Plattformen — Aktionen mehrerer Händler

- [marktguru.at/r/lidl](https://www.marktguru.at/r/lidl) — Lidl-Angebote, auch nach Bundesland
- [aktionsfinder.at](https://www.aktionsfinder.at/) — über 150 Flugblätter, App verfügbar
- [kimbino.at/lidl](https://www.kimbino.at/lidl/), [kupino.at/angebote/lidl](https://www.kupino.at/angebote/lidl)
- wogibtswas.at

Gleiche Einschränkung wie beim Flugblatt: **nur Aktionsware**. Nützlich, um den
Einkaufstag zu legen — Paprika und Vemondo sind die Posten, bei denen sich das lohnt.

## 4. AK Preismonitor — Vergleichsdaten, keine Einzelpreise

Die Arbeiterkammer erhebt regelmässig Preise in je drei Filialen von sieben Wiener
Supermärkten, Lidl inklusive:

- [wien.arbeiterkammer.at/preismonitor](https://wien.arbeiterkammer.at/preismonitor)
- [wien.arbeiterkammer.at/preisradar](https://wien.arbeiterkammer.at/preisradar)
- [arbeiterkammer.at/lebensmittel-und-drogeriewaren](https://www.arbeiterkammer.at/lebensmittel-und-drogeriewaren)

Veröffentlicht werden Warenkorb-Auswertungen als PDF, keine durchsuchbare
Einzelpreis-Datenbank. Gut zur Plausibilitätsprüfung: liegt eine Schätzung hier
komplett daneben, fällt es auf.

## 5. Private Plattformen

[preismonitor.at](https://preismonitor.at/) und [preismonitor.net](https://preismonitor.net/)
vergleichen österreichische Lebensmittelpreise. Datenqualität und Abdeckung des
Lidl-Eigenmarkensortiments sind ungeprüft — vor dem Verlassen selbst ansehen.

## 6. Scraper-APIs — nicht empfohlen

Kommerzielle Anbieter (Apify, ShoppingScraper, Piloterr, RealDataAPI) verkaufen
Lidl-Scraper. **Lidl betreibt keine offizielle öffentliche API.** Diese Dienste
kosten Geld, zielen meist auf den deutschen Onlineshop statt auf das
österreichische Filialsortiment, und Scraping berührt die Nutzungsbedingungen.
Für eine Handvoll Zutaten steht das in keinem Verhältnis zum Kassenbon aus Punkt 1.

## Empfehlung

**Punkt 1 plus Punkt 3.** Vor dem Einkauf kurz marktguru prüfen, ob Paprika oder
Vemondo gerade in Aktion sind; nach dem Einkauf die echten Werte vom Lidl-Plus-Bon
in `preise-lidl.yaml` übertragen. Danach ist jede weitere Rechnung in diesem Projekt
mit Realpreisen unterlegt.
