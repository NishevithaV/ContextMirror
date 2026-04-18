import type { InsightResponse } from "./types";

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
        reflection_question: "Is there a way to cap meetings on days you need good sleep?",
      },
      {
        id: "1b",
        type: "trend",
        description:
          "Your step count has been steadily increasing over the past 3 weeks — up 18% from your baseline.",
        confidence: 0.92,
        sources: ["health"],
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
