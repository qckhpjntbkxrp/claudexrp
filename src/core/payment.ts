import { Wallet as XrplWallet, xrpToDrops, dropsToXrp } from "xrpl";
import type { Payment } from "xrpl";
import { getClient } from "./xrpl-client.js";
import type { XrplNetwork, VerificationResult } from "./types.js";

/* eslint-disable @typescript-eslint/no-explicit-any */

/**
 * Submit a payment on the XRP Ledger.
 */
export async function submitPayment(opts: {
  seed: string;
  destination: string;
  amountXrp: string;
  invoiceId: string;
  network?: XrplNetwork;
}): Promise<{ txHash: string; resultCode: string; balanceChanges: string }> {
  const network = opts.network ?? "testnet";
  const client = await getClient(network);
  const wallet = XrplWallet.fromSeed(opts.seed);

  // Convert invoiceId (UUID) to 256-bit hex for XRPL InvoiceID field
  const invoiceIdHex = opts.invoiceId.replace(/-/g, "").padEnd(64, "0").toUpperCase();

  const payment: Payment = {
    TransactionType: "Payment",
    Account: wallet.address,
    Destination: opts.destination,
    Amount: xrpToDrops(opts.amountXrp),
    InvoiceID: invoiceIdHex,
    Memos: [
      {
        Memo: {
          MemoType: Buffer.from("x402/payment", "utf8").toString("hex").toUpperCase(),
          MemoData: Buffer.from(opts.invoiceId, "utf8").toString("hex").toUpperCase(),
        },
      },
    ],
  };

  const result = await client.submitAndWait(payment, { wallet });
  const meta = result.result.meta as any;
  const resultCode: string = meta?.TransactionResult ?? "unknown";

  return {
    txHash: result.result.hash,
    resultCode,
    balanceChanges: opts.amountXrp,
  };
}

/**
 * Verify a payment transaction on the XRP Ledger.
 * Checks: tx exists, validated, successful, correct amount, correct destination, invoice ID matches.
 */
export async function verifyPayment(opts: {
  txHash: string;
  expectedDestination: string;
  expectedAmountXrp: string;
  expectedInvoiceId?: string;
  network?: XrplNetwork;
}): Promise<VerificationResult> {
  const network = opts.network ?? "testnet";
  const client = await getClient(network);

  try {
    const response = await client.request({
      command: "tx",
      transaction: opts.txHash,
    });

    const tx = response.result as any;

    // Check if validated
    if (!tx.validated) {
      return {
        verified: false,
        txHash: opts.txHash,
        amount: "0",
        destination: "",
        source: "",
        ledgerIndex: 0,
        timestamp: "",
        error: "Transaction not yet validated",
      };
    }

    // Check result code
    const resultCode: string = tx.meta?.TransactionResult ?? "unknown";

    if (resultCode !== "tesSUCCESS") {
      return {
        verified: false,
        txHash: opts.txHash,
        amount: "0",
        destination: "",
        source: "",
        ledgerIndex: 0,
        timestamp: "",
        error: `Transaction failed with code: ${resultCode}`,
      };
    }

    // Extract payment details
    const rawAmount = tx.Amount;
    const amountDrops = typeof rawAmount === "string" ? rawAmount : "0";
    const amountXrp = String(dropsToXrp(amountDrops));
    const destination = (tx.Destination as string) ?? "";
    const source = (tx.Account as string) ?? "";
    const invoiceId = (tx.InvoiceID as string) ?? "";
    const ledgerIndex: number = tx.ledger_index ?? 0;

    // Verify destination
    if (destination !== opts.expectedDestination) {
      return {
        verified: false,
        txHash: opts.txHash,
        amount: amountXrp,
        destination,
        source,
        ledgerIndex,
        timestamp: "",
        error: `Wrong destination: expected ${opts.expectedDestination}, got ${destination}`,
      };
    }

    // Verify amount (must be >= expected)
    if (Number(amountXrp) < Number(opts.expectedAmountXrp)) {
      return {
        verified: false,
        txHash: opts.txHash,
        amount: amountXrp,
        destination,
        source,
        ledgerIndex,
        timestamp: "",
        error: `Insufficient amount: expected ${opts.expectedAmountXrp} XRP, got ${amountXrp} XRP`,
      };
    }

    // Verify invoice ID if expected
    if (opts.expectedInvoiceId) {
      const expectedHex = opts.expectedInvoiceId.replace(/-/g, "").padEnd(64, "0").toUpperCase();
      if (invoiceId !== expectedHex) {
        return {
          verified: false,
          txHash: opts.txHash,
          amount: amountXrp,
          destination,
          source,
          ledgerIndex,
          timestamp: "",
          invoiceId,
          error: `Invoice ID mismatch: expected ${expectedHex}, got ${invoiceId}`,
        };
      }
    }

    return {
      verified: true,
      txHash: opts.txHash,
      amount: amountXrp,
      destination,
      source,
      ledgerIndex,
      timestamp: new Date().toISOString(),
      invoiceId,
    };
  } catch (err) {
    return {
      verified: false,
      txHash: opts.txHash,
      amount: "0",
      destination: "",
      source: "",
      ledgerIndex: 0,
      timestamp: "",
      error: `Verification failed: ${err instanceof Error ? err.message : String(err)}`,
    };
  }
}
