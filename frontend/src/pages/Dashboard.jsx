import {
  Activity,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  RefreshCw,
} from "lucide-react";

import IncidentCard from "../components/IncidentCard";

function Dashboard({ incidents, loading, error, onRefresh, onOpenIncident }) {
  const activeIncidents = incidents.filter(
    (incident) =>
      incident.status === "investigating" || incident.status === "active"
  );

  const criticalIncidents = incidents.filter(
    (incident) => incident.severity === "critical"
  );

  return (
    <div className="page">
      <header className="topbar">
        <div>
          <div className="brand">IncidentGraph</div>

          <div className="subtitle">AI-powered incident investigation</div>
        </div>

        <button
          className="secondary-button"
          onClick={onRefresh}
          disabled={loading}
        >
          <RefreshCw size={16} />
          Refresh
        </button>
      </header>

      <main className="content">
        <section className="stats-grid">
          <StatCard
            icon={<Activity size={20} />}
            title="Active Incidents"
            value={activeIncidents.length}
          />

          <StatCard
            icon={<AlertCircle size={20} />}
            title="Critical"
            value={criticalIncidents.length}
          />

          <StatCard
            icon={<CheckCircle2 size={20} />}
            title="Resolved"
            value={
              incidents.filter(
                (incident) =>
                  incident.status === "completed" ||
                  incident.status === "resolved"
              ).length
            }
          />
        </section>

        <section className="section">
          <div className="section-header">
            <div>
              <h1>Recent Incidents</h1>
              <p>Production incidents investigated by IncidentGraph.</p>
            </div>
          </div>

          {error && (
            <div className="error-banner">
              <AlertTriangle size={18} />
              {error}
            </div>
          )}

          {loading ? (
            <div className="empty-state">Loading incidents...</div>
          ) : incidents.length === 0 ? (
            <div className="empty-state">
              <Activity size={32} />
              <h3>No incidents yet</h3>
              <p>
                Trigger an incident from the API or connect a CloudWatch
                webhook.
              </p>
            </div>
          ) : (
            <div className="incident-list">
              {incidents.map((incident) => (
                <IncidentCard
                  key={incident.incident_id || incident.id}
                  incident={incident}
                  onClick={() =>
                    onOpenIncident(incident.incident_id || incident.id)
                  }
                />
              ))}
            </div>
          )}
        </section>
      </main>
    </div>
  );
}

function StatCard({ icon, title, value }) {
  return (
    <div className="stat-card">
      <div className="stat-icon">{icon}</div>

      <div>
        <div className="stat-title">{title}</div>

        <div className="stat-value">{value}</div>
      </div>
    </div>
  );
}

export default Dashboard;
