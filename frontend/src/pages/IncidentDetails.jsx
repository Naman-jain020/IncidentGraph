import { ArrowLeft, AlertTriangle, RefreshCw } from "lucide-react";

import InvestigationFlow from "../components/InvestigationFlow";
import EvidencePanel from "../components/EvidencePanel";
import BlastRadius from "../components/BlastRadius";
import RCAPanel from "../components/RCAPanel";

function IncidentDetails({ incidentId, incident, error, onBack, onRefresh }) {
  if (!incident) {
    return (
      <div className="page">
        <header className="topbar">
          <button className="secondary-button" onClick={onBack}>
            <ArrowLeft size={16} />
            Back
          </button>

          <button className="secondary-button" onClick={onRefresh}>
            <RefreshCw size={16} />
            Refresh
          </button>
        </header>

        <main className="content">
          {error ? (
            <div className="error-banner">
              <AlertTriangle size={18} />
              {error}
            </div>
          ) : (
            <div className="empty-state">Loading incident...</div>
          )}
        </main>
      </div>
    );
  }

  const data = incident;
  const incidentData = data.incident || data;

  return (
    <div className="page">
      <header className="topbar">
        <button className="secondary-button" onClick={onBack}>
          <ArrowLeft size={16} />
          Incidents
        </button>

        <button className="secondary-button" onClick={onRefresh}>
          <RefreshCw size={16} />
          Refresh
        </button>
      </header>

      <main className="content">
        <section className="incident-header">
          <div>
            <div className="eyebrow">{incidentId}</div>

            <h1>{incidentData.problem || "Production Incident"}</h1>

            <p>
              Service: <strong>{incidentData.service || "Unknown"}</strong>
            </p>
          </div>

          <div
            className={`severity-badge ${incidentData.severity || "unknown"}`}
          >
            {incidentData.severity || "UNKNOWN"}
          </div>
        </section>

        <InvestigationFlow
          history={data.investigation_history || []}
          status={data.status}
        />

        <div className="two-column">
          <EvidencePanel evidence={data.evidence || []} />

          <BlastRadius components={data.affected_components || []} />
        </div>

        <RCAPanel rca={data.final_rca} confidence={data.confidence} />
      </main>
    </div>
  );
}

export default IncidentDetails;
