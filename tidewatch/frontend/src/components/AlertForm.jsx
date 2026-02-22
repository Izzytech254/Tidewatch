import { useState } from "react";
import { subscribeAlerts } from "../services/api";

export default function AlertForm({ assessment }) {
  const [phone, setPhone] = useState("");
  const [threshold, setThreshold] = useState("C");
  const [loading, setLoading] = useState(false);
  const [success, setSuccess] = useState(false);
  const [error, setError] = useState("");

  const handleSubmit = async (e) => {
    e.preventDefault();
    if (!phone || !assessment) return;

    setLoading(true);
    setError("");
    try {
      await subscribeAlerts(
        phone,
        assessment.address,
        assessment.latitude,
        assessment.longitude,
        threshold,
      );
      setSuccess(true);
      setPhone("");
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  if (!assessment) {
    return (
      <div className="card">
        <div className="card-header">
          <h3>
            <span className="card-icon">🔔</span> SMS Alerts
          </h3>
        </div>
        <p style={{ fontSize: "0.85rem", color: "var(--text-secondary)" }}>
          Assess a location first to set up alerts.
        </p>
      </div>
    );
  }

  return (
    <div className="card">
      <div className="card-header">
        <h3>
          <span className="card-icon">🔔</span> SMS Flood Alerts
        </h3>
      </div>

      {success ? (
        <div className="alert-success">
          ✅ Subscribed! You'll receive alerts for {assessment.address} when
          risk reaches grade {threshold} or higher.
        </div>
      ) : (
        <form className="alert-form" onSubmit={handleSubmit}>
          <input
            type="tel"
            placeholder="Phone number (+1...)"
            value={phone}
            onChange={(e) => setPhone(e.target.value)}
            required
          />
          <select
            value={threshold}
            onChange={(e) => setThreshold(e.target.value)}
          >
            <option value="B">Alert at Grade B (Minor) or worse</option>
            <option value="C">Alert at Grade C (Moderate) or worse</option>
            <option value="D">Alert at Grade D (High) or worse</option>
            <option value="F">Alert at Grade F (Severe) only</option>
          </select>
          <button className="btn btn-primary" type="submit" disabled={loading}>
            {loading ? "Subscribing..." : "Subscribe to Alerts"}
          </button>
          {error && (
            <p style={{ color: "var(--grade-f)", fontSize: "0.85rem" }}>
              {error}
            </p>
          )}
        </form>
      )}
    </div>
  );
}
