import { getSignals } from "@/services/trading-engine";
import type { SignalsResponse } from "@/types/signal";

export async function fetchSignals(): Promise<SignalsResponse> {
  return getSignals({ useSample: true });
}
