import { getGradeColor, getGradeLabel } from "../utils/helpers";

export default function RiskDisplay({ risk }) {
  if (!risk) return null;

  const color = getGradeColor(risk.grade);

  return (
    <div className="card">
      <div className="card-header">
        <h3>
          <span className="card-icon">🛡️</span> Flood Risk Score
        </h3>
        <span style={{ color, fontWeight: 700, fontSize: "0.85rem" }}>
          {getGradeLabel(risk.grade)}
        </span>
      </div>

      <div className="risk-display">
        <div className="risk-grade-ring" style={{ "--ring-color": color }}>
          <div className={`risk-grade grade-${risk.grade}`}>{risk.grade}</div>
        </div>
        <div className="risk-score-num">{risk.score} / 100</div>
        <div className="risk-summary">{risk.summary}</div>

        <div className="confidence-bar">
          <span>Confidence</span>
          <div className="confidence-track">
            <div
              className="confidence-fill"
              style={{ width: `${risk.confidence * 100}%` }}
            />
          </div>
          <span>{Math.round(risk.confidence * 100)}%</span>
        </div>
      </div>

      {/* Factor breakdown */}
      <div style={{ marginTop: 16 }}>
        <div className="card-header">
          <h3>
            <span className="card-icon">📈</span> Risk Factors
          </h3>
        </div>
        <div className="factors-grid">
          <FactorBar
            icon="🌊"
            label="Tidal"
            value={risk.factors.tidal_factor}
            cls="tidal"
          />
          <FactorBar
            icon="⛰️"
            label="Elevation"
            value={risk.factors.elevation_factor}
            cls="elevation"
          />
          <FactorBar
            icon="🌧️"
            label="Rain"
            value={risk.factors.precipitation_factor}
            cls="precipitation"
          />
          <FactorBar
            icon="💨"
            label="Wind Surge"
            value={risk.factors.wind_surge_factor}
            cls="wind"
          />
        </div>
      </div>

      {/* Recommendations */}
      {risk.recommendations?.length > 0 && (
        <div style={{ marginTop: 16 }}>
          <div className="card-header">
            <h3>
              <span className="card-icon">💡</span> Recommendations
            </h3>
          </div>
          <ul className="recommendations-list">
            {risk.recommendations.map((rec, i) => (
              <li key={i}>
                <span className="rec-icon">→</span>
                {rec}
              </li>
            ))}
          </ul>
        </div>
      )}
    </div>
  );
}

function FactorBar({ icon, label, value, cls }) {
  return (
    <div className="factor-row">
      <span className="factor-icon">{icon}</span>
      <span className="factor-label">{label}</span>
      <div className="factor-bar-track">
        <div
          className={`factor-bar-fill ${cls}`}
          style={{ width: `${value * 100}%` }}
        />
      </div>
      <span className="factor-value">{(value * 100).toFixed(0)}%</span>
    </div>
  );
}
