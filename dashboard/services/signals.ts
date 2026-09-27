import { getSignals } from "@/services/trading-engine";

export async function fetchSignals() {
  return getSignals({ source: "auto" });
}
