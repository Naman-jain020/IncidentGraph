const API_BASE_URL =
  import.meta.env.VITE_API_BASE_URL || "/api";

async function request(
  path,
  options = {}
) {
  const response = await fetch(
    `${API_BASE_URL}${path}`,
    {
      headers: {
        "Content-Type": "application/json",
        ...(options.headers || {}),
      },
      ...options,
    }
  );

  let data = null;

  try {
    data = await response.json();
  } catch {
    data = null;
  }

  if (!response.ok) {
    const message =
      data?.message ||
      data?.error ||
      `Request failed with status ${response.status}`;

    throw new Error(message);
  }

  return data;
}

export async function listIncidents() {
  /*
   * The backend list endpoint can be added when incident
   * history browsing is implemented. For the MVP, return
   * an empty list if it does not exist yet.
   */
  try {
    return await request("/incidents");
  } catch (error) {
    if (error.message.includes("404")) {
      return [];
    }

    throw error;
  }
}

export async function createIncident(
  incident
) {
  return request("/incidents", {
    method: "POST",
    body: JSON.stringify(incident),
  });
}

export async function getIncident(
  incidentId
) {
  return request(
    `/incidents/${encodeURIComponent(
      incidentId
    )}`
  );
}

export async function getHealth() {
  return request("/health");
}

export async function analyzeRepository(repository) {
  return request("/repos/analyze", {
    method: "POST",
    body: JSON.stringify({ repository }),
  });
}