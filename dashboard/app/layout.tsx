import type { Metadata } from "next";
import "./globals.css";
import { Nav } from "@/components/ui/Nav";

export const metadata: Metadata = {
  title: "AI Trading Bot",
  description: "SMC + Price Action dashboard",
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body>
        <Nav />
        {children}
      </body>
    </html>
  );
}
