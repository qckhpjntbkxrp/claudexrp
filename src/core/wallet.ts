import { Wallet as XrplWallet } from "xrpl";
import { getClient } from "./xrpl-client.js";
import type { XrplNetwork } from "./types.js";

export interface WalletInfo {
  address: string;
  seed: string;
  publicKey: string;
}

export interface BalanceInfo {
  address: string;
  balanceXrp: string;
  network: XrplNetwork;
}

/**
 * Create a new XRPL wallet. On testnet/devnet, automatically funds it from the faucet.
 */
export async function createWallet(
  network: XrplNetwork = "testnet"
): Promise<WalletInfo> {
  const client = await getClient(network);

  if (network === "mainnet") {
    const wallet = XrplWallet.generate();
    return {
      address: wallet.address,
      seed: wallet.seed!,
      publicKey: wallet.publicKey,
    };
  }

  // Testnet/devnet: fund from faucet
  const { wallet } = await client.fundWallet();
  return {
    address: wallet.address,
    seed: wallet.seed!,
    publicKey: wallet.publicKey,
  };
}

/**
 * Restore a wallet from a seed.
 */
export function walletFromSeed(seed: string): XrplWallet {
  return XrplWallet.fromSeed(seed);
}

/**
 * Get XRP balance for an address.
 */
export async function getBalance(
  address: string,
  network: XrplNetwork = "testnet"
): Promise<BalanceInfo> {
  const client = await getClient(network);
  const response = await client.request({
    command: "account_info",
    account: address,
    ledger_index: "validated",
  });

  const balanceDrops = response.result.account_data.Balance;
  const balanceXrp = (Number(balanceDrops) / 1_000_000).toString();

  return {
    address,
    balanceXrp,
    network,
  };
}

/**
 * Get recent transactions for an address.
 */
export async function getTransactions(
  address: string,
  network: XrplNetwork = "testnet",
  limit: number = 10
): Promise<unknown[]> {
  const client = await getClient(network);
  const response = await client.request({
    command: "account_tx",
    account: address,
    limit,
    ledger_index_min: -1,
    ledger_index_max: -1,
  });

  return response.result.transactions;
}
