import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { DashboardLoading, DashboardState } from "./components/dashboard-state";
import { TrendChart } from "./components/trend-chart";
import { apiGet } from "./services/api";

import type {
  CoverageResponse,
  NowcastResponse,
  OperationalStatusResponse,
  MetadataResponse,
  OptionsResponse,
  SignalResponse,
  TrendResponse,
} from "./types/api";

interface DashboardProps {
  options: OptionsResponse;
}

function formatDateTime(value: string) {
  return new Intl.DateTimeFormat("pt-BR", {
    dateStyle: "short",
    timeStyle: "short",
  }).format(new Date(value));
}

function formatDate(value: string) {
  const [year, month, day] = value.split("-");

  return `${day}/${month}/${year}`;
}

function Dashboard({ options }: DashboardProps) {
  const [region, setRegion] = useState(
    () => options.regions[0].value,
  );

  const initialRegion = options.regions[0];

  const [year, setYear] = useState(
    () => initialRegion.years[0],
  );

  const metadataQuery = useQuery({
    queryKey: ["metadata", region, year],
    queryFn: () =>
      apiGet<MetadataResponse>("/api/metadata", {
        region,
        year,
      }),
  });

  const trendsQuery = useQuery({
    queryKey: ["trends", region, year],
    queryFn: () =>
      apiGet<TrendResponse>("/api/trends", {
        region,
        year,
      }),
  });

  const signalsQuery = useQuery({
    queryKey: ["signals", region, year],
    queryFn: () =>
      apiGet<SignalResponse>("/api/signals", {
        region,
        year,
      }),
  });

  const coverageQuery = useQuery({
    queryKey: ["coverage", region, year],
    queryFn: () =>
      apiGet<CoverageResponse>("/api/coverage", {
        region,
        year,
      }),
    enabled: region !== null && year !== null,
  });

  const nowcastQuery = useQuery({
    queryKey: ["nowcast", region, year],
    queryFn: () =>
        apiGet<NowcastResponse>("/api/nowcast", {
          region,
          year,
        }),
      enabled: region !== null && year !== null,
      retry: false,
  });

  const operationalStatusQuery = useQuery({
    queryKey: ["operational-status", region, year],
    queryFn: () =>
      apiGet<OperationalStatusResponse>("/api/status", {
        region,
        year,
      }),
    enabled: region !== null && year !== null,
    retry: false,
  });

  if (
    coverageQuery.isPending ||
    metadataQuery.isPending ||
    trendsQuery.isPending ||
    signalsQuery.isPending
  ) {
    return <DashboardLoading />;
  }

  if (
    metadataQuery.isError ||
    trendsQuery.isError ||
    signalsQuery.isError ||
    coverageQuery.isError

  ) {
    const handleRetry = () => {
      void Promise.all([
        metadataQuery.refetch(),
        trendsQuery.refetch(),
        signalsQuery.refetch(),
        coverageQuery.refetch(),
      ]);
    };

    return (
      <main className="dashboard">
        <DashboardState
          title="Não foi possível carregar o painel"
          description="Ocorreu um problema ao consultar os dados. Verifique a conexão e tente novamente."
          action={{
            label: "Tentar novamente",
            onClick: handleRetry,
          }}
        />
      </main>
    );
  }

  const metadata = metadataQuery.data;
  const trends = trendsQuery.data;
  const signals = signalsQuery.data;
  const coverage = coverageQuery.data;

  const nowcast = nowcastQuery.data ?? null;

  const operationalStatus =
    operationalStatusQuery.data ?? null;

  if (trends.weeks.length === 0) {
    return (
      <main className="dashboard">
        <DashboardState
          title="Nenhum dado disponível"
          description={`Não há observações disponíveis para ${region} em ${year}.`}
        />
      </main>
    );
  }

  const totalRecords = trends.weeks.reduce(
    (total, week) => total + week.record_count,
    0,
  );

  const selectedRegion = options.regions.find(
    (option) => option.value === region,
  );

  const operationalWeeks =
    operationalStatus?.weeks ?? [];

  const latestOperationalWeek =
    operationalWeeks.length > 0
      ? operationalWeeks[
          operationalWeeks.length - 1
        ]
      : null;

  const currentOperationalState =
    latestOperationalWeek?.operational_state ?? null;

  const lastStableState =
    latestOperationalWeek?.last_stable_state ?? null;
  
  const firstSignalWeek =
    operationalWeeks.find(
      (week) =>
         week.operational_state === "SIGNAL",
    ) ?? null;

  const firstAlertWeek =
    operationalWeeks.find(
      (week) =>
        week.operational_state === "ALERT",
    ) ?? null;

  const firstNowcastSignal =
    nowcast?.weeks[0] ?? null;

  return (
    <main
      className="dashboard"
      aria-labelledby="page-title"
    >
      <header className="page-header">
        <div>
          <p className="eyebrow">
            Vigilância epidemiológica
          </p>

          <h1 id="page-title">
            Sentinela
          </h1>

          <p className="subtitle">
            Monitoramento de SRAG em{" "}
            {selectedRegion?.label ?? region}
          </p>
        </div>

        <div className="source">
          <span>Fonte</span>

          <strong>
            {metadata.source}
          </strong>

          <small>
            Atualizado em{" "}
            {formatDateTime(metadata.source_updated_at)}
          </small>

          <small>
            Dados observados até{" "}
            {formatDate(metadata.observed_through)}
          </small>
        </div>
      </header>

      <section
        className="filters"
        aria-label="Filtros do painel"
      >
        <div className="filter-field">
          <label htmlFor="region-filter">
            Região
          </label>

          <select
            id="region-filter"
            value={region}
            onChange={(event) => {
              const nextRegion = event.target.value;

              const regionOption = options.regions.find(
                (option) => option.value === nextRegion,
              );

              if (!regionOption) {
                return ;
              }
              
              setRegion(nextRegion);
              setYear(regionOption.years[0]);
            }}
          >
            {options.regions.map((option) => (
              <option
                key={option.value}
                value={option.value}
              >
                {option.label}
              </option>
            ))}
          </select>
        </div>

        <div className="filter-field">
          <label htmlFor="year-filter">
            Ano
          </label>

          <select
            id="year-filter"
            value={year}
            onChange={(event) => {
              setYear(Number(event.target.value));
            }}
          >
            {selectedRegion?.years.map((option) => (
              <option
                key={option}
                value={option}
              >
                {option}
              </option>
            ))}
          </select>
        </div>
      </section>

      <section
        className="indicadores"
        aria-label="Indicadores principais"
      >
        <article className="card">
          <span>
            Registros observados
          </span>

          <strong>
            {totalRecords.toLocaleString("pt-BR")}
          </strong>

          <small>
            SRAG em residentes de {region}
          </small>
        </article>

        <article className="card">
          <span>
            Última semana observada
          </span>

          <strong>
            SE {metadata.last_observed_week}
          </strong>

          <small>
            {metadata.observed_weeks} semanas disponíveis
          </small>
        </article>

        <article className="card">
          <span>
            Sinais identificados
          </span>

          <strong>
            {signals.signals.length}
          </strong>

          <small>
            Regra estatística do Sentinela
          </small>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">
              Série temporal
            </p>

            <h2>
              Evolução semanal de SRAG
            </h2>
          </div>
          <div className="panel-meta">
            <span>
              Observado: SE {metadata.first_observed_week}–
              {metadata.last_observed_week}
            </span>

            <span>
              Referência: {metadata.historical_start_year}–
              {metadata.historical_end_year}
            </span>
          </div>
        </div>

        <TrendChart
          data={trends.weeks}
          coverage={coverage.weeks}
          signals={signals.signals}
          operationalStatus={
            operationalStatus?.weeks ?? []
          }
          year={year}
        />
      </section>

      <section
        id="signals"
        className="panel"
        aria-labelledby="signals-title"
      >
        <div className="panel-heading">
          <div>
            <p className="eyebrow">
              Monitoramento
            </p>

            <h2 id="signals-title">
              Sinais de aumento incomum
            </h2>
          </div>
        </div>

        {signals.signals.length === 0 ? (
          <p className="empty-state">
            Nenhum sinal identificado no período
          </p>
        ) : (
          <div className="signal-list">
            {signals.signals.map((signal) => (
              <article
                id={`signal-week-${signal.epi_week}`}
                className="signal-card"
                key={signal.epi_week}
              >
                <div>
                  <span className="signal-badge">
                    Sinal
                  </span>

                  <h3>
                    Semana epidemiológica{" "}
                    {signal.epi_week}
                  </h3>

                  <p>
                    {signal.signal_reason}
                  </p>
                </div>

                <dl className="signal-values">
                  <div>
                    <dt>
                      Observado
                    </dt>

                    <dd>
                      {signal.record_count.toLocaleString(
                        "pt-BR",
                      )}
                    </dd>
                  </div>

                  <div>
                    <dt>
                      Mediana histórica
                    </dt>

                    <dd>
                      {signal.historical_median.toLocaleString(
                        "pt-BR",
                      )}
                    </dd>
                  </div>

                  <div>
                    <dt>
                      Q75
                    </dt>

                    <dd>
                      {signal.q75.toLocaleString(
                        "pt-BR",
                      )}
                    </dd>
                  </div>

                  <div>
                    <dt>
                      Razão
                    </dt>

                    <dd>
                      {signal.ratio_to_median.toLocaleString(
                        "pt-BR",
                        {
                          minimumFractionDigits: 2,
                          maximumFractionDigits: 2,
                        },
                      )}
                      ×
                    </dd>
                  </div>
                </dl>
              </article>
            ))}
          </div>
        )}
        </section>

        <section
          className="panel operational-panel"
          aria-labelledby="operational-title"
        >
          <div className="panel-heading">
            <div>
              <p className="eyebrow">
                Situação operacional
              </p>

              <h2 id="operational-title">
                Estado do monitoramento
              </h2>
            </div>
          </div>

        <article className="card operational-card">
          <div className="operational-header">
            <div>
              <span className="operational-label">
                Estado operacional
              </span>

              {currentOperationalState ? (
                <strong
                  className={`operational-state operational-state-${currentOperationalState.toLowerCase()}`}
                >
                  {currentOperationalState}
                </strong>
              ) : (
                <strong className="operational-state operational-state-unavailable">
                  —
                </strong>
              )}
            </div>

            {currentOperationalState && (
              <span className="operational-current-week">
                Situação atual do período analisado
              </span>
            )}
          </div>

          {currentOperationalState ? (
            <div className="operational-history">
              {firstSignalWeek && (
                <div className="operational-history-item">
                  <span>Primeiro sinal</span>

                  <strong>
                    SE {firstSignalWeek.epi_week}
                  </strong>
                </div>
              )}

              {firstAlertWeek && (
                <div className="operational-history-item">
                  <span>Início do alerta</span>

                  <strong>
                    SE {firstAlertWeek.epi_week}
                  </strong>
                </div>
              )}

              <div className="operational-history-item">
                <span>Semana atual:</span>

                <strong>
                  {currentOperationalState}
                </strong>
              </div>

               {currentOperationalState === "PENDING" &&
                  lastStableState && (
                    <div className="operational-history-item">
                      <span>Último estado estável</span>

                      <strong>
                        {lastStableState}
                      </strong>
                    </div>
                )}
            </div>
          ) : (
            <p className="operational-unavailable-message">
              Análise operacional indisponível para este período.
            </p>
          )}

          {currentOperationalState === "PENDING" && (
            <p className="operational-pending-message">
              A semana mais recente ainda não atingiu maturidade suficiente
              para avaliação operacional.
            </p>
          )}

          {firstNowcastSignal && (
            <div
              className="nowcast-summary"
              aria-label="Resumo do nowcast"
            >
              <div>
                <span>
                  Primeiro sinal com nowcasting
                </span>

                <strong>
                  SE {firstNowcastSignal.epi_week}
                </strong>
              </div>

              <div>
                <span>Defasagem</span>

                <strong>
                  D+{firstNowcastSignal.lag_days}
                </strong>
              </div>

              <div>
                <span>Casos conhecidos</span>

                <strong>
                  {firstNowcastSignal.known_cases.toLocaleString(
                    "pt-BR",
                  )}
                </strong>
              </div>

              <div>
                <span>Estimativa</span>

                <strong>
                  {firstNowcastSignal.nowcast.toLocaleString(
                    "pt-BR",
                    {
                      maximumFractionDigits: 1,
                    },
                  )}
                </strong>
              </div>
            </div>
          )}
        </article>

        <div className="operational-explanation">
          <span>
            <strong>NORMAL:</strong> sem alerta ativo no período atual.
          </span>

          <span>
            <strong>SIGNAL:</strong> uma semana madura acima dos limiares.
          </span>

          <span>
            <strong>ALERT:</strong> duas semanas consecutivas com sinal maduro.
          </span>

          <span>
            <strong>PENDING:</strong> semana mais recente ainda sem dados maduros para classificação operacional
          </span>
        </div>
      </section>

      <section className="panel limitations">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">
              Sobre os dados
            </p>

            <h2>
              Limitações
            </h2>
          </div>
        </div>

        <ul>
          {metadata.limitations.map((limitation) => (
            <li key={limitation}>
              {limitation}
            </li>
          ))}
        </ul>
      </section>
    </main>
  );
}

function App() {
  const optionsQuery = useQuery({
    queryKey: ["options"],
    queryFn: () =>
      apiGet<OptionsResponse>("/api/options"),
  });

  if (optionsQuery.isPending) {
    return <DashboardLoading />;
  }

  if (optionsQuery.isError) {
    return (
      <main className="dashboard">
        <DashboardState
          title="Não foi possível carregar o painel"
          description="Não foi possível consultar as opções disponíveis."
          action={{
            label: "Tentar novamente",
            onClick: () => {
              void optionsQuery.refetch();
            },
          }}
        />
      </main>
    );
  }

  const options = optionsQuery.data;

  if (
    options.regions.length === 0 ||
    options.regions.every(
      (region) => region.years.length === 0,
    )
  ) {
    return (
      <main className="dashboard">
        <DashboardState
          title="Nenhum conjunto de dados disponível"
          description="Não existem regiões e anos disponíveis para consulta."
        />
      </main>
    );
  }

  return (
    <Dashboard options={options} />
  );
}

export default App;
