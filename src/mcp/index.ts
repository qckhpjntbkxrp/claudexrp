#!/usr/bin/env node
import { McpServer } from "@modelcontextprotocol/sdk/server/mcp.js";
import { StdioServerTransport } from "@modelcontextprotocol/sdk/server/stdio.js";
import { z } from "zod";
import { createWallet, getBalance, getTransactions, walletFromSeed } from "../core/wallet.js";
import { submitPayment, verifyPayment } from "../core/payment.js";
import { disconnectAll } from "../core/xrpl-client.js";
import type { XrplNetwork } from "../core/types.js";

const server = new McpServer({
  name: "xrpl-x402",
  version: "0.1.0",
});

// --- Tool: create_wallet ---
server.tool(
  "create_wallet",
  "Create a new XRPL wallet. On testnet/devnet, the wallet is automatically funded from the faucet with test XRP. Returns the wallet address, seed (secret key), and public key.",
  {
    network: z
      .enum(["mainnet", "testnet", "devnet"])
      .default("testnet")
      .describe("XRPL network to create the wallet on. Use testnet for development."),
  },
  async ({ network }) => {
    try {
      const wallet = await createWallet(network as XrplNetwork);
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(
              {
                success: true,
                wallet: {
                  address: wallet.address,
                  seed: wallet.seed,
                  publicKey: wallet.publicKey,
                  network,
                  funded: network !== "mainnet",
                },
                warning:
                  network === "mainnet"
                    ? "This is a MAINNET wallet. Fund it with real XRP before use."
                    : "This wallet has been funded with test XRP from the faucet.",
              },
              null,
              2
            ),
          },
        ],
      };
    } catch (err) {
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              success: false,
              error: {
                code: "WALLET_CREATION_FAILED",
                message: err instanceof Error ? err.message : String(err),
                suggestion: "Check network connectivity. For testnet, the faucet may be temporarily unavailable — retry in 30 seconds.",
              },
            }),
          },
        ],
        isError: true,
      };
    }
  }
);

// --- Tool: get_balance ---
server.tool(
  "get_balance",
  "Get the XRP balance of an XRPL wallet address.",
  {
    address: z.string().describe("The XRPL wallet address (starts with 'r')"),
    network: z
      .enum(["mainnet", "testnet", "devnet"])
      .default("testnet")
      .describe("XRPL network to query"),
  },
  async ({ address, network }) => {
    try {
      const balance = await getBalance(address, network as XrplNetwork);
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({ success: true, ...balance }, null, 2),
          },
        ],
      };
    } catch (err) {
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              success: false,
              error: {
                code: "BALANCE_QUERY_FAILED",
                message: err instanceof Error ? err.message : String(err),
                suggestion: "Verify the address is valid and the account exists on the specified network.",
              },
            }),
          },
        ],
        isError: true,
      };
    }
  }
);

// --- Tool: pay_invoice ---
server.tool(
  "pay_invoice",
  "Pay an x402 invoice by submitting an XRP payment to the specified destination. Use this to respond to HTTP 402 Payment Required challenges. The payment is submitted on-ledger and the transaction hash is returned for use in the X-Payment-Tx-Hash header.",
  {
    seed: z.string().describe("Your XRPL wallet seed (secret key). Starts with 's'."),
    destination: z
      .string()
      .describe("The destination XRPL address to pay (from the 402 response)"),
    amount: z.string().describe("Amount in XRP to pay (from the 402 response)"),
    invoiceId: z.string().describe("The invoice ID from the 402 response (UUID format)"),
    network: z
      .enum(["mainnet", "testnet", "devnet"])
      .default("testnet")
      .describe("XRPL network"),
  },
  async ({ seed, destination, amount, invoiceId, network }) => {
    try {
      const wallet = walletFromSeed(seed);
      const result = await submitPayment({
        seed,
        destination,
        amountXrp: amount,
        invoiceId,
        network: network as XrplNetwork,
      });

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(
              {
                success: result.resultCode === "tesSUCCESS",
                payment: {
                  txHash: result.txHash,
                  resultCode: result.resultCode,
                  from: wallet.address,
                  to: destination,
                  amount: `${amount} XRP`,
                  invoiceId,
                  network,
                },
                nextStep:
                  result.resultCode === "tesSUCCESS"
                    ? `Retry your original HTTP request with header: X-Payment-Tx-Hash: ${result.txHash}`
                    : "Payment failed. Check your wallet balance and try again.",
              },
              null,
              2
            ),
          },
        ],
      };
    } catch (err) {
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              success: false,
              error: {
                code: "PAYMENT_FAILED",
                message: err instanceof Error ? err.message : String(err),
                suggestion: "Ensure your wallet has sufficient XRP balance and the seed is correct.",
              },
            }),
          },
        ],
        isError: true,
      };
    }
  }
);

