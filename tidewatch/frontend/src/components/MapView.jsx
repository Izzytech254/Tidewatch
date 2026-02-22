import { useEffect, useRef } from "react";
import L from "leaflet";
import "leaflet/dist/leaflet.css";
import { getGradeColor } from "../utils/helpers";

const NORFOLK_CENTER = [36.8508, -76.2859];

const TILES = {
  dark: {
    url: "https://{s}.basemaps.cartocdn.com/dark_all/{z}/{x}/{y}{r}.png",
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
  },
  light: {
    url: "https://{s}.basemaps.cartocdn.com/light_all/{z}/{x}/{y}{r}.png",
    attribution:
      '&copy; <a href="https://www.openstreetmap.org/copyright">OpenStreetMap</a> &copy; <a href="https://carto.com/">CARTO</a>',
  },
};

export default function MapView({ assessment, onMapClick, theme = "dark" }) {
  const mapContainer = useRef(null);
  const map = useRef(null);
  const tileLayer = useRef(null);
  const marker = useRef(null);
  const pulseMarker = useRef(null);

  // Initialize map
  useEffect(() => {
    if (map.current) return;

    map.current = L.map(mapContainer.current, {
      center: NORFOLK_CENTER,
      zoom: 12,
      zoomControl: true,
      attributionControl: true,
    });

    const tiles = TILES[theme] || TILES.dark;
    tileLayer.current = L.tileLayer(tiles.url, {
      attribution: tiles.attribution,
      subdomains: "abcd",
      maxZoom: 19,
    }).addTo(map.current);

    // Norfolk boundary hint — subtle circle
    L.circle(NORFOLK_CENTER, {
      radius: 8000,
      color: "rgba(6, 182, 212, 0.15)",
      fillColor: "rgba(6, 182, 212, 0.03)",
      fillOpacity: 1,
      weight: 1,
      dashArray: "6 4",
      interactive: false,
    }).addTo(map.current);

    map.current.on("click", (e) => {
      const { lat, lng } = e.latlng;
      if (onMapClick) onMapClick(lat, lng);
    });

    return () => {
      if (map.current) {
        map.current.remove();
        map.current = null;
      }
    };
  }, []);

  // Switch tiles when theme changes
  useEffect(() => {
    if (!map.current || !tileLayer.current) return;

    const tiles = TILES[theme] || TILES.dark;
    tileLayer.current.setUrl(tiles.url);
  }, [theme]);

  // Update marker when assessment changes
  useEffect(() => {
    if (!map.current || !assessment) return;

    if (marker.current) marker.current.remove();
    if (pulseMarker.current) pulseMarker.current.remove();

    const color = getGradeColor(assessment.risk.grade);

    // Pulse ring marker (underneath)
    const pulseIcon = L.divIcon({
      className: "custom-marker",
      html: `<div style="
        width: 54px;
        height: 54px;
        border-radius: 50%;
        border: 2px solid ${color};
        animation: markerPulse 2s ease-out infinite;
        --pulse-color: ${color}60;
        position: absolute;
        top: -5px;
        left: -5px;
      "></div>`,
      iconSize: [44, 44],
      iconAnchor: [22, 22],
    });

    pulseMarker.current = L.marker(
      [assessment.latitude, assessment.longitude],
      { icon: pulseIcon, interactive: false },
    ).addTo(map.current);

    // Main marker
    const icon = L.divIcon({
      className: "custom-marker",
      html: `<div style="
        width: 44px;
        height: 44px;
        border-radius: 50%;
        background: radial-gradient(circle at 35% 35%, ${color}dd, ${color});
        border: 3px solid white;
        display: flex;
        align-items: center;
        justify-content: center;
        font-size: 20px;
        font-weight: 800;
        color: #fff;
        box-shadow: 0 0 24px ${color}80, 0 4px 12px rgba(0,0,0,0.4);
        text-shadow: 0 1px 3px rgba(0,0,0,0.3);
        transition: transform 0.3s ease;
      ">${assessment.risk.grade}</div>`,
      iconSize: [44, 44],
      iconAnchor: [22, 22],
      popupAnchor: [0, -26],
    });

    marker.current = L.marker([assessment.latitude, assessment.longitude], {
      icon,
    }).addTo(map.current);

    // Themed popup
    const isDark = theme === "dark";
    marker.current.bindPopup(`
      <div style="
        font-family: 'Inter', sans-serif;
        min-width: 200px;
        padding: 4px;
      ">
        <div style="font-weight: 700; font-size: 0.95rem; margin-bottom: 8px; color: ${isDark ? "#e8edf5" : "#1a2332"};">
          ${assessment.address}
        </div>
        <div style="display: flex; gap: 12px; margin-bottom: 8px;">
          <div style="text-align: center;">
            <div style="font-size: 1.6rem; font-weight: 800; color: ${color};">${assessment.risk.grade}</div>
            <div style="font-size: 0.65rem; color: ${isDark ? "#8b97b0" : "#5b6b82"}; text-transform: uppercase;">Grade</div>
          </div>
          <div style="text-align: center;">
            <div style="font-size: 1.6rem; font-weight: 800; color: ${isDark ? "#e8edf5" : "#1a2332"};">${assessment.risk.score}</div>
            <div style="font-size: 0.65rem; color: ${isDark ? "#8b97b0" : "#5b6b82"}; text-transform: uppercase;">Score</div>
          </div>
          <div style="text-align: center;">
            <div style="font-size: 1.6rem; font-weight: 800; color: ${isDark ? "#e8edf5" : "#1a2332"};">${assessment.elevation?.elevation_ft?.toFixed(0) || "—"}</div>
            <div style="font-size: 0.65rem; color: ${isDark ? "#8b97b0" : "#5b6b82"}; text-transform: uppercase;">Elev (ft)</div>
          </div>
        </div>
        <div style="font-size: 0.75rem; color: ${isDark ? "#8b97b0" : "#5b6b82"}; padding-top: 6px; border-top: 1px solid ${isDark ? "rgba(255,255,255,0.08)" : "rgba(0,0,0,0.08)"};">
          🌊 Water: ${assessment.tide?.current?.water_level_ft?.toFixed(2) || "—"} ft &nbsp;|&nbsp; 💨 Wind: ${assessment.weather?.wind_speed_mph || "—"} mph
        </div>
      </div>
    `);

    map.current.flyTo([assessment.latitude, assessment.longitude], 14, {
      duration: 1.5,
    });
  }, [assessment, theme]);

  return (
    <div
      ref={mapContainer}
      style={{ width: "100%", height: "100%", minHeight: "400px" }}
    />
  );
}
