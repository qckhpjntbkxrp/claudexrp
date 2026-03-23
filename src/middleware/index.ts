import type { Request, Response, NextFunction } from "express";
import { v4 as uuidv4 } from "uuid";
import { type X402Config, type XrplNetwork, makeError, ERROR_CODES } from "../core/types.js";
import { verifyAndCache } from "./verify.js";

// Track issued invoices (invoiceId → metadata)
const pendingInvoices = new Map<
  string,
  { destination: string; amount: string; network: XrplNetwork; expiry: Date; resource: string }
>();

/**
 * x402 Express middleware factory.
 *
 * Usage:
 * ```ts
 * import { x402 } from "xrpl-x402/middleware";
 *
 * app.get("/api/data", x402({
 *   destination: "rYourXrplAddress...",
 *   amount: "0.001",
 * }), (req, res) => {
 *   res.json({ data: "premium content" });
 * });
 * ```
 */
export function x402(config: X402Config) {
  const network: XrplNetwork = config.network ?? "testnet";
  const expirySeconds = config.expirySeconds ?? 300;
  const cacheVerified = config.cacheVerified ?? true;

  return async (req: Request, res: Response, next: NextFunction): Promise<void> => {
    const txHash = req.headers["x-payment-tx-hash"] as string | undefined;

    // --- No payment provided: return 402 ---
    if (!txHash) {
      const invoiceId = uuidv4();
      const expiry = new Date(Date.now() + expirySeconds * 1000);
      const resource = `${req.method} ${req.originalUrl}`;

      pendingInvoices.set(invoiceId, {
        destination: config.destination,
        amount: config.amount,
        network,
        expiry,
        resource,
      });

      // Auto-cleanup expired invoices
      setTimeout(() => pendingInvoices.delete(invoiceId), expirySeconds * 1000);

      res.status(402);
      res.setHeader("X-Payment-Amount", config.amount);
      res.setHeader("X-Payment-Destination", config.destination);
      res.setHeader("X-Payment-Network", `xrpl:${network}`);
      res.setHeader("X-Payment-Invoice-Id", invoiceId);
      res.setHeader("X-Payment-Expiry", expiry.toISOString());
      res.setHeader("Content-Type", "application/json");

      res.json({
        status: 402,
        type: "x402-payment-required",
        payment: {
          network: `xrpl:${network}`,
          destination: config.destination,
          amount: config.amount,
          currency: "XRP",
          invoiceId,
          expiry: expiry.toISOString(),
          resource,
          description: config.resourceDescription ?? `Payment required for ${resource}`,
        },
        instructions: {
          step1: `Submit an XRPL payment of ${config.amount} XRP to ${config.destination} on ${network}`,
          step2: `Include InvoiceID: ${invoiceId} (as hex, zero-padded to 64 chars) in the transaction`,
          step3: `Retry this request with header: X-Payment-Tx-Hash: <your_tx_hash>`,
        },
      });
      return;
    }

    // --- Payment provided: verify it ---
    if (!/^[A-Fa-f0-9]{64}$/.test(txHash)) {
      res.status(400).json(
        makeError(
          ERROR_CODES.PAYMENT_INVALID,
          "Invalid transaction hash format. Must be 64 hex characters.",
          "Ensure X-Payment-Tx-Hash is a valid XRPL transaction hash (64 hex chars)."
        )
      );
      return;
    }

    // Extract invoice ID from request header (optional — for stricter verification)
    const invoiceId = req.headers["x-payment-invoice-id"] as string | undefined;

    try {
      const result = await verifyAndCache({
        txHash,
        expectedDestination: config.destination,
        expectedAmountXrp: config.amount,
        expectedInvoiceId: invoiceId,
        network,
        useCache: cacheVerified,
      });

      if (!result.verified) {
        const errorCode = result.error?.includes("not yet validated")
          ? ERROR_CODES.PAYMENT_NOT_VALIDATED
          : result.error?.includes("Insufficient")
            ? ERROR_CODES.PAYMENT_INSUFFICIENT
            : result.error?.includes("destination")
              ? ERROR_CODES.PAYMENT_WRONG_DESTINATION
              : ERROR_CODES.PAYMENT_INVALID;

        res.status(402).json(
          makeError(
            errorCode,
            result.error ?? "Payment verification failed",
            errorCode === ERROR_CODES.PAYMENT_NOT_VALIDATED
              ? "Wait a few seconds for the transaction to be validated on the XRP Ledger, then retry."
              : "Check that you sent the correct amount to the correct destination on the correct network."
          )
        );
        return;
      }

      // Payment verified — attach payment info to request and continue
      (req as unknown as Record<string, unknown>).x402Payment = result;

      // Set response headers with payment receipt
      res.setHeader("X-Payment-Verified", "true");
      res.setHeader("X-Payment-Tx-Hash", txHash);
      res.setHeader("X-Payment-Amount", result.amount);
      res.setHeader("X-Payment-Source", result.source);

      next();
    } catch (err) {
      res.status(500).json(
        makeError(
          ERROR_CODES.VERIFICATION_FAILED,
          `Payment verification error: ${err instanceof Error ? err.message : String(err)}`,
          "Retry the request. If the error persists, the XRPL network may be temporarily unavailable."
        )
      );
    }
  };
}

export { clearVerificationCache } from "./verify.js";
