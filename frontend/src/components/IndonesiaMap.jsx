import React, { useState, useMemo } from "react";
import {
  ComposableMap,
  Geographies,
  Geography,
  Marker,
} from "react-simple-maps";
import { formatRupiah, formatTanggalFull } from "../api";

const geoUrl = "/indonesia-province.json";

export default function IndonesiaMap({
  data,
  komoditas,
  horizon = 7,
  baseDate,
  monitoredProvinces = [],
}) {
  const [hoverRegion, setHoverRegion] = useState(null);
  const [tooltipPos, setTooltipPos] = useState({ x: 0, y: 0 });
  const [selectedProv, setSelectedProv] = useState(null);

  const normalizeProvName = (name) => {
    if (!name) return "";
    return String(name)
      .toUpperCase()
      .replace(/\./g, " ")
      .replace(/-/g, " ")
      .replace(/\s+/g, " ")
      .trim();
  };

  const PROV_ALIASES = {
    // Jakarta & Yogyakarta
    "DKI JAKARTA": "DKI JAKARTA",
    "DAERAH KHUSUS IBUKOTA JAKARTA": "DKI JAKARTA",

    "DI YOGYAKARTA": "DI YOGYAKARTA",
    "D I YOGYAKARTA": "DI YOGYAKARTA",
    "DI ACEH": "ACEH",
    "DI. ACEH": "ACEH",
    "DAERAH ISTIMEWA YOGYAKARTA": "DI YOGYAKARTA",

    // Aceh
    ACEH: "ACEH",
    "NANGGROE ACEH DARUSSALAM": "ACEH",

    // Banten
    BANTEN: "BANTEN",
    PROBANTEN: "BANTEN",
    "PROV BANTEN": "BANTEN",
    "PROVINSI BANTEN": "BANTEN",

    // Bangka Belitung
    "KEPULAUAN BANGKA BELITUNG": "BANGKA BELITUNG",
    "KEP BANGKA BELITUNG": "BANGKA BELITUNG",
    "BANGKA BELITUNG": "BANGKA BELITUNG",

    // Kepulauan Riau
    "KEPULAUAN RIAU": "KEPULAUAN RIAU",
    "KEP RIAU": "KEPULAUAN RIAU",

    // Nusa Tenggara
    "NUSATENGGARA BARAT": "NUSA TENGGARA BARAT",
    "NUSA TENGGARA BARAT": "NUSA TENGGARA BARAT",
    "NUSATENGGARA TIMUR": "NUSA TENGGARA TIMUR",
    "NUSA TENGGARA TIMUR": "NUSA TENGGARA TIMUR",

    // Papua lama ke Papua modern
    "IRIAN JAYA TIMUR": "PAPUA",
    "IRIAN JAYA TENGAH": "PAPUA",
    "IRIAN JAYA BARAT": "PAPUA BARAT",

    PAPUA: "PAPUA",
    "PAPUA BARAT": "PAPUA BARAT",

    // Kalau GeoJSON kamu 38 provinsi, tapi backend masih 34
    "PAPUA BARAT DAYA": "PAPUA BARAT",
    "PAPUA SELATAN": "PAPUA",
    "PAPUA TENGAH": "PAPUA",
    "PAPUA PEGUNUNGAN": "PAPUA",

    // Kalimantan
    "KALIMANTAN BARAT": "KALIMANTAN BARAT",
    "KALIMANTAN TENGAH": "KALIMANTAN TENGAH",
    "KALIMANTAN SELATAN": "KALIMANTAN SELATAN",
    "KALIMANTAN TIMUR": "KALIMANTAN TIMUR",
    "KALIMANTAN UTARA": "KALIMANTAN UTARA",

    // Sulawesi
    "SULAWESI UTARA": "SULAWESI UTARA",
    "SULAWESI TENGAH": "SULAWESI TENGAH",
    "SULAWESI SELATAN": "SULAWESI SELATAN",
    "SULAWESI TENGGARA": "SULAWESI TENGGARA",
    "SULAWESI BARAT": "SULAWESI BARAT",
    GORONTALO: "GORONTALO",

    // Maluku
    MALUKU: "MALUKU",
    "MALUKU UTARA": "MALUKU UTARA",

    // Sumatera
    "SUMATERA UTARA": "SUMATERA UTARA",
    "SUMATERA BARAT": "SUMATERA BARAT",
    "SUMATERA SELATAN": "SUMATERA SELATAN",
    RIAU: "RIAU",
    JAMBI: "JAMBI",
    BENGKULU: "BENGKULU",
    LAMPUNG: "LAMPUNG",

    // Jawa & Bali
    "JAWA BARAT": "JAWA BARAT",
    "JAWA TENGAH": "JAWA TENGAH",
    "JAWA TIMUR": "JAWA TIMUR",
    BALI: "BALI",
  };

  const PROVINCE_COORDS = {
    ACEH: [96.91, 4.69],
    "SUMATERA UTARA": [99.06, 2.12],
    "SUMATERA BARAT": [100.47, -0.85],
    RIAU: [101.81, 0.51],
    JAMBI: [103.61, -1.61],
    "SUMATERA SELATAN": [104.75, -3.32],
    BENGKULU: [102.26, -3.79],
    LAMPUNG: [105.26, -5.45],
    "BANGKA BELITUNG": [106.44, -2.74],
    "KEPULAUAN RIAU": [104.45, 0.92],

    "DKI JAKARTA": [106.83, -6.2],
    "JAWA BARAT": [107.6, -6.9],
    "JAWA TENGAH": [110.42, -7.15],
    "DI YOGYAKARTA": [110.37, -7.8],
    "JAWA TIMUR": [112.75, -7.25],
    BANTEN: [106.16, -6.12],
    BALI: [115.18, -8.65],

    "NUSA TENGGARA BARAT": [117.36, -8.65],
    "NUSA TENGGARA TIMUR": [121.08, -8.65],

    "KALIMANTAN BARAT": [111.1, -0.1],
    "KALIMANTAN TENGAH": [113.92, -1.68],
    "KALIMANTAN SELATAN": [115.22, -3.09],
    "KALIMANTAN TIMUR": [116.99, 0.54],
    "KALIMANTAN UTARA": [117.36, 2.8],

    "SULAWESI UTARA": [124.85, 1.49],
    "SULAWESI TENGAH": [120.0, -1.43],
    "SULAWESI SELATAN": [119.7, -4.6],
    "SULAWESI TENGGARA": [122.07, -4.0],
    GORONTALO: [123.06, 0.7],
    "SULAWESI BARAT": [119.32, -2.84],

    MALUKU: [129.36, -3.7],
    "MALUKU UTARA": [127.8, 0.63],
    PAPUA: [138.08, -4.27],
    "PAPUA BARAT": [132.9, -1.34],
  };

  const getGeoProvName = (properties = {}) => {
    return (
      properties.Propinsi ||
      properties.PROVINSI ||
      properties.provinsi ||
      properties.Provinsi ||
      properties.NAMOBJ ||
      properties.NAME_1 ||
      properties.NAME ||
      properties.name ||
      properties.prov_name ||
      properties.province ||
      properties.Province ||
      ""
    );
  };

  const toCanonicalProv = (name) => {
    const key = normalizeProvName(name);

    const spacedKey = key
      .replace(/^NUSATENGGARA/, "NUSA TENGGARA")
      .replace(/^KEPULAUAN/, "KEPULAUAN ")
      .replace(/^SULAWESI/, "SULAWESI ")
      .replace(/^KALIMANTAN/, "KALIMANTAN ")
      .replace(/^SUMATERA/, "SUMATERA ")
      .replace(/^JAWA/, "JAWA ")
      .replace(/^MALUKU/, "MALUKU ")
      .replace(/^PAPUA/, "PAPUA ")
      .replace(/\s+/g, " ")
      .trim();

    return PROV_ALIASES[spacedKey] || PROV_ALIASES[key] || spacedKey;
  };

  const backendProvCanonicalSet = useMemo(() => {
    const set = new Set();
    (monitoredProvinces || []).forEach((p) => {
      const raw = typeof p === "string" ? p : p?.nama || p?.slug || "";
      if (!raw) return;
      set.add(toCanonicalProv(raw));
    });
    return set;
  }, [monitoredProvinces]);

  const toBackendProv = (name) => {
    const canonical = toCanonicalProv(name);
    if (backendProvCanonicalSet.has(canonical)) return canonical;

    // Fallback bridging for legacy 34-prov data vs newer labels in geojson.
    if (canonical.startsWith("PAPUA") && backendProvCanonicalSet.has("PAPUA"))
      return "PAPUA";
    if (
      canonical.startsWith("PAPUA BARAT") &&
      backendProvCanonicalSet.has("PAPUA BARAT")
    )
      return "PAPUA BARAT";
    if (
      canonical.startsWith("KEP ") &&
      backendProvCanonicalSet.has(canonical.replace(/^KEP /, "KEPULAUAN "))
    ) {
      return canonical.replace(/^KEP /, "KEPULAUAN ");
    }
    return canonical;
  };

  // Parse backend data into a lookup dictionary keyed by normalized province name
  const provDataMap = useMemo(() => {
    const mapData = {};
    if (!data) return mapData;
    data.forEach((d) => {
      const normalizedName = toBackendProv(d.name);

      const computedPct =
        d.changePct !== undefined && d.changePct !== null
          ? Number(d.changePct)
          : ((Number(d.prediksi) - Number(d.harga)) / Number(d.harga)) * 100;
      const changePct = Number.isFinite(computedPct) ? computedPct : 0;
      const absChange = Math.abs(changePct);

      let status = "Aman";
      let color = "#10B981";

      if (absChange >= 20) {
        status = "Kritis";
        color = "#EF4444"; // Red
      } else if (absChange >= 10) {
        status = "Berisiko Tinggi";
        color = "#F97316"; // Orange
      } else if (absChange >= 5) {
        status = "Waspada";
        color = "#EAB308"; // Yellow
      }

      mapData[normalizedName] = {
        ...d,
        changePct,
        status,
        color,
      };
    });
    return mapData;
  }, [data]);

  const updateTooltipPos = (clientX, clientY) => {
    const tooltipWidth = 260; // Estimated max width
    const tooltipHeight = 280; // Estimated height
    const margin = 15;

    let x = clientX + margin;
    let y = clientY + margin;

    // Right edge detection
    if (x + tooltipWidth > window.innerWidth) {
      x = clientX - tooltipWidth - margin;
    }

    // Bottom edge detection
    if (y + tooltipHeight > window.innerHeight) {
      y = window.innerHeight - tooltipHeight - margin;
    }

    // Top edge detection
    if (y < margin) {
      y = margin;
    }

    setTooltipPos({ x, y });
  };

  const handleMouseEnter = (geo, e) => {
    const rawGeoName = getGeoProvName(geo.properties);
    const provName = toBackendProv(rawGeoName);

    const provData = provDataMap[provName] || {
      name: rawGeoName || "Provinsi tidak terbaca",
      harga: 0,
      prediksi: 0,
      changePct: 0,
      status: "Tidak Ada Data",
      color: "#CBD5E1",
    };

    setHoverRegion({ ...provData, rawName: rawGeoName });
    updateTooltipPos(e.clientX, e.clientY);
  };

  const handleMarkerEnter = (provName, e) => {
    const provData = provDataMap[provName];

    if (!provData) return;

    setHoverRegion({
      ...provData,
      rawName: provName,
    });

    updateTooltipPos(e.clientX, e.clientY);
  };

  const handleMouseMove = (e) => {
    updateTooltipPos(e.clientX, e.clientY);
  };

  const handleMouseLeave = () => {
    setHoverRegion(null);
  };

  const handleClick = (geo) => {
    const rawGeoName = getGeoProvName(geo.properties);
    const provName = toBackendProv(rawGeoName);

    if (selectedProv === provName) {
      setSelectedProv(null);
    } else {
      setSelectedProv(provName);
    }
  };

  let currentDateStr = "Hari ini";
  if (baseDate) {
    currentDateStr = formatTanggalFull(baseDate);
  }

  const getPerubahanIcon = (val) => {
    if (val > 0) return "▲";
    if (val < 0) return "▼";
    return "-";
  };

  return (
    <div
      style={{
        position: "relative",
        width: "100%",
        height: 400,
        background: "var(--gray-50)",
        borderRadius: 8,
        overflow: "hidden",
        border: "1px solid var(--gray-200)",
      }}
    >
      {/* Map */}
      <ComposableMap
        projection="geoMercator"
        projectionConfig={{
          center: [118, -2.5],
          scale: 1600,
        }}
        style={{ width: "100%", height: "100%" }}
      >
        <Geographies geography={geoUrl}>
          {({ geographies }) => {
            return geographies.map((geo) => {
              const rawGeoName = getGeoProvName(geo.properties);
              const provName = toBackendProv(rawGeoName);
              const d = provDataMap[provName];

              const defaultColor = "#CBD5E1";
              const fillColor = d ? d.color : defaultColor;
              const isSelected = selectedProv === provName;

              return (
                <Geography
                  key={geo.rsmKey}
                  geography={geo}
                  onMouseEnter={(e) => handleMouseEnter(geo, e)}
                  onMouseMove={handleMouseMove}
                  onMouseLeave={handleMouseLeave}
                  onClick={() => handleClick(geo)}
                  style={{
                    default: {
                      fill: fillColor,
                      stroke: isSelected ? "#111827" : "#FFFFFF",
                      strokeWidth: isSelected ? 1.5 : 0.5,
                      outline: "none",
                      opacity: isSelected ? 1 : 0.85,
                    },
                    hover: {
                      fill: fillColor,
                      stroke: "#111827",
                      strokeWidth: 1,
                      outline: "none",
                      opacity: 1,
                      cursor: "pointer",
                    },
                    pressed: {
                      fill: fillColor,
                      stroke: "#111827",
                      strokeWidth: 1.5,
                      outline: "none",
                      opacity: 1,
                    },
                  }}
                />
              );
            });
          }}
        </Geographies>
        {Object.entries(provDataMap).map(([provName, prov]) => {
          const coords = PROVINCE_COORDS[provName];
          if (!coords) return null;

          return (
            <Marker key={provName} coordinates={coords}>
              <circle
                r={provName === "KALIMANTAN UTARA" ? 6 : 4}
                fill={prov.color}
                stroke="#111827"
                strokeWidth={1}
                style={{ cursor: "pointer" }}
                onMouseEnter={(e) => handleMarkerEnter(provName, e)}
                onMouseMove={handleMouseMove}
                onMouseLeave={handleMouseLeave}
              />
            </Marker>
          );
        })}
      </ComposableMap>

      {/* Legend */}
      <div
        style={{
          position: "absolute",
          bottom: 16,
          left: 16,
          background: "rgba(255, 255, 255, 0.9)",
          padding: "8px 12px",
          borderRadius: 6,
          boxShadow: "0 1px 3px rgba(0,0,0,0.1)",
          fontSize: 12,
          fontWeight: 500,
          display: "flex",
          flexDirection: "column",
          gap: 6,
        }}
      >
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: 2,
              background: "#10B981",
            }}
          ></div>
          <span>Aman (&lt; 5% Perubahan)</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: 2,
              background: "#EAB308",
            }}
          ></div>
          <span>Waspada (5-10% Perubahan)</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: 2,
              background: "#F97316",
            }}
          ></div>
          <span>Berisiko Tinggi (10-20% Perubahan)</span>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 6 }}>
          <div
            style={{
              width: 12,
              height: 12,
              borderRadius: 2,
              background: "#EF4444",
            }}
          ></div>
          <span>Kritis (&gt; 20% Perubahan)</span>
        </div>
      </div>

      {/* Custom Tooltip */}
      {hoverRegion && (
        <div
          style={{
            position: "fixed",
            top: tooltipPos.y,
            left: tooltipPos.x,
            background: "white",
            padding: 12,
            borderRadius: 8,
            boxShadow: "0 4px 12px rgba(0,0,0,0.15)",
            border: "1px solid var(--gray-200)",
            pointerEvents: "none",
            zIndex: 1000,
            minWidth: 200,
          }}
        >
          <div style={{ fontWeight: "bold", fontSize: 14, marginBottom: 6 }}>
            {hoverRegion.name}
          </div>
          <div
            style={{
              fontSize: 12,
              color: "var(--text-muted)",
              marginBottom: 2,
            }}
          >
            Komoditas:{" "}
            <span style={{ fontWeight: 500, color: "#111827" }}>
              {komoditas}
            </span>
          </div>

          <div style={{ fontSize: 12, marginBottom: 2 }}>
            <span style={{ color: "var(--text-muted)" }}>Status: </span>
            <span style={{ fontWeight: "bold", color: hoverRegion.color }}>
              {hoverRegion.status}
            </span>
          </div>

          <div style={{ fontSize: 12, marginBottom: 12 }}>
            <span style={{ color: "var(--text-muted)" }}>Data per: </span>
            <span style={{ fontWeight: 500, color: "#111827" }}>
              {currentDateStr}
            </span>
          </div>

          <div
            style={{
              borderTop: "1px solid var(--gray-200)",
              paddingTop: 12,
              marginBottom: 12,
            }}
          >
            <div style={{ fontSize: 12 }}>
              <div style={{ color: "var(--text-muted)", marginBottom: 2 }}>
                Harga Saat Ini
              </div>
              <div style={{ fontWeight: 600, fontSize: 14 }}>
                {hoverRegion.harga > 0 ? formatRupiah(hoverRegion.harga) : "-"}
              </div>
            </div>
          </div>

          <div style={{ fontSize: 12, marginBottom: 12 }}>
            <div style={{ color: "var(--text-muted)", marginBottom: 2 }}>
              Prediksi (+{horizon} Hari)
            </div>
            <div style={{ fontWeight: 600, fontSize: 14 }}>
              {hoverRegion.prediksi > 0
                ? formatRupiah(hoverRegion.prediksi)
                : "-"}
            </div>
          </div>

          <div style={{ fontSize: 12 }}>
            <div style={{ color: "var(--text-muted)", marginBottom: 2 }}>
              Perubahan
            </div>
            <div
              style={{
                fontWeight: "bold",
                fontSize: 14,
                color:
                  hoverRegion.changePct > 0
                    ? "#EF4444"
                    : hoverRegion.changePct < 0
                      ? "#10B981"
                      : "#6B7280",
              }}
            >
              {getPerubahanIcon(hoverRegion.changePct)}{" "}
              {Math.abs(hoverRegion.changePct).toFixed(2)}%
            </div>
          </div>

          {hoverRegion.score && (
            <div
              style={{
                display: "flex",
                justifyContent: "space-between",
                fontSize: 12,
                marginTop: 4,
              }}
            >
              <span style={{ color: "var(--text-muted)" }}>Skor Risiko:</span>
              <span style={{ fontWeight: "bold" }}>{hoverRegion.score}</span>
            </div>
          )}
        </div>
      )}
    </div>
  );
}
