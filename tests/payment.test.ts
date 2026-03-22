import { describe, it, expect } from "vitest";
import { makeError, ERROR_CODES, XRPL_NETWORKS } from "../src/core/types.js";

describe("types", () => {
  it("makeError creates structured error", () => {
    const err = makeError("TEST_CODE", "Something went wrong", "Try again later");
    expect(err.error.code).toBe("TEST_CODE");
    expect(err.error.message).toBe("Something went wrong");
    expect(err.error.suggestion).toBe("Try again later");
  });

  it("ERROR_CODES contains all expected codes", () => {
    expect(ERROR_CODES.PAYMENT_REQUIRED).toBe("PAYMENT_REQUIRED");
    expect(ERROR_CODES.PAYMENT_INVALID).toBe("PAYMENT_INVALID");
    expect(ERROR_CODES.PAYMENT_EXPIRED).toBe("PAYMENT_EXPIRED");
    expect(ERROR_CODES.PAYMENT_INSUFFICIENT).toBe("PAYMENT_INSUFFICIENT");
    expect(ERROR_CODES.PAYMENT_WRONG_DESTINATION).toBe("PAYMENT_WRONG_DESTINATION");
    expect(ERROR_CODES.AMOUNT_EXCEEDS_MAX).toBe("AMOUNT_EXCEEDS_MAX");
  });

  it("XRPL_NETWORKS has correct URLs", () => {
    expect(XRPL_NETWORKS.testnet).toContain("rippletest.net");
    expect(XRPL_NETWORKS.mainnet).toContain("xrplcluster.com");
    expect(XRPL_NETWORKS.devnet).toContain("devnet");
  });
});
