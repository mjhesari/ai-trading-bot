export default function SettingsPage() {
  return (
    <main className="page">
      <h1>Settings</h1>
      <p className="muted">
        Configure engine URL via <code>NEXT_PUBLIC_ENGINE_URL</code>. MT5 credentials live in
        trading-engine env only.
      </p>
    </main>
  );
}
