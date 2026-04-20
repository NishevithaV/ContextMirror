import type { DayRecord, InsightResponse } from "./types";

// 7-day timeline for the most recent week (2026-03-01 → 2026-03-07).
// Shape matches shared/schema.json DayRecord exactly.
const recentTimeline: DayRecord[] = [
  {
    date: "2026-03-01",
    user_id: "user-1",
    health: { steps: 6200, sleep_hours: 7.2, sleep_quality: 7, heart_rate_avg: 62, active_minutes: 28 },
    calendar_events: [
      { id: "e1", title: "Sunday reset", start_time: "2026-03-01T10:00:00", end_time: "2026-03-01T11:00:00", status: "confirmed", category: "personal" },
    ],
    messaging: [
      { chat_id: "c1", contact_name: "Family", date: "2026-03-01", message_count_sent: 18, message_count_received: 22, active_hours: [10, 14, 20] },
    ],
  },
  {
    date: "2026-03-02",
    user_id: "user-1",
    health: { steps: 9400, sleep_hours: 6.8, sleep_quality: 6, heart_rate_avg: 65, active_minutes: 42 },
    calendar_events: [
      { id: "e2", title: "Standup", start_time: "2026-03-02T09:00:00", end_time: "2026-03-02T09:30:00", status: "confirmed", category: "meeting", attendee_count: 6 },
      { id: "e3", title: "Design review", start_time: "2026-03-02T14:00:00", end_time: "2026-03-02T15:00:00", status: "confirmed", category: "meeting", attendee_count: 4 },
      { id: "e4", title: "Deep work", start_time: "2026-03-02T15:30:00", end_time: "2026-03-02T17:30:00", status: "confirmed", category: "deep-work" },
    ],
    messaging: [
      { chat_id: "c2", contact_name: "Work team", date: "2026-03-02", message_count_sent: 32, message_count_received: 48, active_hours: [9, 10, 14, 16] },
    ],
  },
  {
    date: "2026-03-03",
    user_id: "user-1",
    health: { steps: 11200, sleep_hours: 7.5, sleep_quality: 8, heart_rate_avg: 60, active_minutes: 55 },
    calendar_events: [
      { id: "e5", title: "1:1 with manager", start_time: "2026-03-03T11:00:00", end_time: "2026-03-03T11:30:00", status: "confirmed", category: "meeting", attendee_count: 2 },
      { id: "e6", title: "Evening walk", start_time: "2026-03-03T18:30:00", end_time: "2026-03-03T19:15:00", status: "confirmed", category: "personal" },
    ],
    messaging: [
      { chat_id: "c1", contact_name: "Family", date: "2026-03-03", message_count_sent: 24, message_count_received: 20, active_hours: [12, 19, 20] },
    ],
  },
  {
    date: "2026-03-04",
    user_id: "user-1",
    health: { steps: 5800, sleep_hours: 5.9, sleep_quality: 5, heart_rate_avg: 68, active_minutes: 18 },
    calendar_events: [
      { id: "e7", title: "All-hands", start_time: "2026-03-04T10:00:00", end_time: "2026-03-04T11:00:00", status: "confirmed", category: "meeting", attendee_count: 40 },
      { id: "e8", title: "Client sync", start_time: "2026-03-04T13:00:00", end_time: "2026-03-04T14:00:00", status: "confirmed", category: "meeting", attendee_count: 5 },
      { id: "e9", title: "Sprint planning", start_time: "2026-03-04T15:00:00", end_time: "2026-03-04T16:30:00", status: "confirmed", category: "meeting", attendee_count: 8 },
      { id: "e10", title: "Retro", start_time: "2026-03-04T17:00:00", end_time: "2026-03-04T18:00:00", status: "cancelled", category: "meeting" },
    ],
    messaging: [
      { chat_id: "c2", contact_name: "Work team", date: "2026-03-04", message_count_sent: 0, message_count_received: 12, active_hours: [] },
    ],
  },
  {
    date: "2026-03-05",
    user_id: "user-1",
    health: { steps: 8800, sleep_hours: 7.8, sleep_quality: 8, heart_rate_avg: 61, active_minutes: 44 },
    calendar_events: [
      { id: "e11", title: "Focus block", start_time: "2026-03-05T09:00:00", end_time: "2026-03-05T12:00:00", status: "confirmed", category: "deep-work" },
      { id: "e12", title: "Coffee with Sam", start_time: "2026-03-05T15:00:00", end_time: "2026-03-05T16:00:00", status: "confirmed", category: "social", attendee_count: 2 },
    ],
    messaging: [
      { chat_id: "c3", contact_name: "Sam", date: "2026-03-05", message_count_sent: 14, message_count_received: 18, active_hours: [14, 15, 16] },
    ],
  },
  {
    date: "2026-03-06",
    user_id: "user-1",
    health: { steps: 10400, sleep_hours: 7.1, sleep_quality: 7, heart_rate_avg: 63, active_minutes: 50 },
    calendar_events: [
      { id: "e13", title: "Review & ship", start_time: "2026-03-06T10:00:00", end_time: "2026-03-06T11:30:00", status: "confirmed", category: "meeting", attendee_count: 3 },
      { id: "e14", title: "Evening run", start_time: "2026-03-06T19:00:00", end_time: "2026-03-06T19:45:00", status: "confirmed", category: "personal" },
    ],
    messaging: [
      { chat_id: "c1", contact_name: "Family", date: "2026-03-06", message_count_sent: 28, message_count_received: 25, active_hours: [13, 17, 21] },
    ],
  },
  {
    date: "2026-03-07",
    user_id: "user-1",
    health: { steps: 7300, sleep_hours: 8.1, sleep_quality: 9, heart_rate_avg: 59, active_minutes: 36 },
    calendar_events: [
      { id: "e15", title: "Brunch", start_time: "2026-03-07T11:00:00", end_time: "2026-03-07T12:30:00", status: "confirmed", category: "social", attendee_count: 4 },
    ],
    messaging: [
      { chat_id: "c1", contact_name: "Family", date: "2026-03-07", message_count_sent: 22, message_count_received: 20, active_hours: [11, 16, 20] },
    ],
  },
];

