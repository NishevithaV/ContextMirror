# A few notes about `frontend/data/mock-insights.ts`

- `mockInsights` is `InsightResponse[]` but the real contract is one `InsightResponse` per call. Real backend will need 2 endpoints: current + history.
- `generated_at` in mock is `2026-03-07` but the real contracts is ISO datetime. Will need to update when wiring real API.
- Mock is missing `timeline`, `date_range`, `supporting_data`. Find for now since UI doesn't use them.

- 