import {
  LineChart,
  Line,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  ReferenceLine,
  Area,
  AreaChart,
} from "recharts";

export default function TideChart({ tide }) {
  if (!tide || !tide.predictions || tide.predictions.length === 0) return null;

  const data = tide.predictions.map((p) => ({
    time: new Date(p.timestamp).toLocaleTimeString("en-US", {
      hour: "numeric",
      minute: "2-digit",
    }),
    level: p.prediction_ft,
  }));

  const currentLevel = tide.current?.water_level_ft;

  // Read theme from CSS custom property
  const isDark = getComputedStyle(document.documentElement)
    .getPropertyValue("--bg-primary")
    .trim()
    .startsWith("#0");

  const gridColor = isDark ? "#1e3054" : "#d1d9e6";
  const axisColor = isDark ? "#8b97b0" : "#5b6b82";
  const tooltipBg = isDark ? "#162040" : "#ffffff";
  const tooltipBorder = isDark ? "rgba(255,255,255,0.1)" : "rgba(0,0,0,0.08)";
  const tooltipText = isDark ? "#e8edf5" : "#1a2332";

  return (
    <div className="card">
      <div className="card-header">
        <h3>
          <span className="card-icon">🌊</span> Tide Predictions
        </h3>
        {currentLevel != null && (
          <span style={{ fontSize: "0.85rem", color: "var(--accent-blue)" }}>
            Now: {currentLevel.toFixed(2)} ft
          </span>
        )}
      </div>

      <div className="tide-chart-container">
        <ResponsiveContainer width="100%" height="100%">
          <AreaChart data={data.slice(0, 24)}>
            <defs>
              <linearGradient id="tideGradient" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3b82f6" stopOpacity={0.3} />
                <stop offset="95%" stopColor="#3b82f6" stopOpacity={0.02} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke={gridColor} />
            <XAxis
              dataKey="time"
              stroke={axisColor}
              fontSize={10}
              interval={3}
            />
            <YAxis stroke={axisColor} fontSize={10} unit=" ft" />
            <Tooltip
              contentStyle={{
                background: tooltipBg,
                border: `1px solid ${tooltipBorder}`,
                borderRadius: 12,
                color: tooltipText,
                backdropFilter: "blur(16px)",
                boxShadow: "0 8px 32px rgba(0,0,0,0.15)",
              }}
            />
            {currentLevel != null && (
              <ReferenceLine
                y={currentLevel}
                stroke="#ef4444"
                strokeDasharray="5 5"
                label={{ value: "Current", fill: "#ef4444", fontSize: 10 }}
              />
            )}
            <Area
              type="monotone"
              dataKey="level"
              stroke="#3b82f6"
              strokeWidth={2}
              fill="url(#tideGradient)"
              dot={false}
              activeDot={{
                r: 5,
                fill: "#06b6d4",
                stroke: "#fff",
                strokeWidth: 2,
              }}
            />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <div className="data-sources">
        <span className="source-badge">NOAA Sewells Point</span>
        <span className="source-badge">Station #8638610</span>
      </div>
    </div>
  );
}
