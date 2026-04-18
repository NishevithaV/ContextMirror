export type InsightType = "correlation" | "trend" | "anomaly" | "cluster";
export type SourceKey = "calendar" | "health" | "messaging" | "whatsapp";

export interface PatternInsight {
  id: string;
  type: InsightType;
  description: string;
  confidence: number;
  sources: SourceKey[];
  reflection_question?: string;
}

export interface InsightResponse {
  user_id: string;
  generated_at: string;
  summary: string;
  insights: PatternInsight[];
}