export const mockInsights: InsightResponse[] = [
  {
    user_id: "user-1",
    generated_at: "2026-03-07",
    summary:
      "Your sleep quality dropped noticeably on days with 3+ meetings. On the bright side, your evening walks seem to correlate with better rest — you slept 40 minutes longer on walk days.",
    insights: [
      {
        id: "1a",
        type: "correlation",
        description:
          "Days with 3 or more meetings correlated with 30% lower sleep scores the following night.",
        confidence: 0.87,
        sources: ["calendar", "health"],
        date_range: { start: "2026-03-01T00:00:00Z", end: "2026-03-07T23:59:59Z" },
        supporting_data: {
          series: [
            { meetings: 1, sleep_score: 7 },
            { meetings: 3, sleep_score: 6 },
            { meetings: 1, sleep_score: 8 },
            { meetings: 4, sleep_score: 5 },
            { meetings: 3, sleep_score: 8 },
            { meetings: 2, sleep_score: 7 },
            { meetings: 1, sleep_score: 9 },
          ],
        },
        reflection_question: "Is there a way to cap meetings on days you need good sleep?",
      },
      {
        id: "1b",
        type: "trend",
        description:
          "Your step count has been steadily increasing over the past 3 weeks — up 18% from your baseline.",
        confidence: 0.92,
        sources: ["health"],
        supporting_data: { weekly_avg: [6200, 7100, 7800, 8400] },
      },
      {
        id: "1c",
        type: "anomaly",
        description:
          "Wednesday had zero messages sent, which is unusual compared to your average of 45 messages per day.",
        confidence: 0.78,
        sources: ["messaging"],
        reflection_question: "Was Wednesday a focus day, or were you feeling off?",
      },
      {
        id: "1d",
        type: "correlation",
        description:
          "Evening walks (after 6pm) correlated with 40 extra minutes of sleep that night.",
        confidence: 0.81,
        sources: ["health"],
      },
    ],
    timeline: recentTimeline,
  },
  {
    user_id: "user-1",
    generated_at: "2026-02-28",
    summary:
      "A quieter week overall — fewer meetings and more consistent sleep. Your messaging spiked mid-week around a group planning thread, but energy levels stayed steady.",
    insights: [
      {
        id: "2a",
        type: "trend",
        description: "Your resting heart rate has dropped by 3 bpm over the last two weeks.",
        confidence: 0.88,
        sources: ["health"],
      },
      {
        id: "2b",
        type: "cluster",
        description:
          "Most of your messaging activity this week happened in a 2-hour window on Wednesday afternoon.",
        confidence: 0.83,
        sources: ["messaging"],
        reflection_question: "Do you prefer batching conversations or spreading them out?",
      },
      {
        id: "2c",
        type: "correlation",
        description: "Days with no evening meetings had 25% higher sleep scores.",
        confidence: 0.79,
        sources: ["calendar", "health"],
      },
    ],
  },
  {
    user_id: "user-1",
    generated_at: "2026-02-21",
    summary:
      "This was a high-activity week. Lots of meetings, lots of messages, but your sleep held up better than expected — possibly because you kept your evening routine consistent.",
    insights: [
      {
        id: "3a",
        type: "anomaly",
        description:
          "You had 12 meetings on Tuesday, more than double your weekly average per day.",
        confidence: 0.95,
        sources: ["calendar"],
        reflection_question: "Did that many meetings feel productive or overwhelming?",
      },
      {
        id: "3b",
        type: "trend",
        description:
          "Your messaging volume has been climbing steadily — up 30% over 3 weeks.",
        confidence: 0.84,
        sources: ["messaging"],
      },
      {
        id: "3c",
        type: "correlation",
        description:
          "On days you walked 8,000+ steps, your self-reported mood was consistently higher.",
        confidence: 0.76,
        sources: ["health"],
      },
    ],
  },
];
