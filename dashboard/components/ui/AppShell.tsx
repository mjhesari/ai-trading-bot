"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/dashboard", label: "Overview" },
  { href: "/dashboard/signals", label: "Signals" },
  { href: "/dashboard/backtest", label: "Backtest" },
  { href: "/dashboard/charts", label: "Charts" },
  { href: "/dashboard/settings", label: "Settings" },
];

export function AppShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const isHome = pathname === "/";

  if (isHome) {
    return <div className="app-shell is-home">{children}</div>;
  }

  return (
    <div className="app-shell">
      <aside className="sidebar">
        <div className="brand-block">
          <Link href="/" className="brand-mark">
            <span className="brand-orb" aria-hidden />
            <span className="brand-name">Aether SMC</span>
          </Link>
          <p className="brand-sub">Smart money desk</p>
        </div>

        <nav className="side-nav" aria-label="Primary">
          {links.map((l) => {
            const active = pathname === l.href;
            return (
              <Link key={l.href} href={l.href} className={`side-link${active ? " active" : ""}`}>
                <span className="dot" aria-hidden />
                {l.label}
              </Link>
            );
          })}
        </nav>

        <div className="side-foot">
          <strong>TWELVE · SMC</strong>
          <p>Deep-blue desk · full timeframes · real market APIs.</p>
        </div>
      </aside>

      <div className="main-col">
        <nav className="mobile-nav" aria-label="Mobile">
          <Link href="/">Home</Link>
          {links.map((l) => (
            <Link key={l.href} href={l.href} className={pathname === l.href ? "active" : undefined}>
              {l.label}
            </Link>
          ))}
        </nav>

        <header className="topbar">
          <div className="status-pill">
            <span className="live" aria-hidden />
            live feed · real APIs
          </div>
          <div className="status-pill">1m–1w · deep blue</div>
        </header>

        {children}
      </div>
    </div>
  );
}
