import type { InsightType, DataSource } from "../types";

export const insightStyles: Record<
  InsightType,
  { label: string; bg: string; text: string; accent: string }
> = {
  correlation: {
    label: "correlation",
    bg: "bg-primary/15",
    text: "text-primary",
    accent: "#4F7CFF",
  },
  trend: {
    label: "trend",
    bg: "bg-positive/15",
    text: "text-positive",
    accent: "#10B981",
  },
  anomaly: {
    label: "anomaly",
    bg: "bg-warning/15",
    text: "text-warning",
    accent: "#F59E0B",
  },
  cluster: {
    label: "cluster",
    bg: "bg-accent/15",
    text: "text-accent",
    accent: "#A78BFA",
  },
};

export const sourceColors: Record<DataSource, string> = {
  calendar: "#4F7CFF",
  health: "#10B981",
  messaging: "#A78BFA",
};
