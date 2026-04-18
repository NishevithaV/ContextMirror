import type { InsightResponse } from "./types";
import { mockInsights } from "./mock-insights";
import { clearStoredAuth, getStoredToken } from "./auth/AuthContext";

const API_BASE = import.meta.env.VITE_API_BASE ?? "";

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
    user_id: obj.user_id ?? "",
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

  const token = getStoredToken();
  if (!token) {
    // No token yet — show mock so UI isn't blank, but mark as mock.
    return { data: mockInsights, source: "mock", error: "Not signed in" };
  }

  try {
    const res = await fetch(`${API_BASE}/api/v1/insights?days=7`, {
      headers: {
        Accept: "application/json",
        Authorization: `Bearer ${token}`,
      },
    });

    if (res.status === 401) {
      // Token expired or invalid — clear and force a re-sign-in on next nav.
      clearStoredAuth();
      throw new Error("Session expired. Please sign in again.");
    }
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
