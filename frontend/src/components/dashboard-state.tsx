interface DashboardStateProps {
    title: string;
    description: string;
    action?: {
        label: string;
        onClick: () => void;
    };
}

export function DashboardState({
    title,
    description,
    action,
}: DashboardStateProps) {
    return (
        <div
            className="dashboard-state"
            role="status"
            aria-live="polite"
        >
            <h2>{title}</h2>
            <p>{description}</p>

            {action && (
                <button
                    type="button"
                    onClick={action.onClick}
                >
                    {action.label}
                </button>
            )}
        </div>
    );
}

export function DashboardLoading() {
    return (
        <main
            className="dashboard"
            aria-busy="true"
            aria-label="Carregando painel"
        >
            <div className="loading-header">
                <div className="skeleton skeleton-title" />
                <div className="skeleton skeleton-subtitle" />
            </div>

            <div className="loading-filters skeleton" />

            <div className="loading-cards">
                <div className="skeleton loading-card" />
                <div className="skeleton loading-card" />
                <div className="skeleton loading-card" />
            </div>

            <div className="skeleton loading-chart" />

            <span className="sr-only">
                Carregando dados epidemiológicos.
            </span>
        </main>
    );
}
