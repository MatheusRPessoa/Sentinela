export interface TrendWeek {
  epi_week: number;
  record_count: number;
  historical_median: number;
  q25: number;
  q75: number;
}

export interface TrendResponse {
  region: string;
  year: number;
  weeks: TrendWeek[];
}

export interface Signal {
  epi_week: number;
  week_start: string;
  week_end: string;
  record_count: number;
  historical_median: number;
  q75: number;
  median_threshold: number;
  ratio_to_median: number;
  historical_years: number;
  data_status: string;
  signal_status: string;
  signal_reason: string;
}

export interface SignalResponse {
  region: string;
  year: number;
  signals: Signal[];
}

export interface MetadataResponse {
  source: string;
  region: string;
  year: number;
  source_updated_at: string;
  observed_through: string;
  first_observed_week: number;
  last_observed_week: number;
  observed_weeks: number;
  limitations: string[];
}