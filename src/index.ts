// xrpl-x402 — x402 Payment Gateway for XRPL
// AI agents pay for APIs with XRP micropayments

export { x402 } from "./middleware/index.js";
export { X402Client } from "./client/index.js";
export { createWallet, getBalance, walletFromSeed, getTransactions } from "./core/wallet.js";
export { submitPayment, verifyPayment } from "./core/payment.js";
export { getClient, disconnectAll } from "./core/xrpl-client.js";
export {
  type X402Config,
  type X402ClientConfig,
  type PaymentRequest,
  type PaymentProof,
  type VerificationResult,
  type X402Error,
  type XrplNetwork,
  XRPL_NETWORKS,
  ERROR_CODES,
  makeError,
} from "./core/types.js";