// --- Tool: check_payment ---
server.tool(
  "check_payment",
  "Verify that a payment transaction was successfully validated on the XRP Ledger. Use this to confirm a payment settled before relying on it.",
  {
    txHash: z.string().describe("The XRPL transaction hash to verify (64 hex characters)"),
    expectedDestination: z.string().describe("The expected payment destination address"),
    expectedAmount: z.string().describe("The expected payment amount in XRP"),
    network: z
      .enum(["mainnet", "testnet", "devnet"])
      .default("testnet")
      .describe("XRPL network"),
  },
  async ({ txHash, expectedDestination, expectedAmount, network }) => {
    try {
      const result = await verifyPayment({
        txHash,
        expectedDestination,
        expectedAmountXrp: expectedAmount,
        network: network as XrplNetwork,
      });

      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({ success: true, verification: result }, null, 2),
          },
        ],
      };
    } catch (err) {
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              success: false,
              error: {
                code: "VERIFICATION_FAILED",
                message: err instanceof Error ? err.message : String(err),
                suggestion: "Wait a few seconds for the transaction to be validated, then retry.",
              },
            }),
          },
        ],
        isError: true,
      };
    }
  }
);

// --- Tool: list_transactions ---
server.tool(
  "list_transactions",
  "List recent transactions for an XRPL wallet address.",
  {
    address: z.string().describe("The XRPL wallet address"),
    network: z
      .enum(["mainnet", "testnet", "devnet"])
      .default("testnet")
      .describe("XRPL network"),
    limit: z.number().min(1).max(100).default(10).describe("Number of transactions to return"),
  },
  async ({ address, network, limit }) => {
    try {
      const txs = await getTransactions(address, network as XrplNetwork, limit);
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify(
              { success: true, address, network, count: txs.length, transactions: txs },
              null,
              2
            ),
          },
        ],
      };
    } catch (err) {
      return {
        content: [
          {
            type: "text" as const,
            text: JSON.stringify({
              success: false,
              error: {
                code: "TX_LIST_FAILED",
                message: err instanceof Error ? err.message : String(err),
                suggestion: "Verify the address exists on the specified network.",
              },
            }),
          },
        ],
        isError: true,
      };
    }
  }
);

// --- Tool: estimate_cost ---
server.tool(
  "estimate_cost",
  "Estimate the total cost of an x402 payment including XRPL transaction fees. Use this before paying to know the exact cost.",
  {
    amount: z.string().describe("The payment amount in XRP"),
  },
  async ({ amount }) => {
    // XRPL standard fee is 12 drops (0.000012 XRP)
    const fee = 0.000012;
    const total = Number(amount) + fee;

    return {
      content: [
        {
          type: "text" as const,
          text: JSON.stringify(
            {
              success: true,
              estimate: {
                paymentAmount: `${amount} XRP`,
                networkFee: `${fee} XRP`,
                totalCost: `${total} XRP`,
                totalCostUsd: "Varies — check current XRP/USD rate",
              },
            },
            null,
            2
          ),
        },
      ],
    };
  }
);

// --- Start server ---
async function main() {
  const transport = new StdioServerTransport();
  await server.connect(transport);

  // Cleanup on exit
  process.on("SIGINT", async () => {
    await disconnectAll();
    process.exit(0);
  });
}

main().catch((err) => {
  console.error("MCP server failed to start:", err);
  process.exit(1);
});
