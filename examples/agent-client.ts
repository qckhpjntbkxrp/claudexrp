/**
 * Example: AI agent pays for API calls automatically with XRP.
 *
 * The X402Client detects 402 responses, pays the invoice on XRPL,
 * and retries the request — all in one call.
 */
import { X402Client, createWallet } from "../src/index.js";

async function main() {
  // Step 1: Create a wallet (or use an existing seed)
  console.log("Creating agent wallet on XRPL Testnet...");
  const wallet = await createWallet("testnet");
  console.log(`Agent wallet: ${wallet.address}`);

  // Step 2: Create the x402 client
  const client = new X402Client({
    seed: wallet.seed,
    network: "testnet",
    maxAutoPayment: "0.1", // Max XRP per auto-payment
  });

  // Step 3: Call a paid API — payment happens automatically
  console.log("\nCalling paid API endpoint...");
  const result = await client.get("http://localhost:3000/api/price/XRP");

  console.log(`Status: ${result.status}`);
  console.log(`Data:`, result.data);

  if (result.payment) {
    console.log(`\nPayment made:`);
    console.log(`  TX Hash: ${result.payment.txHash}`);
    console.log(`  Amount:  ${result.payment.amount} XRP`);
    console.log(`  To:      ${result.payment.destination}`);
  }
}

main().catch(console.error);
