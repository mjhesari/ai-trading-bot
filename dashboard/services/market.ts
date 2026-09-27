import { getMarket } from "@/services/trading-engine";

export async function fetchMarket(symbol = "EURUSD") {
  return getMarket(symbol, { source: "auto", count: 500 });
}
