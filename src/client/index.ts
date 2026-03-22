import { type X402ClientConfig, type XrplNetwork, ERROR_CODES } from "../core/types.js";
import { submitPayment } from "../core/payment.js";
import { walletFromSeed } from "../core/wallet.js";

interface X402Response<T = unknown> {
  ok: boolean;
  status: number;
  data: T;
  payment?: {
    txHash: string;
    amount: string;
    destination: string;
    invoiceId: string;
  };
  headers: Record<string, string>;
}

/**
 * x402 HTTP client for AI agents.
 *
 * Automatically detects 402 Payment Required responses, submits XRPL payments,
 * and retries the request with payment proof.
 *
 * Usage:
 * ```ts
 * import { X402Client } from "xrpl-x402/client";
 *
 * const client = new X402Client({ seed: "sEdV..." });
 * const result = await client.get("http://api.example.com/data");
 * // Payment happens automatically — result.data contains the API response
 * ```
 */
export class X402Client {
  private seed: string;
  private network: XrplNetwork;
  private maxAutoPayment: number;
  private autoApprove: boolean;

  constructor(config: X402ClientConfig) {
    this.seed = config.seed;
    this.network = config.network ?? "testnet";
    this.maxAutoPayment = Number(config.maxAutoPayment ?? "1");
    this.autoApprove = config.autoApprove ?? true;
  }

  /** Get the wallet address */
  get address(): string {
    return walletFromSeed(this.seed).address;
  }

  /** Make a GET request, auto-paying 402 challenges */
  async get<T = unknown>(url: string, headers?: Record<string, string>): Promise<X402Response<T>> {
    return this.request<T>(url, { method: "GET", headers });
  }

  /** Make a POST request, auto-paying 402 challenges */
  async post<T = unknown>(
    url: string,
    body?: unknown,
    headers?: Record<string, string>
  ): Promise<X402Response<T>> {
    return this.request<T>(url, {
      method: "POST",
      headers: { "Content-Type": "application/json", ...headers },
      body: body ? JSON.stringify(body) : undefined,
    });
  }

  /** Generic request with auto-payment */
  async request<T = unknown>(url: string, init?: RequestInit): Promise<X402Response<T>> {
    // First attempt
    const response = await fetch(url, init);

    // If not 402, return as-is
    if (response.status !== 402) {
      return this.parseResponse<T>(response);
    }

    // Parse 402 payment request
    const paymentRequest = (await response.json()) as any;
    const payment = paymentRequest.payment;

    if (!payment) {
      return {
        ok: false,
        status: 402,
        data: paymentRequest as T,
        headers: this.extractHeaders(response),
      };
    }

    // Check amount against max
    const amount = Number(payment.amount);
    if (amount > this.maxAutoPayment) {
      return {
        ok: false,
        status: 402,
        data: {
          error: {
            code: ERROR_CODES.AMOUNT_EXCEEDS_MAX,
            message: `Payment of ${payment.amount} XRP exceeds max auto-payment of ${this.maxAutoPayment} XRP`,
            suggestion: `Increase maxAutoPayment in client config, or manually approve this payment.`,
          },
        } as T,
        headers: this.extractHeaders(response),
      };
    }

    if (!this.autoApprove) {
      return {
        ok: false,
        status: 402,
        data: paymentRequest as T,
        headers: this.extractHeaders(response),
      };
    }

    // Submit XRPL payment
    const result = await submitPayment({
      seed: this.seed,
      destination: payment.destination,
      amountXrp: payment.amount,
      invoiceId: payment.invoiceId,
      network: this.network,
    });

    if (result.resultCode !== "tesSUCCESS") {
      return {
        ok: false,
        status: 402,
        data: {
          error: {
            code: ERROR_CODES.PAYMENT_INVALID,
            message: `XRPL payment failed: ${result.resultCode}`,
            suggestion: "Check wallet balance and try again.",
          },
        } as T,
        headers: this.extractHeaders(response),
      };
    }

    // Retry original request with payment proof
    const retryHeaders = new Headers(init?.headers);
    retryHeaders.set("X-Payment-Tx-Hash", result.txHash);
    retryHeaders.set("X-Payment-Invoice-Id", payment.invoiceId);

    const retryResponse = await fetch(url, {
      ...init,
      headers: retryHeaders,
    });

    const parsed = await this.parseResponse<T>(retryResponse);
    parsed.payment = {
      txHash: result.txHash,
      amount: payment.amount,
      destination: payment.destination,
      invoiceId: payment.invoiceId,
    };

    return parsed;
  }

  private async parseResponse<T>(response: Response): Promise<X402Response<T>> {
    const contentType = response.headers.get("content-type") ?? "";
    let data: T;

    if (contentType.includes("application/json")) {
      data = (await response.json()) as T;
    } else {
      data = (await response.text()) as T;
    }

    return {
      ok: response.ok,
      status: response.status,
      data,
      headers: this.extractHeaders(response),
    };
  }

  private extractHeaders(response: Response): Record<string, string> {
    const headers: Record<string, string> = {};
    response.headers.forEach((value, key) => {
      if (key.startsWith("x-payment-")) {
        headers[key] = value;
      }
    });
    return headers;
  }
}
