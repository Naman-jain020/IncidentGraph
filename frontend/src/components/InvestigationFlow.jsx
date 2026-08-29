import { CheckCircle2, Circle, LoaderCircle } from "lucide-react";

const NODE_LABELS = {
  incident_trigger: "Incident Trigger",
  reasoning: "LLM Reasoning",
  latentgraph: "LatentGraph",
  github: "GitHub",
  observability: "Observability",
  aws_infra: "AWS / Infrastructure",
  incident_history: "Incident History",
  rca: "RCA Generation",
};

function InvestigationFlow({ history, status }) {
  const latestNode =
    history.length > 0 ? history[history.length - 1]?.node : null;

  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Investigation Flow</h2>
          <p>How the agent investigated the incident.</p>
        </div>

        <span className="status-pill">{status || "investigating"}</span>
      </div>

      <div className="flow">
        {history.length === 0 ? (
          <div className="flow-empty">Waiting for investigation steps...</div>
        ) : (
          history.map((item, index) => {
            const isLast = index === history.length - 1;

            return (
              <div className="flow-step" key={`${item.step || index}-${index}`}>
                <div className="flow-icon">
                  {isLast && status === "investigating" ? (
                    <LoaderCircle size={18} className="spin" />
                  ) : (
                    <CheckCircle2 size={18} />
                  )}
                </div>

                <div className="flow-content">
                  <strong>{NODE_LABELS[item.node] || item.node}</strong>

                  {item.reason && <span>{item.reason}</span>}

                  {item.query && <code>{item.query}</code>}
                </div>
              </div>
            );
          })
        )}
      </div>
    </section>
  );
}

export default InvestigationFlow;
