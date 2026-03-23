import { describe, it, expect, vi, beforeEach } from "vitest";
import type { Request, Response, NextFunction } from "express";
import { x402, clearVerificationCache } from "../src/middleware/index.js";

// Mock the verify module
vi.mock("../src/middleware/verify.js", () => ({
  verifyAndCache: vi.fn(),
  clearVerificationCache: vi.fn(),
}));

import { verifyAndCache } from "../src/middleware/verify.js";

function mockReq(overrides: Partial<Request> = {}): Request {
  return {
    method: "GET",
    originalUrl: "/api/test",
    headers: {},
    ...overrides,
  } as Request;
}

function mockRes(): Response & { _status: number; _headers: Record<string, string>; _json: unknown } {
  const res = {
    _status: 200,
    _headers: {} as Record<string, string>,
    _json: null as unknown,
    status(code: number) {
      res._status = code;
      return res;
    },
    setHeader(key: string, value: string) {
      res._headers[key] = value;
      return res;
    },
    json(data: unknown) {
      res._json = data;
      return res;
    },
  };
  return res as unknown as Response & { _status: number; _headers: Record<string, string>; _json: unknown };
}

describe("x402 middleware", () => {
  beforeEach(() => {
    vi.clearAllMocks();
    clearVerificationCache();
  });

  it("returns 402 when no payment header is provided", async () => {
    const middleware = x402({
      destination: "rTestAddr1234567890123456789012",
      amount: "0.001",
      network: "testnet",
    });

    const req = mockReq();
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    expect(res._status).toBe(402);
    expect(res._headers["X-Payment-Amount"]).toBe("0.001");
    expect(res._headers["X-Payment-Destination"]).toBe("rTestAddr1234567890123456789012");
    expect(res._headers["X-Payment-Network"]).toBe("xrpl:testnet");
    expect(res._json).toBeDefined();

    const body = res._json as { type: string; payment: { invoiceId: string } };
    expect(body.type).toBe("x402-payment-required");
    expect(body.payment.invoiceId).toBeDefined();
    expect(next).not.toHaveBeenCalled();
  });

  it("rejects invalid transaction hash format", async () => {
    const middleware = x402({
      destination: "rTestAddr1234567890123456789012",
      amount: "0.001",
    });

    const req = mockReq({
      headers: { "x-payment-tx-hash": "invalid-hash" } as Record<string, string>,
    });
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    expect(res._status).toBe(400);
    const body = res._json as { error: { code: string } };
    expect(body.error.code).toBe("PAYMENT_INVALID");
    expect(next).not.toHaveBeenCalled();
  });

  it("calls next() when payment is verified", async () => {
    const mockVerify = vi.mocked(verifyAndCache);
    mockVerify.mockResolvedValue({
      verified: true,
      txHash: "A".repeat(64),
      amount: "0.001",
      destination: "rTestAddr1234567890123456789012",
      source: "rSourceAddr1234567890123456789",
      ledgerIndex: 12345,
      timestamp: new Date().toISOString(),
    });

    const middleware = x402({
      destination: "rTestAddr1234567890123456789012",
      amount: "0.001",
    });

    const req = mockReq({
      headers: { "x-payment-tx-hash": "A".repeat(64) } as Record<string, string>,
    });
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    expect(next).toHaveBeenCalledOnce();
    expect(res._headers["X-Payment-Verified"]).toBe("true");
  });

  it("returns 402 when payment verification fails", async () => {
    const mockVerify = vi.mocked(verifyAndCache);
    mockVerify.mockResolvedValue({
      verified: false,
      txHash: "B".repeat(64),
      amount: "0.0005",
      destination: "rTestAddr1234567890123456789012",
      source: "rSourceAddr1234567890123456789",
      ledgerIndex: 0,
      timestamp: "",
      error: "Insufficient amount: expected 0.001 XRP, got 0.0005 XRP",
    });

    const middleware = x402({
      destination: "rTestAddr1234567890123456789012",
      amount: "0.001",
    });

    const req = mockReq({
      headers: { "x-payment-tx-hash": "B".repeat(64) } as Record<string, string>,
    });
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    expect(res._status).toBe(402);
    const body = res._json as { error: { code: string } };
    expect(body.error.code).toBe("PAYMENT_INSUFFICIENT");
    expect(next).not.toHaveBeenCalled();
  });

  it("includes payment instructions in 402 response body", async () => {
    const middleware = x402({
      destination: "rTestAddr1234567890123456789012",
      amount: "0.005",
      network: "testnet",
      resourceDescription: "Premium data feed",
    });

    const req = mockReq({ originalUrl: "/api/feed" });
    const res = mockRes();
    const next = vi.fn();

    await middleware(req, res as unknown as Response, next as NextFunction);

    const body = res._json as {
      payment: { amount: string; destination: string; description: string };
      instructions: { step1: string; step2: string; step3: string };
    };

    expect(body.payment.amount).toBe("0.005");
    expect(body.payment.destination).toBe("rTestAddr1234567890123456789012");
    expect(body.payment.description).toBe("Premium data feed");
    expect(body.instructions.step1).toContain("0.005 XRP");
    expect(body.instructions.step3).toContain("X-Payment-Tx-Hash");
  });
});
