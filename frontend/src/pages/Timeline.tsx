import { useEffect, useMemo, useState } from "react";
import { fetchInsights } from "../api";
import type { CalendarEvent, DayRecord, MessageSummary } from "../types";
import { sourceColors } from "../lib/insight-style";

const categoryColor: Record<string, string> = {
  meeting: "#4F7CFF",
  "deep-work": "#A78BFA",
  personal: "#10B981",
  social: "#F59E0B",
};

function fmtWeekday(date: string) {
  return new Date(date + "T00:00:00").toLocaleDateString("en-US", {
    weekday: "short",
  });
}
function fmtDay(date: string) {
  return new Date(date + "T00:00:00").toLocaleDateString("en-US", {
    day: "numeric",
  });
}
function fmtTime(iso: string) {
  return new Date(iso).toLocaleTimeString("en-US", {
    hour: "numeric",
    minute: "2-digit",
  });
}

export function Timeline() {
  const [timeline, setTimeline] = useState<DayRecord[] | null>(null);
  const [selected, setSelected] = useState<string | null>(null);

  useEffect(() => {
    fetchInsights().then((r) => {
      const days = r.data[0]?.timeline ?? [];
      setTimeline(days);
      if (days.length > 0) setSelected(days[days.length - 1].date);
    });
  }, []);

  const selectedDay = useMemo(
    () => timeline?.find((d) => d.date === selected) ?? null,
    [timeline, selected]
  );

  if (!timeline) return <div className="text-text-muted">Loading…</div>;

  if (timeline.length === 0) {
    return (
      <div className="flex flex-col gap-10">
        <header>
          <h1 className="text-2xl font-semibold tracking-tight text-white">
            Timeline
          </h1>
          <p className="text-text-muted text-sm mt-1">
            Day-by-day view of your connected data sources.
          </p>
        </header>
        <div className="rounded-2xl border border-elevated bg-card/40 p-10 text-center">
          <p className="text-text-muted text-sm">
            Timeline data will appear here once your sources are connected.
          </p>
        </div>
      </div>
    );
  }

  return (
    <div className="flex flex-col gap-10">
      <header>
        <h1 className="text-2xl font-semibold tracking-tight text-white">
          Timeline
        </h1>
        <p className="text-text-muted text-sm mt-1">
          {timeline[0].date} → {timeline[timeline.length - 1].date} · day-by-day
          breakdown across all sources.
        </p>
      </header>

      <DayStrip
        days={timeline}
        selected={selected}
        onSelect={(d) => setSelected(d)}
      />

      {selectedDay && <DayDetail day={selectedDay} />}
    </div>
  );
}

function DayStrip({
  days,
  selected,
  onSelect,
}: {
  days: DayRecord[];
  selected: string | null;
  onSelect: (date: string) => void;
}) {
  const maxSleep = 9;
  return (
    <section className="rounded-2xl border border-elevated bg-card/40 p-5">
      <div className="text-text-muted text-xs uppercase tracking-widest mb-5">
        Week overview
      </div>
      <div className="grid grid-cols-7 gap-2">
        {days.map((d) => {
          const isActive = selected === d.date;
          const sleep = d.health?.sleep_hours ?? 0;
          const steps = d.health?.steps ?? 0;
          const meetings = (d.calendar_events ?? []).filter(
            (e) => e.status !== "cancelled"
          ).length;
          const msgs = (d.messaging ?? []).reduce(
            (s, m) => s + m.message_count_sent,
            0
          );
          return (
            <button
              key={d.date}
              onClick={() => onSelect(d.date)}
              className={`flex flex-col items-stretch gap-2 rounded-xl border p-2.5 text-left transition-colors ${
                isActive
                  ? "border-primary/60 bg-primary/5"
                  : "border-elevated hover:bg-elevated/40"
              }`}
            >
              <div className="flex items-baseline justify-between">
                <span className="text-[10px] uppercase tracking-widest text-text-muted">
                  {fmtWeekday(d.date)}
                </span>
                <span className="text-white text-sm font-medium">
                  {fmtDay(d.date)}
                </span>
              </div>

              <div className="h-10 flex items-end">
                <div
                  className="w-full rounded-sm"
                  style={{
                    height: `${Math.min(100, (sleep / maxSleep) * 100)}%`,
                    backgroundColor: sleep >= 7 ? "#10B981" : sleep >= 6 ? "#F59E0B" : "#EF4444",
                    opacity: 0.7,
                  }}
                  title={`${sleep}h sleep`}
                />
              </div>

              <div className="flex items-center gap-1">
                {Array.from({ length: Math.min(meetings, 4) }).map((_, i) => (
                  <span
                    key={i}
                    className="w-1.5 h-1.5 rounded-full"
                    style={{ backgroundColor: sourceColors.calendar }}
                  />
                ))}
                {meetings > 4 && (
                  <span className="text-text-muted text-[10px]">
                    +{meetings - 4}
                  </span>
                )}
              </div>

              <div className="grid grid-cols-2 gap-1 mt-1">
                <div className="flex flex-col">
                  <span className="text-[10px] text-text-muted">steps</span>
                  <span className="text-white text-[11px] font-medium">
                    {steps >= 1000 ? `${(steps / 1000).toFixed(1)}k` : steps}
                  </span>
                </div>
                <div className="flex flex-col">
                  <span className="text-[10px] text-text-muted">msgs</span>
                  <span className="text-white text-[11px] font-medium">
                    {msgs}
                  </span>
                </div>
              </div>
            </button>
          );
        })}
      </div>
    </section>
  );
}

