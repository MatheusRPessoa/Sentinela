import {
  Area,
  CartesianGrid,
  ComposedChart,
  Line,
  ReferenceLine,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

import type {
    Signal, 
    TrendWeek 
} from "../types/api";

interface TrendChartProps {
  data: TrendWeek[];
  signals: Signal[];
}

interface ChartData extends TrendWeek {
  historical_range: number;
}

interface CustomTooltipProps {
  active?: boolean;
  label?: number | string;
  payload?: Array<{
    payload: ChartData;
  }>;
}

function CustomTooltip({
  active,
  label,
  payload,
}: CustomTooltipProps) {
  if (!active || !payload?.length) {
    return null;
  }

  const data = payload[0].payload;

  const formatNumber = (value: number) =>
    value.toLocaleString("pt-BR", {
      maximumFractionDigits: 1,
    });

  return (
    <div className="chart-tooltip">
      <strong>SE {label}</strong>

      <dl>
        <div>
          <dt>2026</dt>
          <dd>{formatNumber(data.record_count)}</dd>
        </div>

        <div>
          <dt>Mediana histórica</dt>
          <dd>{formatNumber(data.historical_median)}</dd>
        </div>

        <div>
          <dt>Q25</dt>
          <dd>{formatNumber(data.q25)}</dd>
        </div>

        <div>
          <dt>Q75</dt>
          <dd>{formatNumber(data.q75)}</dd>
        </div>
      </dl>
    </div>
  );
}

export function TrendChart({ data, signals }: TrendChartProps) {
    const chartData: ChartData[] = data.map((week) => ({
        ...week,
        historical_range: week.q75 - week.q25,
    }));

    return (
        <div className="trend-chart">
            <ResponsiveContainer width="100%" height={380}>
                <ComposedChart
                    data={chartData}
                    margin={{
                        top: 10,
                        right: 20,
                        bottom: 35,
                        left: 0,
                    }}
                >
                    <CartesianGrid strokeDasharray="3 3" />

                    <XAxis
                        dataKey="epi_week"
                        tickLine={false}
                        height={60}
                        label={{
                            value: "Semana epidemiológica",
                            position: "insideBottom",
                            offset: -10, 
                        }}
                    />

                    <YAxis
                        tickLine={false}
                        width={60}
                    />

                    <Tooltip content={<CustomTooltip />} />

                    {signals.map((signal) => (
                        <ReferenceLine
                            key={signal.epi_week}
                            x={signal.epi_week}
                            stroke="#b54708"
                            strokeDasharray="4 4"
                            label={{
                                value: "Sinal",
                                position: "insideTopRight",
                                fill: "#b54708",
                                fontSize: 12, 
                            }}
                        />
                    ))}

                    <Area
                        type="monotone"
                        dataKey="q25"
                        stackId="historical"
                        stroke="none"
                        fill="transparent"
                        legendType="none"
                        isAnimationActive={false}
                    />

                    <Area
                        type="monotone"
                        dataKey="historical_range"
                        stackId="historical"
                        stroke="none"
                        fill="#bfdbfe"
                        fillOpacity={0.5}
                        name="Faixa histórica Q25–Q75"
                        isAnimationActive={false}
                    />

                    <Line
                        type="monotone"
                        dataKey="historical_median"
                        name="Mediana histórica"
                        stroke="#2563eb"
                        strokeWidth={2}
                        dot={false}
                        activeDot={{ r: 4 }}
                    />

                    <Line
                        type="monotone"
                        dataKey="record_count"
                        name="2026"
                        stroke="#f97316"
                        strokeWidth={3}
                        dot={false}
                        activeDot={{ r: 5 }}
                    />

                    <Line
                        type="monotone"
                        dataKey="record_count"
                        name="2026"
                        stroke="#f97316"
                        strokeWidth={3}
                        dot={(props) => {
                            const week = props.payload as ChartData;

                            const isSignal = signals.some(
                            (signal) => signal.epi_week === week.epi_week,
                            );

                            if (!isSignal) {
                            return <g />;
                            }

                            return (
                            <circle
                                cx={props.cx}
                                cy={props.cy}
                                r={6}
                                fill="#fff"
                                stroke="#b54708"
                                strokeWidth={3}
                            />
                            );
                        }}
                        activeDot={{ r: 5 }}
                        />
                </ComposedChart>
            </ResponsiveContainer>

            <div
                className="chart-legend"
                aria-label="Legenda do gráfico"
                >
                <span>
                    <i className="legend-line legend-observed" />
                    2026
                </span>

                <span>
                    <i className="legend-area" />
                    Faixa histórica Q25–Q75
                </span>

                <span>
                    <i className="legend-line legend-median" />
                    Mediana histórica
                </span>
            </div>

            {signals.length > 0 && (
            <div className="chart-signals">
                <span>Sinais no gráfico:</span>

                {signals.map((signal) => (
                <a
                    key={signal.epi_week}
                    href={`#signal-week-${signal.epi_week}`}
                >
                    SE {signal.epi_week}
                </a>
                ))}
            </div>
            )}
        </div>
    )
}