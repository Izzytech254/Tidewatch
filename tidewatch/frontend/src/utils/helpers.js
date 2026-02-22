export function getGradeColor(grade) {
  const colors = {
    A: "#22c55e",
    B: "#84cc16",
    C: "#eab308",
    D: "#f97316",
    F: "#ef4444",
  };
  return colors[grade] || "#8b97b0";
}

export function getGradeLabel(grade) {
  const labels = {
    A: "Low Risk",
    B: "Minor Risk",
    C: "Moderate Risk",
    D: "High Risk",
    F: "Severe Risk",
  };
  return labels[grade] || "Unknown";
}

export function formatTimestamp(ts) {
  return new Date(ts).toLocaleString("en-US", {
    month: "short",
    day: "numeric",
    hour: "numeric",
    minute: "2-digit",
  });
}
