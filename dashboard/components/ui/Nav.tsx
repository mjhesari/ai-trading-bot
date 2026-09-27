import Link from "next/link";

const links = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/signals", label: "Signals" },
  { href: "/dashboard/backtest", label: "Backtest" },
  { href: "/dashboard/charts", label: "Charts" },
  { href: "/dashboard/settings", label: "Settings" },
];

export function Nav() {
  return (
    <nav className="nav">
      <Link href="/" className="brand">
        AI Trading Bot
      </Link>
      <div className="nav-links">
        {links.map((l) => (
          <Link key={l.href} href={l.href}>
            {l.label}
          </Link>
        ))}
      </div>
    </nav>
  );
}
