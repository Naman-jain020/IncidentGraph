import { AlertTriangle, Box, Network } from "lucide-react";

function BlastRadius({ components }) {
  return (
    <section className="panel">
      <div className="panel-header">
        <div>
          <h2>Blast Radius</h2>
          <p>Components potentially affected by the incident.</p>
        </div>
      </div>

      {components.length === 0 ? (
        <div className="panel-empty">
          No affected components identified yet.
        </div>
      ) : (
        <div className="blast-list">
          {components.map((component, index) => {
            const name =
              typeof component === "string"
                ? component
                : component.name || component.component_name || "Unknown";

            const impact =
              typeof component === "string"
                ? "potentially affected"
                : component.impact ||
                  component.impact_level ||
                  "potentially affected";

            return (
              <div className="blast-item" key={`${name}-${index}`}>
                <div className="blast-icon">
                  <Network size={18} />
                </div>

                <div>
                  <strong>{name}</strong>
                  <span>{impact}</span>
                </div>
              </div>
            );
          })}
        </div>
      )}
    </section>
  );
}

export default BlastRadius;
