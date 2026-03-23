import express from "express";
import { x402 } from "../middleware/index.js";
import { createWallet } from "../core/wallet.js";
import { disconnectAll } from "../core/xrpl-client.js";

const PORT = Number(process.env.PORT ?? 3000);

async function main() {
  console.log("🚀 Starting x402 XRPL demo server...");
  console.log("📡 Creating merchant wallet on XRPL Testnet...");

  // Create a merchant wallet on testnet (auto-funded)
  const merchant = await createWallet("testnet");
  console.log(`💰 Merchant wallet: ${merchant.address}`);
  console.log(`🔑 Merchant seed:   ${merchant.seed}`);

  const app = express();
  app.use(express.json());

  // --- Free endpoint ---
  app.get("/api/health", (_req, res) => {
    res.json({
      status: "ok",
      service: "x402-xrpl-demo",
      network: "xrpl:testnet",
      merchantAddress: merchant.address,
      endpoints: {
        "/api/health": { cost: "free", method: "GET" },
        "/api/price/:token": { cost: "0.001 XRP", method: "GET" },
        "/api/analysis": { cost: "0.01 XRP", method: "POST" },
      },
    });
  });

  // --- Paid endpoint: token price (0.001 XRP) ---
  app.get(
    "/api/price/:token",
    x402({
      destination: merchant.address,
      amount: "0.001",
      network: "testnet",
      resourceDescription: "Real-time token price data",
    }),
    (req, res) => {
      const token = (req.params.token as string).toUpperCase();
      // Simulated price data
      const prices: Record<string, number> = {
        XRP: 2.35 + Math.random() * 0.1,
        BTC: 98500 + Math.random() * 1000,
        ETH: 3200 + Math.random() * 100,
        SOL: 180 + Math.random() * 10,
        RLUSD: 1.0,
      };

      const price = prices[token];
      if (!price) {
        res.status(404).json({
          error: {
            code: "TOKEN_NOT_FOUND",
            message: `Token ${token} not found`,
            suggestion: `Available tokens: ${Object.keys(prices).join(", ")}`,
          },
        });
        return;
      }

      res.json({
        token,
        price: price.toFixed(4),
        currency: "USD",
        timestamp: new Date().toISOString(),
        source: "x402-xrpl-demo",
        payment: (req as unknown as Record<string, unknown>).x402Payment,
      });
    }
  );

  // --- Paid endpoint: analysis (0.01 XRP) ---
  app.post(
    "/api/analysis",
    x402({
      destination: merchant.address,
      amount: "0.01",
      network: "testnet",
      resourceDescription: "AI-powered market analysis",
    }),
    (req, res) => {
      const { token = "XRP" } = req.body as { token?: string };
      res.json({
        token: token.toUpperCase(),
        analysis: {
          trend: Math.random() > 0.5 ? "bullish" : "bearish",
          confidence: (0.6 + Math.random() * 0.35).toFixed(2),
          signals: ["volume_increase", "rsi_oversold", "macd_crossover"].slice(
            0,
            Math.ceil(Math.random() * 3)
          ),
          summary: `${token.toUpperCase()} showing ${Math.random() > 0.5 ? "positive" : "mixed"} momentum on short timeframes.`,
        },
        timestamp: new Date().toISOString(),
        payment: (req as unknown as Record<string, unknown>).x402Payment,
      });
    }
  );

  const serverInstance = app.listen(PORT, () => {
    console.log(`\n✅ Demo server running at http://localhost:${PORT}`);
    console.log(`\nEndpoints:`);
    console.log(`  GET  http://localhost:${PORT}/api/health         (free)`);
    console.log(`  GET  http://localhost:${PORT}/api/price/XRP      (0.001 XRP)`);
    console.log(`  POST http://localhost:${PORT}/api/analysis       (0.01 XRP)`);
    console.log(`\nTest with:`);
    console.log(`  curl http://localhost:${PORT}/api/health`);
    console.log(`  curl http://localhost:${PORT}/api/price/XRP`);
    console.log(`\nPress Ctrl+C to stop.`);
  });

  process.on("SIGINT", async () => {
    console.log("\nShutting down...");
    serverInstance.close();
    await disconnectAll();
    process.exit(0);
  });
}

main().catch((err) => {
  console.error("Failed to start demo server:", err);
  process.exit(1);
});
