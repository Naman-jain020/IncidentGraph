import { useState } from "react";
import { analyzeRepository, createIncident } from "../services/api";

export default function RepoOnboardingWizard({ onComplete }) {
  const [step, setStep] = useState(1);
  const [repo, setRepo] = useState("");
  const [loading, setLoading] = useState(false);
  const [analysis, setAnalysis] = useState(null);
  const [userConfigs, setUserConfigs] = useState({});

  async function handleAnalyzeRepo(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const data = await analyzeRepository(repo);
      setAnalysis(data);
      setStep(2);
    } catch (err) {
      alert("Error analyzing repository: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  function handleConfigChange(field, value) {
    setUserConfigs((prev) => ({ ...prev, [field]: value }));
  }

  async function handleStartGraph(e) {
    e.preventDefault();
    setLoading(true);
    try {
      const payload = {
        repository: repo,
        service: repo.split("/")[1] || repo,
        problem: "Initial indexing and root cause setup",
        ...userConfigs,
      };
      const result = await createIncident(payload);
      onComplete(result);
    } catch (err) {
      alert("Error starting graph: " + err.message);
    } finally {
      setLoading(false);
    }
  }

  return (
    <div className="wizard-card p-6 bg-white rounded-lg shadow-md max-w-xl mx-auto">
      {step === 1 && (
        <form onSubmit={handleAnalyzeRepo} className="space-y-4">
          <h2 className="text-xl font-bold">1. Connect GitHub Repository</h2>
          <div>
            <label className="block text-sm font-medium mb-1">
              Repository Name (owner/repo)
            </label>
            <input
              type="text"
              className="w-full border p-2 rounded"
              placeholder="e.g. myorg/payments-service"
              value={repo}
              onChange={(e) => setRepo(e.target.value)}
              required
            />
          </div>
          <button
            type="submit"
            disabled={loading}
            className="bg-blue-600 text-white px-4 py-2 rounded"
          >
            {loading
              ? "Analyzing Repository..."
              : "Analyze & Detect Configurations"}
          </button>
        </form>
      )}

      {step === 2 && analysis && (
        <form onSubmit={handleStartGraph} className="space-y-6">
          <h2 className="text-xl font-bold">
            2. Configure Integrations & Roles
          </h2>

          {analysis.detected_configs.length > 0 && (
            <div className="bg-blue-50 p-3 rounded">
              <p className="font-semibold text-blue-900 mb-1">
                Detected Infrastructure & Tools:
              </p>
              <ul className="list-disc pl-5 text-sm text-blue-800">
                {analysis.detected_configs.map((c, i) => (
                  <li key={i}>{c.name}</li>
                ))}
              </ul>
            </div>
          )}

          {analysis.required_user_inputs.map((section, idx) => (
            <div key={idx} className="border-t pt-4">
              <h3 className="font-semibold text-md mb-2">{section.title}</h3>
              {section.fields.map((field) => (
                <div key={field.name} className="mb-3">
                  <label className="block text-sm mb-1">{field.label}</label>
                  <input
                    type="text"
                    className="w-full border p-2 rounded"
                    placeholder={field.placeholder || ""}
                    onChange={(e) =>
                      handleConfigChange(field.name, e.target.value)
                    }
                  />
                </div>
              ))}
            </div>
          ))}

          <div className="flex gap-3">
            <button
              type="button"
              onClick={() => setStep(1)}
              className="border px-4 py-2 rounded"
            >
              Back
            </button>
            <button
              type="submit"
              disabled={loading}
              className="bg-green-600 text-white px-4 py-2 rounded"
            >
              {loading
                ? "Initializing Incident Graph..."
                : "Connect & Generate Graph"}
            </button>
          </div>
        </form>
      )}
    </div>
  );
}
