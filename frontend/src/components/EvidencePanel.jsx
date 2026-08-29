import {
  Database,
  FileCode2,
  Github,
  Server,
  Activity,
  Search,
} from "lucide-react";

const SOURCE_ICONS = {
  latentgraph: FileCode2,
  github: Github,
  aws: Server,
  observability: Activity,
  incident_history: Search,
};

function EvidencePanel({ evidence }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Evidence</h2>
          <p>Findings collected during the investigation.</p>
        </div>
      </div>

      {evidence.length === 0 ? (
        <div className="panel-empty">No evidence collected yet.</div>
      ) : (
        <div className="evidence-list">
          {evidence.map((item, index) => {
            const Icon = SOURCE_ICONS[item.source] || Database;

            return (
              <div className="evidence-item" key={index}>
                <div className="evidence-icon">
                  <Icon size={18} />
                </div>

                <div className="evidence-content">
                  <div className="evidence-title">
                    <strong>{item.source || "Unknown source"}</strong>

                    <span>{item.type || "finding"}</span>
                  </div>

                  <pre>{formatEvidence(item.data || item.finding || item)}</pre>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

function formatEvidence(value) {
  if (typeof value === "string") {
    return value;
  }

  try {
    return JSON.stringify(value, null, 2);
  } catch {
    return String(value);
  }
}

export default EvidencePanel;
