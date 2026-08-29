import { AlertCircle, Clock } from "lucide-react";

function IncidentCard({ incident, onClick }) {
  const severity = incident.severity || "unknown";

  const status = incident.status || "unknown";

  return (
    <button className="incident-card" onClick={onClick}>
      <div className="incident-card-main">
        <div className={`incident-status-dot ${severity}`} />

        <div>
          <h3>{incident.problem || "Production incident"}</h3>

          <p>{incident.service || "Unknown service"}</p>
        </div>
      </div>

      <div className="incident-card-meta">
        <span className={`severity-badge ${severity}`}>{severity}</span>

        <span className="status-text">{status}</span>

        {incident.created_at && (
          <span className="time-text">
            <Clock size={14} />
            {formatDate(incident.created_at)}
          </span>
        )}
      </div>
    </button>
  );
}

function formatDate(value) {
  const date = new Date(value);

  if (Number.isNaN(date.getTime())) {
    return value;
  }

  return date.toLocaleString();
}

export default IncidentCard;
