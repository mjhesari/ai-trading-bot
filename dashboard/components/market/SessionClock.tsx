"use client";

import { Badge } from "@/components/ui/badge";
import { useSessions } from "@/hooks/use-sessions";
import type { SessionSnapshot, SessionWindow } from "@/types/session";

function SessionChip({ session }: { session: SessionWindow }) {
  return (
    <div className={`session-chip${session.active ? " active" : ""}`}>
      <span className="session-chip-name">{session.label}</span>
      <span className="session-chip-hours">
        {session.localStart}–{session.localEnd}
      </span>
    </div>
  );
}

function ClockBody({ snap }: { snap: SessionSnapshot }) {
  const activeLabel =
    snap.active.length > 0
      ? snap.sessions
          .filter((s) => s.active)
          .map((s) => s.label)
          .join(" · ")
      : "closed";

  return (
    <>
      <div className="session-clock-meta">
        <div>
          <div className="label">Sessions</div>
          <p className="session-clock-now">
            {snap.nowLocal} {snap.timezoneLabel}{" "}
            <span className="muted">UTC{snap.offset}</span>
          </p>
        </div>
        <div className="session-clock-badges">
          <Badge variant={snap.active.length ? "success" : "secondary"}>{activeLabel}</Badge>
          {snap.overlap ? <Badge variant="default">overlap</Badge> : null}
          {snap.killzone ? <Badge variant="default">killzone</Badge> : null}
        </div>
      </div>
      <div className="session-chip-row">
        {snap.sessions.map((s) => (
          <SessionChip key={s.id} session={s} />
        ))}
      </div>
    </>
  );
}

export function SessionClock({ compact = false }: { compact?: boolean }) {
  const { sessions, error } = useSessions();

  if (error && !sessions) {
    return (
      <div className={`panel session-clock${compact ? " compact" : ""}`}>
        <p className="error">{error}</p>
      </div>
    );
  }

  if (!sessions) {
    return (
      <div className={`panel session-clock${compact ? " compact" : ""}`}>
        <p className="muted">Loading sessions…</p>
      </div>
    );
  }

  return (
    <div className={`panel session-clock${compact ? " compact" : ""}`}>
      <ClockBody snap={sessions} />
    </div>
  );
}
