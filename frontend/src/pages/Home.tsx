import { useEffect, useState } from "react";
import { fetchInsights } from "../api";
import type { InsightResponse, PatternInsight } from "../types";
import { insightStyles, sourceColors } from "../lib/insight-style";
import { Bars, Sparkline } from "../components/Sparkline";

export function Home() {
  const [weeks, setWeeks] = useState<InsightResponse[] | null>(null);
  const [source, setSource] = useState<"api" | "mock">("mock");
  const [error, setError] = useState<string | undefined>();

  useEffect(() => {
    fetchInsights().then((r) => {
      setWeeks(r.data);
      setSource(r.source);
      setError(r.error);
    });
  }, []);

  if (!weeks) return <div className="text-text-muted">Loading…</div>;
  const latestWeek = weeks[0];
  const totalInsights = weeks.reduce((sum, w) => sum + w.insights.length, 0);
  const weeklyCounts = [...weeks].reverse().map((w) => w.insights.length);
  const avgConfidence = Math.round(
    (latestWeek.insights.reduce((s, i) => s + i.confidence, 0) /
      latestWeek.insights.length) *
      100
  );
  const confidenceTrend = [72, 75, 71, 78, 80, avgConfidence];

  return (
    <div className="flex flex-col gap-10">
      <header className="flex flex-col md:flex-row md:items-end md:justify-between gap-3">
        <div>
          <h1 className="text-2xl font-semibold tracking-tight text-white">
            This week
          </h1>
          <p className="text-text-muted text-sm mt-1">
            Patterns detected across your calendar and messaging activity.
          </p>
        </div>
        <div
          className={`self-start text-[10px] uppercase tracking-widest px-2.5 py-1 rounded-full border flex items-center gap-2 ${
            source === "api"
              ? "border-positive/40 text-positive"
              : "border-elevated text-text-muted"
          }`}
          title={error}
        >
          <span
            className={`w-1.5 h-1.5 rounded-full ${
              source === "api" ? "bg-positive" : "bg-text-muted"
            }`}
          />
          {source === "api" ? "Live data" : "Demo data"}
        </div>
      </header>

      <section className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <StatCard
          label="Insights this week"
          value={String(latestWeek.insights.length)}
          delta="+1"
          deltaColor="text-positive"
          viz={<Bars values={weeklyCounts} color="#4F7CFF" />}
        />
        <StatCard
          label="Avg confidence"
          value={`${avgConfidence}%`}
          delta="+4.2%"
          deltaColor="text-positive"
          viz={<Sparkline values={confidenceTrend} color="#10B981" />}
        />
        <StatCard
          label="Active sources"
          value="2 / 3"
          delta="Health off"
          deltaColor="text-warning"
          viz={
            <div className="flex items-center gap-2">
              <Dot color={sourceColors.calendar} />
              <Dot color={sourceColors.whatsapp} />
              <Dot color="#3f3f46" />
            </div>
          }
        />
      </section>

      <section className="rounded-2xl border border-elevated bg-card/40 p-6 md:p-7">
        <div className="flex items-center gap-2">
          <div className="w-1.5 h-1.5 rounded-full bg-primary" />
          <div className="text-text-muted text-xs uppercase tracking-widest">
            This week's story
          </div>
        </div>
        <p className="text-lg md:text-xl text-white mt-3 leading-relaxed max-w-3xl">
          {latestWeek.summary}
        </p>
        <div className="text-text-muted text-xs mt-6">
          Generated {latestWeek.generated_at} · {totalInsights} insights all time
        </div>
      </section>

      <section>
        <div className="flex items-end justify-between mb-1">
          <h2 className="text-base font-medium text-white">Insights</h2>
          <span className="text-text-muted text-xs">
            {latestWeek.insights.length} patterns
          </span>
        </div>
        <p className="text-text-muted text-sm mb-5">
          Correlations and anomalies across your connected sources.
        </p>
        <div className="flex flex-col gap-3">
          {latestWeek.insights.map((insight) => (
            <InsightCard key={insight.id} insight={insight} />
          ))}
        </div>
      </section>

      <section>
        <div className="mb-5">
          <h2 className="text-base font-medium text-white">Past weeks</h2>
          <p className="text-text-muted text-sm mt-1">
            Previous breakdowns in reverse chronological order.
          </p>
        </div>
        <div className="divide-y divide-elevated border-y border-elevated">
          {weeks.slice(1).map((week) => (
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

function StatCard({
  label,
  value,
  delta,
  deltaColor,
  viz,
}: {
  label: string;
  value: string;
  delta?: string;
  deltaColor?: string;
  viz?: React.ReactNode;
}) {
  return (
    <div className="rounded-2xl border border-elevated bg-card/40 p-5">
      <div className="flex items-center justify-between">
        <div className="text-text-muted text-xs">{label}</div>
        {delta && (
          <div
            className={`text-[11px] font-medium px-1.5 py-0.5 rounded bg-elevated ${
              deltaColor ?? "text-text-muted"
            }`}
          >
            {delta}
          </div>
        )}
      </div>
      <div className="flex items-end justify-between mt-3">
        <div className="text-3xl font-semibold text-white tracking-tight">
          {value}
        </div>
        {viz && <div className="opacity-90">{viz}</div>}
      </div>
    </div>
  );
}

function InsightCard({ insight }: { insight: PatternInsight }) {
  const style = insightStyles[insight.type];
  const conf = Math.round(insight.confidence * 100);

  return (
    <div className="relative rounded-2xl border border-elevated bg-card/40 p-5 overflow-hidden">
      <div
        className="absolute left-0 top-0 bottom-0 w-0.5"
        style={{ backgroundColor: style.accent }}
      />
      <div className="flex items-center gap-2 mb-3 flex-wrap">
        <span
          className={`text-[11px] font-medium px-2 py-0.5 rounded ${style.bg} ${style.text}`}
        >
          {style.label}
        </span>
        <div className="flex items-center gap-1.5">
          {insight.sources.map((s) => (
            <span
              key={s}
              className="text-text-muted text-xs flex items-center gap-1"
            >
              <span
                className="w-1.5 h-1.5 rounded-full"
                style={{ backgroundColor: sourceColors[s] }}
              />
              {s}
            </span>
          ))}
        </div>
        <div className="ml-auto flex items-center gap-2">
          <ConfidenceBar value={conf} color={style.accent} />
          <span className="text-text-muted text-xs w-10 text-right">
            {conf}%
          </span>
        </div>
      </div>
      <p className="text-white text-sm leading-6">{insight.description}</p>
      {insight.reflection_question && (
        <p className="text-text-muted text-sm italic leading-6 mt-2">
          {insight.reflection_question}
        </p>
      )}
    </div>
  );
}

function ConfidenceBar({ value, color }: { value: number; color: string }) {
  return (
    <div className="w-16 h-1.5 rounded-full bg-elevated overflow-hidden">
      <div
        className="h-full rounded-full"
        style={{ width: `${value}%`, backgroundColor: color }}
      />
    </div>
  );
}

function Dot({ color }: { color: string }) {
  return (
    <span
      className="w-2 h-2 rounded-full"
      style={{ backgroundColor: color }}
    />
  );
}
