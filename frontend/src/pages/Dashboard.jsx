import { useState } from "react";
import {
  Activity,
  AlertCircle,
  AlertTriangle,
  CheckCircle2,
  PlusCircle,
  RefreshCw,
} from "lucide-react";

import IncidentCard from "../components/IncidentCard";
import RepoOnboardingWizard from "../components/RepoOnboardingWizard";

function Dashboard({ incidents, loading, error, onRefresh, onOpenIncident }) {
  const [showWizard, setShowWizard] = useState(false);

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

        <div className="flex gap-2">
          <button
            className="primary-button flex items-center gap-2 bg-blue-600 text-white px-3 py-1.5 rounded"
            onClick={() => setShowWizard(!showWizard)}
          >
            <PlusCircle size={16} />
            {showWizard ? "Close Onboarding" : "Connect Repo"}
          </button>

          <button
            className="secondary-button flex items-center gap-2 border px-3 py-1.5 rounded"
            onClick={onRefresh}
            disabled={loading}
          >
            <RefreshCw size={16} />
            Refresh
          </button>
        </div>
      </header>

      <main className="content space-y-6">
        {showWizard && (
          <section className="mb-6">
            <RepoOnboardingWizard
              onComplete={(result) => {
                setShowWizard(false);
                onRefresh();
                if (result?.incident?.incident_id) {
                  onOpenIncident(result.incident.incident_id);
                }
              }}
            />
          </section>
        )}

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
          ) : incidents.length === 0 && !showWizard ? (
            <div className="empty-state text-center p-8">
              <Activity size={32} className="mx-auto mb-2" />
              <h3>No incidents yet</h3>
              <p className="mb-4">
                Connect a repository and setup credentials to start an
                investigation graph.
              </p>
              <button
                className="bg-blue-600 text-white px-4 py-2 rounded"
                onClick={() => setShowWizard(true)}
              >
                Connect GitHub Repository
              </button>
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
