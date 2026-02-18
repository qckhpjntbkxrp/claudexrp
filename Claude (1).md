# PATIENT ALGORITHM

Du bist ein erfahrener XRPL-Entwickler. Dein Auftrag: Baue einen Trading-Bot für die XRPL DEX, der über Zeit netto mehr XRP im Wallet hält als zu Beginn.

**XRP ist die einzige Referenzwährung.** Erfolg = mehr XRP als vorher. P&L wird ausschließlich in XRP gemessen. Gehandelte Gegenwährungen sind nur Vehikel – kein Ziel. Der Algorithmus soll geduldig sein. Lieber warten als schlecht handeln.

## HANDELSPAARE

Der Bot handelt NICHT nur ein einzelnes Paar. Implementiere Unterstützung für **mehrere Paare gleichzeitig**, konfigurierbar. Jedes Paar besteht aus XRP und einem issued Token auf dem XRPL. Beispiele:

```yaml
pairs:
  - currency: "USD"
    issuer: "rvYAfWj5gh67oV6fW32ZzP3Aw4Eubs59B"    # Bitstamp
  - currency: "EUR"
    issuer: "rhub8VRN55s94qWKDv6jmDy1pUykJzF3wq"    # GateHub
```

Neue Paare hinzufügen = nur Config ändern, kein Code. Der Bot muss pro Paar eine Trustline prüfen/einrichten und das Grid unabhängig verwalten.

## TECHNISCHER STACK

- **Python 3.11+**, `xrpl-py` mit `JsonRpcClient` (synchron, offiziell empfohlen)
- **Config:** YAML für Parameter, `.env` für Secrets (XRPL_SECRET, TELEGRAM_*)
- **State:** Persistiert in Datei, überlebt Neustarts
- **Benachrichtigungen:** Telegram Bot API
- **Testnet / Mainnet** umschaltbar per Config:
  - Testnet: `https://s.altnet.rippletest.net:51234/` + `generate_faucet_wallet()`
  - Mainnet: `https://s2.ripple.com:51234/` + Wallet aus .env
- **Erster Testlauf IMMER auf Testnet**

## XRPL DEX API

Nutze die offiziellen `xrpl.models`. Bei Unsicherheit: xrpl.org/docs konsultieren.

### Lesen
| Zweck | Modell | Wichtige Felder |
|---|---|---|
| XRP-Balance + OwnerCount | `AccountInfo` | `account_data.Balance` (Drops!), `OwnerCount` |
| Token-Balance | `AccountLines` (peer-Filter) | `lines[].balance` |
| Orderbook | `BookOffers` (Asks + Bids) | `quality`, `owner_funds`, `taker_gets_funded` |
| Eigene Offers | `AccountOffers` | `seq`, `taker_gets`, `taker_pays`, `flags` |
| Reserves (dynamisch!) | `ServerInfo` | `reserve_base_xrp`, `reserve_inc_xrp` |
| AMM-Liquidität | `AMMInfo` | Pool-Größe pro Paar |

### Schreiben
| Zweck | Transaction | Besonderheiten |
|---|---|---|
| Kaufen | `OfferCreate` | `flags=65536` (tfPassive), `Expiration` setzen |
| Verkaufen | `OfferCreate` | `Expiration` setzen |
| Order ersetzen | `OfferCreate` + `offer_sequence` | Atomar: Cancel + Create in 1 TX |
| Order canceln | `OfferCancel` | `offer_sequence` = `seq` aus AccountOffers |
| Trustline | `TrustSet` | Pro Paar, kostet 0.2 XRP Reserve |

Transaktionsergebnis immer prüfen: `tesSUCCESS` = OK.

## KRITISCHE XRPL-EIGENHEITEN

1. **Drops ≠ XRP:** 1 XRP = 1.000.000 Drops. Nutze `xrpl.utils.xrp_to_drops()` / `drops_to_xrp()`.
2. **Ripple Epoch ≠ Unix Epoch:** Offset 946.684.800s. Falsches Epoch = Offers expiren sofort.
3. **Partial Fills:** `account_offers` zeigt verbleibende Menge, nicht ursprüngliche.
4. **Unfunded Offers:** Können ohne Fill verschwinden. Verschwunden ≠ gefüllt.
5. **Reserves dynamisch:** NIEMALS hartcodieren. Per `ServerInfo` abfragen.
6. **tfPassive (65536):** Ohne Flag können Orders sofort matchen statt passiv zu warten.
7. **OfferSequence:** Ist die `seq` der Offer, NICHT die Account-Sequence.

## SAFETY

- Alle Offers mit Expiration als Crash-Safety
- Bei Neustart: State mit Ledger-Offers abgleichen
- Bot muss erkennen wenn XRP knapp wird und sich schützen
- Fehler-Eskalation über Telegram

## CODE-ANFORDERUNGEN

- Jedes Modul einzeln testbar
- Type Hints, Docstrings, kommentierter Code
- Alle Parameter konfigurierbar, keine Magic Numbers
- `.env` für Secrets, nie im Code

## REFERENZ

- https://xrpl.org/docs/tutorials/python/build-apps/get-started
- https://xrpl.org/docs/tutorials/how-tos/use-tokens/trade-in-the-decentralized-exchange
- https://xrpl.org/docs/references/protocol/transactions/types/offercreate
- https://xrpl.org/docs/concepts/accounts/reserves
- https://xrpl.org/docs/concepts/tokens/decentralized-exchange/automated-market-makers
