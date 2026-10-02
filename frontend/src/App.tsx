import { useQuery } from "@tanstack/react-query";

import { apiGet } from "./services/api";
import type {
  MetadataResponse,
  SignalResponse,
  TrendResponse,
} from "./types/api";

import { TrendChart } from "./components/trend-chart";

function App() {
  const region = "MG"
  const year = 2026;

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
    metadataQuery.isPending ||
    trendsQuery.isPending ||
    signalsQuery.isPending
  ) {
    return (
      <main className="dashboard">
        <p>Carregando dados...</p>
      </main>
    );
  }

  if (
    metadataQuery.isError ||
    trendsQuery.isError ||
    signalsQuery.isError
  ) {
    return (
      <main className="dashboard">
        <p>Não foi possível carregar os dados.</p>
      </main>
    );
  }

  const metadata = metadataQuery.data;
  const trends = trendsQuery.data;
  const signals = signalsQuery.data;

  const totalRecords = trends.weeks.reduce(
    (total, week) => total + week.record_count,
    0,
  );

  return (
    <main className="dashboard">
      <header className="page-header">
        <div>
          <p className="eyebrow">Vigilância epidemiológica</p>
          <h1>Sentinela</h1>
          <p className="subtitle">
            Monitoramento de SRAG em Minas Gerais
          </p>
        </div>

        <div className="source">
          <span>Fonte</span>
          <strong>{metadata.source}</strong>
          <small>
            Dados observados até {metadata.observed_through}
          </small>
        </div>
      </header>

      <section
        className="filters"
        aria-label="Filtros do painel"
      >
        <label>
          Região
          <select value={region} disabled>
            <option value="MG">Minas Gerais</option>
          </select>
        </label>

        <label>
          Ano
          <select value={year} disabled>
            <option value={2026}>2026</option>
          </select>
        </label>
      </section>

      <section
        className="indicadores"
        aria-label="Indicadores principais"
      >
        <article className="card">
          <span>Registros observados</span>
          <strong>{totalRecords.toLocaleString("pt-BR")}</strong>
          <small>SRAG em residentes de MG</small>
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
        />
      </section>

      <section
        id="signals" 
        className="panel"
        aria-label="signals-title"
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