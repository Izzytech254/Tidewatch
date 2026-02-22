import { useState, useEffect, useCallback } from "react";
import MapView from "./components/MapView";
import RiskDisplay from "./components/RiskDisplay";
import TideChart from "./components/TideChart";
import WeatherCard from "./components/WeatherCard";
import AlertForm from "./components/AlertForm";
import { assessRisk, getSampleLocations } from "./services/api";

const SAMPLE_LOCATIONS = [
  {
    name: "Ghent",
    address: "Ghent, Norfolk, VA",
    latitude: 36.8695,
    longitude: -76.296,
  },
  {
    name: "Larchmont",
    address: "Larchmont, Norfolk, VA",
    latitude: 36.876,
    longitude: -76.289,
  },
  {
    name: "Downtown",
    address: "Downtown Norfolk, VA",
    latitude: 36.8468,
    longitude: -76.2852,
  },
  {
    name: "Ocean View",
    address: "Ocean View, Norfolk, VA",
    latitude: 36.926,
    longitude: -76.253,
  },
  {
    name: "757 Studios",
    address: "Assembly, Norfolk, VA",
    latitude: 36.8562,
    longitude: -76.259,
  },
];

function useTheme() {
  const [theme, setTheme] = useState(() => {
    const saved = localStorage.getItem("tidewatch-theme");
    return saved || "dark";
  });

  useEffect(() => {
    document.documentElement.setAttribute("data-theme", theme);
    localStorage.setItem("tidewatch-theme", theme);
  }, [theme]);

  const toggleTheme = useCallback(() => {
    setTheme((prev) => (prev === "dark" ? "light" : "dark"));
  }, []);

  return { theme, toggleTheme };
}

