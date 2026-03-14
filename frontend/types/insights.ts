export type InsightTypes = 'correlation' | 'trend' | 'anomaly' | 'cluster';

export type DataSources = 'health' | 'calendar' | 'messaging';

export interface PatternInsight {
    id: string;
    type: InsightTypes;
    description: string;
    confidence: number;
    sources: Array<DataSources>;
    reflection_question?: string;
}

export interface InsightResponse {
    user_id: string;
    generated_at: string;
    summary: string;
    insights: Array<PatternInsight>;
}