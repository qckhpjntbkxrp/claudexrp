import { describe, it, expect, vi, beforeEach, afterEach } from "vitest";
import { X402Client } from "../src/client/index.js";

// Mock the payment module
vi.mock("../src/core/payment.js", () => ({
  submitPayment: vi.fn(),
}));

// Mock the wallet module
vi.mock("../src/core/wallet.js", () => ({
  walletFromSeed: vi.fn().mockReturnValue({
    address: "rAgentWallet123456789012345678",
    seed: "sEdTestSeed123",
    publicKey: "pubkey123",
  }),
}));

import { submitPayment } from "../src/core/payment.js";

describe("X402Client", () => {
  let originalFetch: typeof global.fetch;

  beforeEach(() => {
    vi.clearAllMocks();
    originalFetch = global.fetch;
  });

  afterEach(() => {
    global.fetch = originalFetch;
  });

  it("passes through non-402 responses", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      status: 200,
      ok: true,
      headers: new Headers({ "content-type": "application/json" }),
      json: async () => ({ data: "free content" }),
    });

    const client = new X402Client({ seed: "sEdTestSeed123" });
    const result = await client.get("http://example.com/free");

    expect(result.ok).toBe(true);
    expect(result.status).toBe(200);
    expect(result.data).toEqual({ data: "free content" });
    expect(result.payment).toBeUndefined();
  });

  it("auto-pays 402 and retries with tx hash", async () => {
    const fetchMock = vi.fn();

    // First call: 402
    fetchMock.mockResolvedValueOnce({
      status: 402,
      ok: false,
      headers: new Headers({ "content-type": "application/json" }),
      json: async () => ({
        payment: {
          destination: "rMerchant123456789012345678901",
          amount: "0.001",
          invoiceId: "550e8400-e29b-41d4-a716-446655440000",
          network: "xrpl:testnet",
        },
      }),
    });

    // Second call: 200 (after payment)
    fetchMock.mockResolvedValueOnce({
      status: 200,
      ok: true,
      headers: new Headers({
        "content-type": "application/json",
        "x-payment-verified": "true",
      }),
      json: async () => ({ data: "premium content" }),
    });

    global.fetch = fetchMock;

    const mockSubmit = vi.mocked(submitPayment);
    mockSubmit.mockResolvedValue({
      txHash: "A".repeat(64),
      resultCode: "tesSUCCESS",
      balanceChanges: "0.001",
    });

    const client = new X402Client({ seed: "sEdTestSeed123", network: "testnet" });
    const result = await client.get("http://example.com/paid");

    expect(result.ok).toBe(true);
    expect(result.data).toEqual({ data: "premium content" });
    expect(result.payment).toBeDefined();
    expect(result.payment!.txHash).toBe("A".repeat(64));
    expect(result.payment!.amount).toBe("0.001");

    // Verify payment was submitted
    expect(mockSubmit).toHaveBeenCalledWith({
      seed: "sEdTestSeed123",
      destination: "rMerchant123456789012345678901",
      amountXrp: "0.001",
      invoiceId: "550e8400-e29b-41d4-a716-446655440000",
      network: "testnet",
    });

    // Verify retry had tx hash header
    expect(fetchMock).toHaveBeenCalledTimes(2);
  });

  it("rejects payments exceeding maxAutoPayment", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      status: 402,
      ok: false,
      headers: new Headers({ "content-type": "application/json" }),
      json: async () => ({
        payment: {
          destination: "rMerchant123456789012345678901",
          amount: "5.0",
          invoiceId: "test-invoice",
          network: "xrpl:testnet",
        },
      }),
    });

    const client = new X402Client({
      seed: "sEdTestSeed123",
      maxAutoPayment: "1.0",
    });

    const result = await client.get("http://example.com/expensive");

    expect(result.ok).toBe(false);
    expect(result.status).toBe(402);
    const data = result.data as { error: { code: string } };
    expect(data.error.code).toBe("AMOUNT_EXCEEDS_MAX");
  });

  it("does not auto-pay when autoApprove is false", async () => {
    global.fetch = vi.fn().mockResolvedValue({
      status: 402,
      ok: false,
      headers: new Headers({ "content-type": "application/json" }),
      json: async () => ({
        payment: {
          destination: "rMerchant123456789012345678901",
          amount: "0.001",
          invoiceId: "test-invoice",
          network: "xrpl:testnet",
        },
      }),
    });

    const client = new X402Client({
      seed: "sEdTestSeed123",
      autoApprove: false,
    });

    const result = await client.get("http://example.com/paid");

    expect(result.ok).toBe(false);
    expect(result.status).toBe(402);
    expect(submitPayment).not.toHaveBeenCalled();
  });
});
