import {
  AlertTriangle,
  CheckCircle2,
  Lightbulb,
  ShieldAlert,
} from "lucide-react";

function RCAPanel({ rca, confidence }) {
  if (!rca) {
    return (
      <section className="panel rca-panel">
        <div className="panel-header">
          <div>
            <h2>Root Cause Analysis</h2>
            <p>Final RCA will appear when the investigation is complete.</p>
          </div>
        </div>

        <div className="panel-empty">
          <ShieldAlert size={28} />
          Investigation in progress...
        </div>
      </section>
    );
  }

  const confidenceValue =
    Number(rca.confidence ?? Number(confidence) * 100) || 0;

  return (
    <section className="panel rca-panel">
      <div className="panel-header">
        <div>
          <h2>Root Cause Analysis</h2>
          <p>Evidence-backed investigation result.</p>
        </div>

        <div className="confidence">
          <span>Confidence</span>
          <strong>{Math.round(confidenceValue)}%</strong>
        </div>
      </div>

      <div className="rca-root-cause">
        <div className="rca-section-icon">
          <AlertTriangle size={20} />
        </div>

        <div>
          <h3>Root Cause</h3>
          <p>{rca.root_cause || "Root cause could not be determined."}</p>
        </div>
      </div>

      <RCAList
        title="Evidence"
        icon={<CheckCircle2 size={18} />}
        items={rca.evidence}
      />

      <RCAList
        title="Timeline"
        icon={<CheckCircle2 size={18} />}
        items={rca.timeline}
      />

      <RCAList
        title="Recommended Fix"
        icon={<Lightbulb size={18} />}
        items={rca.recommended_fix}
      />
    </section>
  );
}

function RCAList({ title, icon, items }) {
  if (!Array.isArray(items) || items.length === 0) {
    return null;
  }

  return (
    <div className="rca-list-section">
      <div className="rca-list-title">
        {icon}
        <h3>{title}</h3>
      </div>

      <ul>
        {items.map((item, index) => (
          <li key={index}>{item}</li>
        ))}
      </ul>
    </div>
  );
}

export default RCAPanel;
