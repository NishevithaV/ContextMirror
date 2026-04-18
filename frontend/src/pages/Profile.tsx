import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { fetchInsights } from "../api";
import { useAuth } from "../auth/AuthContext";
import type { InsightResponse, DataSource } from "../types";
import { sourceColors } from "../lib/insight-style";

const sources: {
  key: DataSource;
  name: string;
  description: string;
  connected: boolean;
}[] = [
  {
    key: "calendar",
    name: "Google Calendar",
    description: "Meetings, events, busy windows",
    connected: true,
  },
  {
    key: "messaging",
    name: "WhatsApp",
    description: "Message volume and cadence",
    connected: true,
  },
  {
    key: "health",
    name: "Health data",
    description: "Sleep, steps, heart rate",
    connected: false,
  },
];

export function Profile() {
  const { user, signOut } = useAuth();
  const nav = useNavigate();
  const [weeks, setWeeks] = useState<InsightResponse[]>([]);
  useEffect(() => {
    fetchInsights().then((r) => setWeeks(r.data));
  }, []);

  const initial = user?.name.charAt(0).toUpperCase() ?? "?";

  return (
    <div className="flex flex-col gap-10">
      <header className="flex items-center gap-5">
        <div className="w-14 h-14 rounded-full bg-elevated flex items-center justify-center text-xl font-medium border border-white/5">
          {initial}
        </div>
        <div className="flex-1">
          <h1 className="text-2xl font-semibold tracking-tight text-white">
            {user?.name ?? "Guest"}
          </h1>
          <p className="text-text-muted text-sm mt-0.5">
            {user?.email ?? "Manage your details and connected data sources."}
          </p>
        </div>
        <button
          onClick={() => {
            signOut();
            nav("/signin");
          }}
          className="text-xs text-danger border border-elevated rounded-md px-3 py-1.5 hover:bg-elevated transition-colors"
        >
          Sign out
        </button>
      </header>

      <section>
        <div className="mb-5">
          <h2 className="text-base font-medium text-white">
            Connected sources
          </h2>
          <p className="text-text-muted text-sm mt-1">
            {sources.filter((s) => s.connected).length} of {sources.length} linked.
          </p>
        </div>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
          {sources.map((s) => (
            <div
              key={s.key}
              className="rounded-2xl border border-elevated bg-card/40 p-5"
            >
              <div className="flex items-center justify-between mb-4">
                <div
                  className="w-9 h-9 rounded-md flex items-center justify-center text-sm font-medium"
                  style={{
                    backgroundColor: `${sourceColors[s.key]}22`,
                    color: sourceColors[s.key],
                  }}
                >
                  {s.name[0]}
                </div>
                <span
                  className={`text-[11px] font-medium px-2 py-1 rounded-full border flex items-center gap-1.5 ${
                    s.connected
                      ? "border-positive/40 text-positive"
                      : "border-elevated text-text-muted"
                  }`}
                >
                  <span
                    className={`w-1.5 h-1.5 rounded-full ${
                      s.connected ? "bg-positive" : "bg-text-muted"
                    }`}
                  />
                  {s.connected ? "Connected" : "Off"}
                </span>
              </div>
              <div className="text-white text-sm font-medium">{s.name}</div>
              <div className="text-text-muted text-xs mt-1 leading-5">
                {s.description}
              </div>
            </div>
          ))}
        </div>
      </section>

      <section>
        <div className="mb-5">
          <h2 className="text-base font-medium text-white">Past breakdowns</h2>
          <p className="text-text-muted text-sm mt-1">
            Every weekly summary generated for your account.
          </p>
        </div>
        <div className="divide-y divide-elevated border-y border-elevated">
          {weeks.map((week) => (
            <div
              key={week.generated_at}
              className="flex flex-col md:flex-row md:items-center gap-2 md:gap-6 py-4"
            >
              <div className="md:w-32 shrink-0">
                <div className="text-white text-sm font-medium">
                  {week.generated_at}
                </div>
                <div className="text-text-muted text-xs mt-0.5">
                  {week.insights.length} insights
                </div>
              </div>
              <div className="text-text-muted text-sm leading-6 md:flex-1 line-clamp-2">
                {week.summary}
              </div>
            </div>
          ))}
        </div>
      </section>
    </div>
  );
}
