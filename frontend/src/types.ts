// Mirrors shared/schema.json exactly. If the contract changes, update here.

export type EventStatus = "confirmed" | "cancelled" | "tentative";
export type InsightType = "correlation" | "trend" | "anomaly" | "cluster";
export type DataSource = "health" | "calendar" | "messaging";

export interface TimeRange {
  start: string;
  end: string;
}

export interface HealthMetrics {
  steps?: number;
  sleep_hours?: number;
  sleep_quality?: number;
  heart_rate_avg?: number;
  active_minutes?: number;
  calories_burned?: number;
}

export interface CalendarEvent {
  id: string;
  title: string;
  start_time: string;
  end_time: string;
  status: EventStatus;
  category?: string;
  attendee_count?: number;
  location?: string;
}

export interface MessageSummary {
  chat_id: string;
  contact_name?: string;
  date: string;
  message_count_sent: number;
  message_count_received?: number;
  response_time_avg_seconds?: number;
  active_hours?: number[];
  sentiment_score?: number;
}

export interface DayRecord {
  date: string;
  user_id: string;
  health?: HealthMetrics;
  calendar_events?: CalendarEvent[];
  messaging?: MessageSummary[];
}

export interface PatternInsight {
  id: string;
  type: InsightType;
  description: string;
  confidence: number;
  sources: DataSource[];
  date_range?: TimeRange;
  supporting_data?: Record<string, unknown>;
  reflection_question?: string;
}

export interface InsightResponse {
  user_id: string;
  generated_at: string;
  summary?: string;
  insights: PatternInsight[];
  timeline?: DayRecord[];
}
