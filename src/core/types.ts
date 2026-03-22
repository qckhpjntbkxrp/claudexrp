import { z } from "zod";

// --- Networks ---

export const XRPL_NETWORKS = {
  mainnet: "wss://xrplcluster.com",
  testnet: "wss://s.altnet.rippletest.net:51233",
  devnet: "wss://s.devnet.rippletest.net:51233",
} as const;

export type XrplNetwork = keyof typeof XRPL_NETWORKS;

// --- Payment Request (returned in 402 response) ---

export const PaymentRequestSchema = z.object({
  network: z.enum(["mainnet", "testnet", "devnet"]),
  destination: z.string().min(25).max(35),
  amount: z.string().regex(/^\d+(\.\d{1,6})?$/, "Amount in XRP (up to 6 decimal places)"),
  invoiceId: z.string().uuid(),
  memo: z.string().optional(),
  expiry: z.string().datetime(),
  resource: z.string(),
});

export type PaymentRequest = z.infer<typeof PaymentRequestSchema>;

// --- Payment Proof (sent by agent in retry request) ---

export const PaymentProofSchema = z.object({
  txHash: z.string().length(64),
  network: z.enum(["mainnet", "testnet", "devnet"]),
});

export type PaymentProof = z.infer<typeof PaymentProofSchema>;

// --- Verification Result ---

export interface VerificationResult {
  verified: boolean;
  txHash: string;
  amount: string;
  destination: string;
  source: string;
  ledgerIndex: number;
  timestamp: string;
  invoiceId?: string;
  error?: string;
}

// --- x402 Middleware Config ---

export interface X402Config {
  /** XRPL destination address to receive payments */
  destination: string;
  /** Amount in XRP to charge per request */
  amount: string;
  /** XRPL network (default: testnet) */
  network?: XrplNetwork;
  /** Seconds until payment request expires (default: 300) */
  expirySeconds?: number;
  /** Custom description of what the agent is paying for */
  resourceDescription?: string;
  /** Cache verified payments to avoid re-checking (default: true) */
  cacheVerified?: boolean;
  /** XRPL wallet seed for fee collection — optional, only if you want to charge a fee */
  feeSeed?: string;
  /** Fee percentage (default: 0, range 0-5) */
  feePercent?: number;
}

// --- Client Config ---

export interface X402ClientConfig {
  /** XRPL wallet seed (secret) */
  seed: string;
  /** XRPL network (default: testnet) */
  network?: XrplNetwork;
  /** Maximum XRP the client will auto-pay per request (default: 1) */
  maxAutoPayment?: string;
  /** Whether to auto-approve payments without prompting (default: true) */
  autoApprove?: boolean;
}

// --- Error Response ---

export interface X402Error {
  error: {
    code: string;
    message: string;
    suggestion: string;
  };
}

// --- Standard error codes ---

export const ERROR_CODES = {
  PAYMENT_REQUIRED: "PAYMENT_REQUIRED",
  PAYMENT_INVALID: "PAYMENT_INVALID",
  PAYMENT_EXPIRED: "PAYMENT_EXPIRED",
  PAYMENT_INSUFFICIENT: "PAYMENT_INSUFFICIENT",
  PAYMENT_WRONG_DESTINATION: "PAYMENT_WRONG_DESTINATION",
  PAYMENT_NOT_FOUND: "PAYMENT_NOT_FOUND",
  PAYMENT_NOT_VALIDATED: "PAYMENT_NOT_VALIDATED",
  VERIFICATION_FAILED: "VERIFICATION_FAILED",
  WALLET_INSUFFICIENT_FUNDS: "WALLET_INSUFFICIENT_FUNDS",
  NETWORK_ERROR: "NETWORK_ERROR",
  AMOUNT_EXCEEDS_MAX: "AMOUNT_EXCEEDS_MAX",
} as const;

export function makeError(code: string, message: string, suggestion: string): X402Error {
  return { error: { code, message, suggestion } };
}
