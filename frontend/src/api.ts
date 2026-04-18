import type { InsightResponse } from "./types";
import { mockInsights } from "./mock-insights";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";
const USER_ID = import.meta.env.VITE_USER_ID ?? "user-1";

export interface FetchResult {
  data: InsightResponse[];
  source: "api" | "mock";
  error?: string;
}

function toDateString(value: unknown): string {
  if (typeof value !== "string") return "unknown";
  return value.slice(0, 10);
}

function normalize(raw: unknown): InsightResponse {
  const obj = raw as Partial<InsightResponse> & { generated_at?: string };
  return {
    user_id: obj.user_id ?? USER_ID,
    generated_at: toDateString(obj.generated_at),
    summary: obj.summary ?? "",
    insights: Array.isArray(obj.insights) ? obj.insights : [],
    timeline: Array.isArray(obj.timeline) ? obj.timeline : undefined,
  };
}

export async function fetchInsights(): Promise<FetchResult> {
  if (!API_BASE) {
    return { data: mockInsights, source: "mock" };
  }

  try {
    const url = `${API_BASE}/api/v1/insights?user_id=${encodeURIComponent(
      USER_ID
    )}&days=7`;
    const res = await fetch(url, {
      headers: { Accept: "application/json" },
    });
    if (!res.ok) throw new Error(`HTTP ${res.status}`);
    const json = await res.json();

    const latest = normalize(json);

    const pastWeeks = mockInsights
      .filter((w) => w.generated_at !== latest.generated_at)
      .slice(0, 2);

    return {
      data: [latest, ...pastWeeks],
      source: "api",
    };
  } catch (e) {
    return {
      data: mockInsights,
      source: "mock",
      error: e instanceof Error ? e.message : String(e),
    };
  }
}