function DayDetail({ day }: { day: DayRecord }) {
  const events = (day.calendar_events ?? []).slice().sort((a, b) =>
    a.start_time.localeCompare(b.start_time)
  );
  const msgs = day.messaging ?? [];

  return (
    <div className="grid grid-cols-1 lg:grid-cols-3 gap-4">
      <HealthCard day={day} />
      <CalendarCard events={events} />
      <MessagingCard msgs={msgs} />
    </div>
  );
}

function HealthCard({ day }: { day: DayRecord }) {
  const h = day.health;
  return (
    <div className="rounded-2xl border border-elevated bg-card/40 p-5">
      <div className="flex items-center gap-2 mb-4">
        <span
          className="w-1.5 h-1.5 rounded-full"
          style={{ backgroundColor: sourceColors.health }}
        />
        <span className="text-text-muted text-xs uppercase tracking-widest">
          Health
        </span>
      </div>
      {h ? (
        <div className="flex flex-col gap-3">
          <Metric label="Sleep" value={h.sleep_hours ? `${h.sleep_hours}h` : "—"} />
          <Metric
            label="Quality"
            value={h.sleep_quality ? `${h.sleep_quality}/10` : "—"}
          />
          <Metric
            label="Steps"
            value={h.steps ? h.steps.toLocaleString() : "—"}
          />
          <Metric
            label="Resting HR"
            value={h.heart_rate_avg ? `${h.heart_rate_avg} bpm` : "—"}
          />
          <Metric
            label="Active min"
            value={h.active_minutes !== undefined ? `${h.active_minutes}` : "—"}
          />
        </div>
      ) : (
        <p className="text-text-muted text-sm">No health data this day.</p>
      )}
    </div>
  );
}

function CalendarCard({ events }: { events: CalendarEvent[] }) {
  return (
    <div className="rounded-2xl border border-elevated bg-card/40 p-5">
      <div className="flex items-center gap-2 mb-4">
        <span
          className="w-1.5 h-1.5 rounded-full"
          style={{ backgroundColor: sourceColors.calendar }}
        />
        <span className="text-text-muted text-xs uppercase tracking-widest">
          Calendar · {events.length}
        </span>
      </div>
      {events.length === 0 ? (
        <p className="text-text-muted text-sm">No events.</p>
      ) : (
        <ul className="flex flex-col gap-3">
          {events.map((e) => {
            const color =
              (e.category && categoryColor[e.category]) || "#6b7280";
            return (
              <li key={e.id} className="flex items-start gap-3">
                <span
                  className="mt-1.5 w-1.5 h-1.5 rounded-full shrink-0"
                  style={{ backgroundColor: color }}
                />
                <div className="flex-1 min-w-0">
                  <div className="flex items-center gap-2">
                    <span
                      className={`text-sm truncate ${
                        e.status === "cancelled"
                          ? "line-through text-text-muted"
                          : "text-white"
                      }`}
                    >
                      {e.title}
                    </span>
                  </div>
                  <div className="text-text-muted text-[11px] mt-0.5">
                    {fmtTime(e.start_time)} – {fmtTime(e.end_time)}
                    {e.category ? ` · ${e.category}` : ""}
                    {e.attendee_count ? ` · ${e.attendee_count} ppl` : ""}
                  </div>
                </div>
              </li>
            );
          })}
        </ul>
      )}
    </div>
  );
}

function MessagingCard({ msgs }: { msgs: MessageSummary[] }) {
  const totalSent = msgs.reduce((s, m) => s + m.message_count_sent, 0);
  const totalRecv = msgs.reduce(
    (s, m) => s + (m.message_count_received ?? 0),
    0
  );
  return (
    <div className="rounded-2xl border border-elevated bg-card/40 p-5">
      <div className="flex items-center gap-2 mb-4">
        <span
          className="w-1.5 h-1.5 rounded-full"
          style={{ backgroundColor: sourceColors.messaging }}
        />
        <span className="text-text-muted text-xs uppercase tracking-widest">
          Messaging
        </span>
      </div>
      {msgs.length === 0 ? (
        <p className="text-text-muted text-sm">No messaging activity.</p>
      ) : (
        <div className="flex flex-col gap-3">
          <div className="flex gap-6 text-xs">
            <div>
              <div className="text-text-muted">Sent</div>
              <div className="text-white text-base font-medium">
                {totalSent}
              </div>
            </div>
            <div>
              <div className="text-text-muted">Received</div>
              <div className="text-white text-base font-medium">
                {totalRecv}
              </div>
            </div>
          </div>
          <ul className="flex flex-col gap-2 mt-1">
            {msgs.map((m) => (
              <li
                key={m.chat_id}
                className="flex items-center justify-between text-sm"
              >
                <span className="text-white truncate">
                  {m.contact_name ?? m.chat_id}
                </span>
                <span className="text-text-muted text-xs">
                  {m.message_count_sent} sent
                </span>
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function Metric({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex items-center justify-between text-sm">
      <span className="text-text-muted">{label}</span>
      <span className="text-white font-medium">{value}</span>
    </div>
  );
}
