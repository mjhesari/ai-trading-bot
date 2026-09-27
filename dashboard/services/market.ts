import { getMarket } from "@/services/trading-engine";

export async function fetchMarket(symbol = "EURUSD") {
  return getMarket(symbol, true);
}
