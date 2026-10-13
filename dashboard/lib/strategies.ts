export const STRATEGIES = [
  {
    value: "smc",
    label: "SMC v1",
    description: "BOS / CHoCH + order block + FVG in premium/discount.",
  },
  {
    value: "ict",
    label: "ICT v1",
    description: "Killzone + liquidity sweep + displacement/FVG. SL beyond raid, TP 2R then opposing liquidity.",
  },
] as const;

export type StrategyId = (typeof STRATEGIES)[number]["value"];