export default function App() {
  const { theme, toggleTheme } = useTheme();
  const [assessment, setAssessment] = useState(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [searchAddress, setSearchAddress] = useState("");

  const handleAssess = async (address, lat, lng) => {
    setLoading(true);
    setError("");
    setSearchAddress(address);
    try {
      const result = await assessRisk(address, lat, lng);
      setAssessment(result);
    } catch (err) {
      setError(err.message);
    } finally {
      setLoading(false);
    }
  };

  const handleMapClick = (lat, lng) => {
    handleAssess(`${lat.toFixed(4)}, ${lng.toFixed(4)}`, lat, lng);
  };

  const handleSearch = (e) => {
    e.preventDefault();
    // For hackathon: use a default Norfolk location if no geocoding
    // In production, this would use a geocoding API
    if (searchAddress.trim()) {
      handleAssess(searchAddress, 36.8508, -76.2859);
    }
  };

  return (
    <>
      {/* Animated Background */}
      <div className="bg-animation">
        <div className="bg-image" />
        <div className="bg-image-overlay" />
        <div className="bg-orb bg-orb-1" />
        <div className="bg-orb bg-orb-2" />
        <div className="bg-orb bg-orb-3" />
        <div className="wave-line" />
        <div className="wave-line" />
        <div className="wave-line" />
        <div className="wave-line" />
      </div>

      {/* Header */}
      <header className="header">
        <div className="header-brand">
          <span className="wave-icon">🌊</span>
          <h1>TideWatch</h1>
        </div>
        <span className="header-tagline">
          Know your flood risk before the water knows your address
        </span>
        <div style={{ display: "flex", alignItems: "center", gap: 16 }}>
          <div className="theme-toggle">
            <button
              className="theme-toggle-btn"
              onClick={toggleTheme}
              aria-label="Toggle theme"
              title={
                theme === "dark"
                  ? "Switch to light mode"
                  : "Switch to dark mode"
              }
            >
              <span className="toggle-thumb">
                {theme === "dark" ? "🌙" : "☀️"}
              </span>
            </button>
          </div>
          <div className="header-live-badge">
            <span className="live-dot" />
            LIVE DATA
          </div>
        </div>
      </header>

      {/* Main Layout */}
      <div className="main-layout">
        {/* Sidebar */}
        <aside className="sidebar">
          {/* Search */}
          <div className="card">
            <div className="card-header">
              <h3>
                <span className="card-icon">📍</span> Check a Location
              </h3>
            </div>
            <form className="search-box" onSubmit={handleSearch}>
              <input
                type="text"
                placeholder="Enter address or click map..."
                value={searchAddress}
                onChange={(e) => setSearchAddress(e.target.value)}
              />
              <button
                className="btn btn-primary"
                type="submit"
                disabled={loading}
              >
                {loading ? "..." : "Assess"}
              </button>
            </form>

            <div className="quick-locations">
              {SAMPLE_LOCATIONS.map((loc) => (
                <button
                  key={loc.name}
                  className="location-chip"
                  onClick={() =>
                    handleAssess(loc.address, loc.latitude, loc.longitude)
                  }
                  disabled={loading}
                >
                  {loc.name}
                </button>
              ))}
            </div>
          </div>

          {/* Error */}
          {error && (
            <div className="card" style={{ borderColor: "var(--grade-f)" }}>
              <p style={{ color: "var(--grade-f)", fontSize: "0.85rem" }}>
                ⚠️ {error}
              </p>
            </div>
          )}

          {/* Loading */}
          {loading && (
            <div className="loading">
              <div className="spinner" />
              <span className="loading-text">Analyzing flood risk...</span>
            </div>
          )}

          {/* Risk Score */}
          {!loading && assessment && <RiskDisplay risk={assessment.risk} />}

          {/* Live Stats */}
          {!loading && assessment && (
            <div className="card">
              <div className="card-header">
                <h3>
                  <span className="card-icon">📊</span> Live Conditions
                </h3>
              </div>
              <div className="stat-row">
                <div className="stat-mini">
                  <div className="stat-value">
                    {assessment.tide?.current?.water_level_ft?.toFixed(1) ||
                      "—"}{" "}
                    ft
                  </div>
                  <div className="stat-label">Water Level</div>
                </div>
                <div className="stat-mini">
                  <div className="stat-value">
                    {assessment.elevation?.elevation_ft?.toFixed(0) || "—"} ft
                  </div>
                  <div className="stat-label">Elevation</div>
                </div>
                <div className="stat-mini">
                  <div className="stat-value">
                    {assessment.weather?.wind_speed_mph || "—"} mph
                  </div>
                  <div className="stat-label">Wind</div>
                </div>
              </div>
            </div>
          )}

          {/* Tide Chart */}
          {!loading && assessment?.tide && <TideChart tide={assessment.tide} />}

          {/* Weather */}
          {!loading && assessment?.weather && (
            <WeatherCard weather={assessment.weather} />
          )}

          {/* Alerts */}
          {!loading && <AlertForm assessment={assessment} />}

          {/* Empty State */}
          {!loading && !assessment && !error && (
            <div className="empty-state">
              <div className="empty-illustration">🌊</div>
              <h4>Welcome to TideWatch</h4>
              <p>
                Select a neighborhood above or click anywhere on the map to get
                a real-time flood risk assessment.
              </p>
              <div
                className="data-sources"
                style={{ justifyContent: "center", marginTop: 16 }}
              >
                <span className="source-badge">🌐 NOAA Tides</span>
                <span className="source-badge">⛅ NWS Weather</span>
                <span className="source-badge">🏔️ USGS Elevation</span>
              </div>
            </div>
          )}
        </aside>

        {/* Map */}
        <div className="map-container">
          <MapView
            assessment={assessment}
            onMapClick={handleMapClick}
            theme={theme}
          />
          <div className="map-vignette" />
          <div className="map-info-overlay">
            <div className="map-info-badge">
              <span className="badge-dot" />
              Norfolk, VA — Real-time Monitoring
            </div>
          </div>
        </div>
      </div>
    </>
  );
}
