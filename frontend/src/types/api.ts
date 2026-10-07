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
  historical_start_year: number;
  historical_end_year: number;
  limitations: string[];
}

export interface RegionOption {
  value: string;
  label: string;
  years: number[];
}

export interface OptionsResponse {
  regions: RegionOption[];
}

export interface CoverageWeek {
  epi_week: number;
  week_start: string;
  week_end: string;
  record_count: number | null;
  calendar_status: string;
  data_status: string;
}

export interface CoverageResponse {
  region: string;
  year: number;
  weeks: CoverageWeek[];
}

export interface NowcastWeek {
  epi_week: number;
  lag_days: number;
  snapshot_date: string;
  known_cases: number;
  nowcast: number;
  q75: number;
  median_threshold: number;
  would_signal: boolean;
}

export interface NowcastResponse {
  region: string;
  year: number;
  weeks: NowcastWeek[];
}

export type OperationalState = 
  | "NORMAL"
  | "SIGNAL"
  | "ALERT"
  | "PENDING";

export interface OperationalWeek {
  epi_week: number;
  is_mature: boolean;
  has_signal: boolean | null;
  operational_state: OperationalState;
  last_stable_state:
    | "NORMAL"
    | "SIGNAL"
    | "ALERT";
  consecutive_signals: number;
  consecutive_no_signals: number;
}
export interface OperationalStatusResponse {
  region: string;
  year: number;
  weeks: OperationalWeek[];
}
