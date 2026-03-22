import { verifyPayment } from "../core/payment.js";
import type { XrplNetwork, VerificationResult } from "../core/types.js";

// In-memory cache of verified tx hashes → verification results
const verifiedCache = new Map<string, VerificationResult>();

/**
 * Verify a payment and cache the result.
 * Cached payments skip the ledger lookup on subsequent requests (idempotent).
 */
export async function verifyAndCache(opts: {
  txHash: string;
  expectedDestination: string;
  expectedAmountXrp: string;
  expectedInvoiceId?: string;
  network?: XrplNetwork;
  useCache?: boolean;
}): Promise<VerificationResult> {
  // Check cache first
  if (opts.useCache !== false) {
    const cached = verifiedCache.get(opts.txHash);
    if (cached) {
      return cached;
    }
  }

  const result = await verifyPayment({
    txHash: opts.txHash,
    expectedDestination: opts.expectedDestination,
    expectedAmountXrp: opts.expectedAmountXrp,
    expectedInvoiceId: opts.expectedInvoiceId,
    network: opts.network,
  });

  // Only cache verified payments
  if (result.verified) {
    verifiedCache.set(opts.txHash, result);
  }

  return result;
}

/**
 * Clear the verification cache (for testing).
 */
export function clearVerificationCache(): void {
  verifiedCache.clear();
}
