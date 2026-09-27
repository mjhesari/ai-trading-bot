import Link from "next/link";
import { Button } from "@/components/ui/button";

export default function HomePage() {
  return (
    <main className="hero-home">
      <div className="hero-inner">
        <p className="brand-sub" style={{ marginBottom: "1rem" }}>
          Real-market SMC desk · Mac / Vercel / VPS
        </p>
        <h1 className="hero-brand">Aether SMC</h1>
        <p className="hero-line">
          Smart Money Concepts on live market OHLC — charts, buy/sell signals, and backtests across
          every timeframe.
        </p>
        <div className="hero-actions">
          <Button asChild size="lg">
            <Link href="/dashboard">Open desk</Link>
          </Button>
          <Button asChild variant="outline" size="lg">
            <Link href="/dashboard/charts">View charts</Link>
          </Button>
        </div>
      </div>
    </main>
  );
}
