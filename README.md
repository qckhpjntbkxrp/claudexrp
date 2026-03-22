# xrpl-x402

**x402 Payment Gateway for the XRP Ledger — AI agents pay for APIs with XRP micropayments.**

```
Agent calls API → gets 402 → pays 0.001 XRP on XRPL → retries → gets data
```

## What this does

Implements the [x402 protocol](https://www.x402.org/) on the XRP Ledger. Any API can accept XRP micropayments from AI agents using standard HTTP. No Stripe. No API keys. No subscriptions.

- **Express middleware** — add `x402()` to any route to charge XRP per request
- **Client SDK** — agents auto-detect 402 responses, pay on XRPL, retry transparently
- **MCP server** — 6 tools for AI agents (create wallet, pay invoices, verify payments)
- **OpenAPI 3.1 spec** — machine-readable API documentation

## Why XRPL

| Feature | XRPL | Base (EVM) |
|---|---|---|
| Transaction cost | ~$0.0005 | ~$0.01-0.10 |
| Finality | 3-5 seconds | ~2 seconds |
| Native DEX | Yes | No |
| Payment channels | Built-in | Smart contract |
| MEV/front-running | None | Possible |

## Quick Start

### For API Providers (accept XRP payments)

```bash
npm install xrpl-x402
```

```typescript
import express from "express";
import { x402 } from "xrpl-x402/middleware";

const app = express();

app.get("/api/data", x402({
  destination: "rYourAddress...",
  amount: "0.001",        // XRP per request
  network: "testnet",
}), (req, res) => {
  res.json({ data: "premium content" });
});

app.listen(3000);
```

### For AI Agents (pay for APIs)

```typescript
import { X402Client, createWallet } from "xrpl-x402";

const wallet = await createWallet("testnet");
const client = new X402Client({ seed: wallet.seed });

// Payment happens automatically when the API returns 402
const result = await client.get("http://api.example.com/data");
console.log(result.data);     // { data: "premium content" }
console.log(result.payment);  // { txHash: "ABC...", amount: "0.001" }
```

### MCP Server (for Claude, Cursor, etc.)

```json
{
  "mcpServers": {
    "xrpl-x402": {
      "command": "npx",
      "args": ["tsx", "src/mcp/index.ts"]
    }
  }
}
```

**Available MCP tools:**

| Tool | Description |
|---|---|
| `create_wallet` | Create a new XRPL wallet (auto-funded on testnet) |
| `get_balance` | Check XRP balance |
| `pay_invoice` | Pay an x402 invoice on XRPL |
| `check_payment` | Verify a payment settled on-ledger |
| `list_transactions` | List recent wallet transactions |
| `estimate_cost` | Estimate total cost including fees |

## x402 Protocol Flow

```
Agent                          API Server                    XRP Ledger
  |                               |                             |
  |-- GET /api/data ------------->|                             |
  |<-- 402 Payment Required ------|                             |
  |   {                           |                             |
  |     destination: "rAddr...",  |                             |
  |     amount: "0.001",          |                             |
  |     invoiceId: "uuid",        |                             |
  |     network: "xrpl:testnet"   |                             |
  |   }                           |                             |
  |                               |                             |
  |-- XRPL Payment (0.001 XRP) --|----------------------------->|
  |<-- tx hash ------------------|<-----------------------------|
  |                               |                             |
  |-- GET /api/data ------------->|                             |
  |   X-Payment-Tx-Hash: <hash>  |                             |
  |                               |-- verify tx --------------->|
  |                               |<-- verified ----------------|
  |<-- 200 { data: "..." } ------|                             |
```

## HTTP Headers

### Request headers (from agent)
- `X-Payment-Tx-Hash` — XRPL transaction hash proving payment
- `X-Payment-Invoice-Id` — Invoice ID from the 402 response (optional, for strict matching)

### Response headers (402 challenge)
- `X-Payment-Amount` — Amount in XRP to pay
- `X-Payment-Destination` — XRPL address to pay
- `X-Payment-Network` — `xrpl:testnet` or `xrpl:mainnet`
- `X-Payment-Invoice-Id` — UUID to include in XRPL payment's InvoiceID field
- `X-Payment-Expiry` — ISO 8601 timestamp when the invoice expires

### Response headers (200 after payment)
- `X-Payment-Verified` — `true`
- `X-Payment-Tx-Hash` — The verified transaction hash
- `X-Payment-Amount` — Amount paid
- `X-Payment-Source` — The agent's XRPL address

## Error Handling

All errors follow a consistent schema with actionable suggestions:

```json
{
  "error": {
    "code": "PAYMENT_INSUFFICIENT",
    "message": "Insufficient amount: expected 0.001 XRP, got 0.0005 XRP",
    "suggestion": "Send at least 0.001 XRP to the destination address."
  }
}
```

**Error codes:** `PAYMENT_REQUIRED`, `PAYMENT_INVALID`, `PAYMENT_EXPIRED`, `PAYMENT_INSUFFICIENT`, `PAYMENT_WRONG_DESTINATION`, `PAYMENT_NOT_FOUND`, `PAYMENT_NOT_VALIDATED`, `VERIFICATION_FAILED`, `WALLET_INSUFFICIENT_FUNDS`, `NETWORK_ERROR`, `AMOUNT_EXCEEDS_MAX`

## Run the Demo

```bash
# Start the demo server (creates a testnet merchant wallet automatically)
npm run demo

# In another terminal:
curl http://localhost:3000/api/health          # Free
curl http://localhost:3000/api/price/XRP        # Returns 402 with payment instructions
```

## Development

```bash
npm install
npm run build       # Compile TypeScript
npm run demo        # Start demo server
npm run mcp         # Start MCP server
npm test            # Run tests
```

## Architecture

```
src/
├── core/           # XRPL utilities (wallet, payment, verification)
├── middleware/      # Express x402 middleware (for API providers)
├── client/         # x402 HTTP client (for AI agents)
├── mcp/            # MCP server (6 tools for AI agents)
└── demo/           # Demo API server with paid endpoints
```

## License

MIT
