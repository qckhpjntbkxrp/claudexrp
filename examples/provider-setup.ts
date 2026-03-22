/**
 * Example: Add x402 XRP payments to your Express API in 5 lines.
 *
 * Any AI agent can now pay for your API with XRP micropayments.
 * No Stripe. No API keys. No subscriptions.
 */
import express from "express";
import { x402 } from "../src/middleware/index.js";

const app = express();

// Free endpoint — no payment needed
app.get("/api/status", (_req, res) => {
  res.json({ status: "online" });
});

// Paid endpoint — costs 0.001 XRP per call
app.get(
  "/api/data",
  x402({
    destination: "rYourXrplAddress...", // Your XRPL address
    amount: "0.001", // XRP per request
    network: "testnet", // or "mainnet" for production
  }),
  (_req, res) => {
    res.json({ data: "This is premium data the agent paid 0.001 XRP for" });
  }
);

app.listen(3000, () => console.log("API with x402 payments running on :3000"));
