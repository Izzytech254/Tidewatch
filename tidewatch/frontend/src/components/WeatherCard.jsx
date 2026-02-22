function getWeatherIcon(forecast) {
  const f = (forecast || "").toLowerCase();
  if (f.includes("thunder") || f.includes("storm")) return "⛈️";
  if (f.includes("rain") || f.includes("shower")) return "🌧️";
  if (f.includes("snow") || f.includes("sleet")) return "🌨️";
  if (f.includes("cloud") || f.includes("overcast")) return "☁️";
  if (f.includes("fog") || f.includes("mist")) return "🌫️";
  if (f.includes("partly")) return "⛅";
  if (f.includes("wind")) return "💨";
  if (f.includes("night") || f.includes("clear")) return "🌙";
  return "☀️";
}

export default function WeatherCard({ weather }) {
  if (!weather || !weather.periods || weather.periods.length === 0) return null;

  return (
    <div className="card">
      <div className="card-header">
        <h3>
          <span className="card-icon">⛅</span> Weather Forecast
        </h3>
        <span style={{ fontSize: "0.8rem", color: "var(--text-secondary)" }}>
          💨 {weather.wind_speed_mph} mph {weather.wind_direction}
        </span>
      </div>

      <div className="weather-strip">
        {weather.periods.slice(0, 5).map((period, i) => (
          <div className="weather-period" key={i}>
            <div className="period-icon">
              {getWeatherIcon(period.short_forecast)}
            </div>
            <div className="period-name">{period.name}</div>
            <div className="period-temp">{period.temperature}°</div>
            <div className="period-forecast">{period.short_forecast}</div>
            {period.precipitation_chance > 0 && (
              <div className="period-rain">
                💧 {period.precipitation_chance}%
              </div>
            )}
          </div>
        ))}
      </div>

      {weather.precipitation_forecast_in > 0 && (
        <div
          style={{
            marginTop: 12,
            fontSize: "0.8rem",
            color: "var(--accent-cyan)",
            display: "flex",
            alignItems: "center",
            gap: 6,
          }}
        >
          🌧️ Expected rainfall: ~{weather.precipitation_forecast_in}" in next
          24h
        </div>
      )}
    </div>
  );
}
