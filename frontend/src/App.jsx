import { useEffect, useState } from "react";

import Dashboard from "./pages/Dashboard";
import IncidentDetails from "./pages/IncidentDetails";

import { getIncident, listIncidents } from "./services/api";

function App() {
  const [page, setPage] = useState("dashboard");
  const [selectedIncidentId, setSelectedIncidentId] = useState(null);

  const [incidents, setIncidents] = useState([]);
  const [selectedIncident, setSelectedIncident] = useState(null);

  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  async function loadIncidents() {
    try {
      setLoading(true);
      setError(null);

      const data = await listIncidents();

      setIncidents(Array.isArray(data) ? data : data.incidents || []);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  }

  async function openIncident(incidentId) {
    try {
      setError(null);
      setSelectedIncidentId(incidentId);
      setPage("incident");

      const data = await getIncident(incidentId);

      setSelectedIncident(data);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    loadIncidents();
  }, []);

  function goToDashboard() {
    setPage("dashboard");
    setSelectedIncidentId(null);
    setSelectedIncident(null);
  }

  return (
    <div className="app-shell">
      {page === "dashboard" ? (
        <Dashboard
          incidents={incidents}
          loading={loading}
          error={error}
          onRefresh={loadIncidents}
          onOpenIncident={openIncident}
        />
      ) : (
        <IncidentDetails
          incidentId={selectedIncidentId}
          incident={selectedIncident}
          error={error}
          onBack={goToDashboard}
          onRefresh={() => openIncident(selectedIncidentId)}
        />
      )}
    </div>
  );
}

export default App;
