import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { apiGet } from "./services/api";
import type {
  MetadataResponse,
  SignalResponse,
  TrendResponse,
  OptionsResponse,
} from "./types/api";

import {
  DashboardLoading,
  DashboardState,
} from "./components/dashboard-state";

import { TrendChart } from "./components/trend-chart";

function App() {

  const [region, setRegion] = useState("MG");
  const [year, setYear] = useState(2026);

  const optionsQuery = useQuery({
    queryKey: ["options"],
    queryFn: () =>
      apiGet<OptionsResponse>("/api/options")
  });

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

  if (
    optionsQuery.isPending ||
    metadataQuery.isPending ||
    trendsQuery.isPending ||
    signalsQuery.isPending
  ) {
    return <DashboardLoading />;
  }

  if (
    optionsQuery.isError ||
    metadataQuery.isError ||
    trendsQuery.isError ||
    signalsQuery.isError
  ) {
    const handleRetry = () => {
      void Promise.all([
        optionsQuery.refetch(),
        metadataQuery.refetch(),
        trendsQuery.refetch(),
        signalsQuery.refetch(),
      ]);
    };

    return (
      <main className="dashboard">
        <DashboardState
          title="Não foi possível carregar o painel"
          description="Ocorreu um problema ao consultar os dados. Verifique a conexão e tente novamente."
          action={{
            label:"tentar novamente",
            onClick: handleRetry 
          }}
        />
      </main>
    )
  }

  const options = optionsQuery.data;
  const metadata = metadataQuery.data;
  const trends = trendsQuery.data;
  const signals = signalsQuery.data;

  if (trends.weeks.length ===0) {
    return (
      <main className="dashboard">
        <DashboardState 
          title="Nenhum dado disponivel"
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

  function formatDateTime(value: string) {
    return new Intl.DateTimeFormat("pt-BR", {
      dateStyle: "short",
      timeStyle: "short",
    }).format(new Date(value));
  }

  function formatDate(value: string) {
    const [year, month, day] = value.split("-")

    return `${day}/${month}/${year}`
  }

  return (
    <main
      className="dashboard"
      aria-labelledby="page-title"
    >
      <header className="page-header">
        <div>
          <p className="eyebrow">Vigilância epidemiológica</p>
          <h1 id="page-title">Sentinela</h1>
          <p className="subtitle">
            Monitoramento de SRAG em{" "}
            {selectedRegion?.label ?? region}
          </p>
        </div>

        <div className="source">
          <span>Fonte</span>

          <strong>{metadata.source}</strong>

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
              setRegion(event.target.value);
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
            {options.years.map((option) => (
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
          <span>Registros observados</span>
          <strong>{totalRecords.toLocaleString("pt-BR")}</strong>
          <small>SRAG em residentes de {region}</small>
        </article>

        <article className="card">
          <span>Última semana observada</span>
          <strong>SE {metadata.last_observed_week}</strong>
          <small>
            {metadata.observed_weeks} semanas disponíveis
          </small>
        </article>

        <article className="card">
          <span>Sinais identificados</span>
          <strong>{signals.signals.length}</strong>
          <small>Regra estatística do Sentinela</small>
        </article>
      </section>

      <section className="panel">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Série temporal</p>
            <h2>Evolução semanal de SRAG</h2>
          </div>

          <span>
            SE {metadata.first_observed_week}–
            {metadata.last_observed_week}
          </span>
        </div>

        <TrendChart 
          data={trends.weeks}
          signals={signals.signals}
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
              <p className="eyebrow">Monitoramento</p>

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
                      Semana epidemiológica {signal.epi_week}
                    </h3>

                    <p>{signal.signal_reason}</p>
                  </div>

                  <dl className="signal-values">
                    <div>
                      <dt>Observado</dt>
                      <dd>
                        {signal.record_count.toLocaleString(
                          "pt-BR",
                        )}
                      </dd>
                    </div>

                    <div>
                      <dt>Mediana histórica</dt>
                      <dd>
                        {signal.historical_median.toLocaleString(
                          "pt-BR",
                        )}
                      </dd>
                    </div>

                    <div>
                      <dt>Q75</dt>
                      <dd>
                        {signal.q75.toLocaleString("pt-BR")}
                      </dd>
                    </div>

                    <div>
                      <dt>Razão</dt>
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

      <section className="panel limitations">
        <div className="panel-heading">
          <div>
            <p className="eyebrow">Sobre os dados</p>
            <h2>Limitações</h2>
          </div>
        </div>

        <ul>
          {metadata.limitations.map((limitation) => (
            <li key={limitation}>{limitation}</li>
          ))}
        </ul>
      </section>
    </main>
  )
}

export default App;
