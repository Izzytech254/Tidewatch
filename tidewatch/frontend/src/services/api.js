const API_BASE = import.meta.env.VITE_API_URL || "/api";

// Retry wrapper for Render cold-start (free tier spins down after inactivity)
async function fetchWithRetry(url, options = {}, retries = 3, delay = 3000) {
  for (let i = 0; i <= retries; i++) {
    try {
      const controller = new AbortController();
      const timeout = setTimeout(() => controller.abort(), 30000);
      const resp = await fetch(url, { ...options, signal: controller.signal });
      clearTimeout(timeout);
      return resp;
    } catch (err) {
      if (i === retries) throw new Error("Server is unavailable. It may be starting up — please try again in 30 seconds.");
      // Dispatch event so UI can show "waking up" message
      window.dispatchEvent(new CustomEvent("api-retry", { detail: { attempt: i + 1, max: retries } }));
      await new Promise((r) => setTimeout(r, delay));
    }
  }
}

export async function assessRisk(address, latitude, longitude) {
  const resp = await fetchWithRetry(`${API_BASE}/risk/assess`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ address, latitude, longitude }),
  });
  if (!resp.ok) {
    const err = await resp.json().catch(() => ({}));
    throw new Error(err.detail || "Failed to assess risk");
  }
  return resp.json();
}

export async function getSampleLocations() {
  const resp = await fetchWithRetry(`${API_BASE}/risk/sample`);
  return resp.json();
}

export async function getCurrentTides() {
  const resp = await fetchWithRetry(`${API_BASE}/tides/current`);
  return resp.json();
}

export async function getTidePredictions(hours = 48) {
  const resp = await fetchWithRetry(`${API_BASE}/tides/predictions?hours=${hours}`);
  return resp.json();
}

export async function getWeatherForecast() {
  const resp = await fetchWithRetry(`${API_BASE}/weather/forecast`);
  return resp.json();
}

export async function subscribeAlerts(
  phoneNumber,
  address,
  latitude,
  longitude,
  thresholdGrade = "C",
) {
  const resp = await fetchWithRetry(`${API_BASE}/alerts/subscribe`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({
      phone_number: phoneNumber,
      address,
      latitude,
      longitude,
      threshold_grade: thresholdGrade,
    }),
  });
  if (!resp.ok) throw new Error("Failed to subscribe");
  return resp.json();
}
