const API_BASE = import.meta.env.VITE_API_URL || "/api";

export async function assessRisk(address, latitude, longitude) {
  const resp = await fetch(`${API_BASE}/risk/assess`, {
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
  const resp = await fetch(`${API_BASE}/risk/sample`);
  return resp.json();
}

export async function getCurrentTides() {
  const resp = await fetch(`${API_BASE}/tides/current`);
  return resp.json();
}

export async function getTidePredictions(hours = 48) {
  const resp = await fetch(`${API_BASE}/tides/predictions?hours=${hours}`);
  return resp.json();
}

export async function getWeatherForecast() {
  const resp = await fetch(`${API_BASE}/weather/forecast`);
  return resp.json();
}

export async function subscribeAlerts(
  phoneNumber,
  address,
  latitude,
  longitude,
  thresholdGrade = "C",
) {
  const resp = await fetch(`${API_BASE}/alerts/subscribe`, {
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
