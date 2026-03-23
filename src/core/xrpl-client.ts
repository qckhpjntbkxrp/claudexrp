import { Client } from "xrpl";
import { XRPL_NETWORKS, type XrplNetwork } from "./types.js";

const clients = new Map<XrplNetwork, Client>();

/**
 * Get a connected XRPL client for the given network.
 * Reuses existing connections (singleton per network).
 */
export async function getClient(network: XrplNetwork = "testnet"): Promise<Client> {
  const existing = clients.get(network);
  if (existing?.isConnected()) {
    return existing;
  }

  const url = XRPL_NETWORKS[network];
  const client = new Client(url);
  await client.connect();
  clients.set(network, client);
  return client;
}

/**
 * Disconnect all cached clients. Call on shutdown.
 */
export async function disconnectAll(): Promise<void> {
  for (const [network, client] of clients) {
    if (client.isConnected()) {
      await client.disconnect();
    }
    clients.delete(network);
  }
}
