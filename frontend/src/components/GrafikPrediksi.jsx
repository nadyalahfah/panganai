import { useEffect, useMemo, useRef, useState } from "react";
import {
  ComposedChart,
  Area,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ReferenceLine,
} from "recharts";
import { TrendingUp } from "lucide-react";
import { formatRupiah, formatRupiahShort, formatTanggalShort } from "../api";

function CustomTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;

  // Remove duplicate 'Prediksi' value if 'Aktual' is also present (at the transition point)
  const hasAktual = payload.some((p) => p.dataKey === "aktual");
  const filteredPayload = payload.filter(
    (p) => !(p.dataKey === "prediksi" && hasAktual),
  );

  return (
    <div className="custom-tooltip">
      <div className="tooltip-date">{formatTanggalShort(label)}</div>
      {filteredPayload.map((p, i) => (
        <div key={i} className="tooltip-item">
          <span
            className="tooltip-dot"
            style={{ background: p.color || p.stroke }}
          />
          <span>
            {p.name}: {formatRupiah(p.value)}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function GrafikPrediksi({
  historis,
  prediksi,
  komoditas,
  tanggalHariIni,
  het,
  historyDays = 45,
}) {
  const scrollRef = useRef(null);
  const [viewportWidth, setViewportWidth] = useState(0);
  const forecastLen = prediksi?.length || 0;
  const effectiveHistoryDays =
    forecastLen > 0
      ? Math.max(7, Math.min(historyDays, forecastLen))
      : historyDays;

  const chartData = useMemo(() => {
    const result = [];
    const cutoffMs = tanggalHariIni
      ? new Date(tanggalHariIni).getTime()
      : Number.POSITIVE_INFINITY;
    if (historis && historis.length > 0) {
      historis
        .filter((d) => {
          const ts = new Date(d.tanggal).getTime();
          return !Number.isNaN(ts) && ts <= cutoffMs;
        })
        .slice(-effectiveHistoryDays)
        .forEach((d) => {
        result.push({
          tanggal: d.tanggal,
            tanggalMs: new Date(d.tanggal).getTime(),
            aktual: d.harga,
            prediksi: null,
          });
        });
    }
    if (prediksi && prediksi.length > 0 && result.length > 0) {
      const last = result[result.length - 1];
      // Connect the lines by setting the first prediction point at the last actual date
      last.prediksi = last.aktual;

      // Fill 1-day gap between last actual date and first prediction date (visual continuity only).
      const firstPredDate = new Date(prediksi[0]?.tanggal);
      const lastActualDate = new Date(last.tanggal);
      if (
        !Number.isNaN(firstPredDate.getTime()) &&
        !Number.isNaN(lastActualDate.getTime())
      ) {
        const diffDays = Math.round(
          (firstPredDate.getTime() - lastActualDate.getTime()) /
            (1000 * 60 * 60 * 24),
        );
        if (diffDays === 2) {
          const gapDate = new Date(lastActualDate);
          gapDate.setDate(gapDate.getDate() + 1);
          result.push({
            tanggal: gapDate.toISOString().slice(0, 10),
            tanggalMs: gapDate.getTime(),
            aktual: null,
            prediksi: last.aktual,
          });
        }
      }

      prediksi.forEach((d) => {
        result.push({
          tanggal: d.tanggal,
          tanggalMs: new Date(d.tanggal).getTime(),
          aktual: null,
          prediksi: d.prediksi,
        });
      });
    }
    return result;
  }, [historis, prediksi, effectiveHistoryDays, tanggalHariIni]);

  const chartWidth = useMemo(() => {
    const pxPerPoint = 24;
    const minWidth = Math.max(640, viewportWidth || 0);
    return Math.max(minWidth, chartData.length * pxPerPoint);
  }, [chartData.length, viewportWidth]);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el) return;
    const update = () => setViewportWidth(el.clientWidth || 0);
    update();
    window.addEventListener("resize", update);
    return () => window.removeEventListener("resize", update);
  }, []);

  useEffect(() => {
    const el = scrollRef.current;
    if (!el || !chartData.length || !tanggalHariIni || !viewportWidth) return;
    const todayMs = new Date(tanggalHariIni).getTime();
    if (Number.isNaN(todayMs)) return;

    const minMs = Math.min(...chartData.map((d) => d.tanggalMs));
    const maxMs = Math.max(...chartData.map((d) => d.tanggalMs));
    const span = maxMs - minMs;
    if (span <= 0) return;

    const ratio = Math.max(0, Math.min(1, (todayMs - minMs) / span));
    const todayX = ratio * chartWidth;
    const targetScroll = todayX - viewportWidth / 2;
    const maxScroll = Math.max(0, chartWidth - viewportWidth);
    el.scrollLeft = Math.max(0, Math.min(maxScroll, targetScroll));
  }, [chartData, chartWidth, tanggalHariIni, viewportWidth]);

  if (chartData.length === 0)
    return <div className="skeleton skeleton-chart" />;

  const actualVals = chartData
    .map((d) => d.aktual)
    .filter((v) => v !== null && v !== undefined);
  const predVals = chartData
    .map((d) => d.prediksi)
    .filter((v) => v !== null && v !== undefined);

  const actualMin = actualVals.length ? Math.min(...actualVals) : null;
  const actualMax = actualVals.length ? Math.max(...actualVals) : null;
  const predMin = predVals.length ? Math.min(...predVals) : null;
  const predMax = predVals.length ? Math.max(...predVals) : null;

  const globalTop = Math.max(
    ...(actualMax !== null ? [actualMax] : []),
    ...(predMax !== null ? [predMax] : []),
  );
  const globalBottom = Math.min(
    ...(actualMin !== null ? [actualMin] : []),
    ...(predMin !== null ? [predMin] : []),
  );

  const yMin = Math.max(0, Math.floor((globalBottom - 5000) / 1000) * 1000);
  const yMax = Math.ceil((globalTop + 5000) / 1000) * 1000;
  const yTicks = useMemo(() => {
    const count = 5;
    const step = (yMax - yMin) / (count - 1 || 1);
    return Array.from({ length: count }, (_, i) => yMin + step * i).reverse();
  }, [yMin, yMax]);

  return (
    <div className="pred-chart-wrapper fade-in">
      <style>{`
        .pred-chart-wrapper .recharts-wrapper:focus,
        .pred-chart-wrapper .recharts-surface:focus,
        .pred-chart-wrapper svg:focus {
          outline: none !important;
        }
      `}</style>
      <div className="chart-card-header" style={{ marginBottom: 16 }}>
        <div
          className="chart-card-title"
          style={{ display: "inline-flex", alignItems: "center", gap: 6 }}
        >
          <TrendingUp size={16} />
          <span>Harga Nasional - {komoditas}</span>
        </div>
        <div style={{ display: "flex", gap: 16, fontSize: 12 }}>
          <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <span
              style={{
                width: 16,
                height: 2.5,
                background: "#3B82F6",
                display: "inline-block",
              }}
            />
            Aktual
          </span>
          <span style={{ display: "flex", alignItems: "center", gap: 5 }}>
            <span
              style={{
                width: 16,
                height: 2.5,
                background: "#10B981",
                display: "inline-block",
              }}
            />
            Prediksi
          </span>
        </div>
      </div>
      <div style={{ position: "relative", height: 330 }}>
        <div
          style={{
            position: "absolute",
            left: 0,
            top: 0,
            bottom: 0,
            width: 72,
            zIndex: 20,
            background: "#FFFFFF",
            borderRight: "1px solid #E5E7EB",
            pointerEvents: "none",
          }}
        >
          <div style={{ position: "relative", width: "100%", height: "100%" }}>
            {yTicks.map((tick, idx) => {
              const ratio = yTicks.length > 1 ? idx / (yTicks.length - 1) : 0;
              // Sync with chart plot area: height(330) - top(10) - bottom(5) - xAxis(30) = 285
              const y = 10 + ratio * 285;
              return (
                <div
                  key={tick}
                  style={{
                    position: "absolute",
                    right: 6,
                    top: y,
                    transform: "translateY(-50%)",
                    fontSize: 10,
                    color: "#9CA3AF",
                    whiteSpace: "nowrap",
                  }}
                >
                  {formatRupiahShort(tick)}
                </div>
              );
            })}
          </div>
        </div>

        <div
          ref={scrollRef}
          style={{
            width: "100%",
            height: "100%",
            overflowX: "auto",
            overflowY: "hidden",
            paddingLeft: 72,
          }}
        >
          <ComposedChart
            width={chartWidth}
            height={330}
            data={chartData}
            margin={{ top: 10, right: 12, left: 0, bottom: 5 }}
          >
            <defs>
              <linearGradient id="gAktual" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gPrediksi" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid
              strokeDasharray="3 3"
              stroke="#F3F4F6"
              vertical={false}
            />
          <XAxis
            dataKey="tanggalMs"
            type="number"
            scale="time"
            domain={["dataMin", "dataMax"]}
            tickFormatter={formatTanggalShort}
            tick={{ fontSize: 10, fill: "#9CA3AF" }}
            interval="preserveStartEnd"
            minTickGap={50}
          />
          <YAxis domain={[yMin, yMax]} hide />
          <Tooltip content={<CustomTooltip />} />
            {tanggalHariIni && (
              <ReferenceLine
                x={new Date(tanggalHariIni).getTime()}
                stroke="#94A3B8"
                strokeDasharray="4 4"
                strokeWidth={1.2}
                label={{
                  value: "Hari ini",
                  position: "insideTop",
                  fill: "#64748B",
                  fontSize: 10,
                  fontWeight: 600,
                  offset: 4,
                  dx: 3,
                  textAnchor: "start",
                }}
              />
            )}
            {het && (
              <ReferenceLine
                y={het}
                stroke="#EF4444"
                strokeDasharray="4 4"
                strokeWidth={1.5}
                label={{
                  value: "Ambang Batas (HET)",
                  position: "insideTopRight",
                  fill: "#EF4444",
                  fontSize: 10,
                  fontWeight: 600,
                }}
              />
            )}
            <Area
              type="monotone"
              dataKey="aktual"
              name="Harga Aktual"
              stroke="#3B82F6"
              strokeWidth={2.5}
              fill="url(#gAktual)"
              dot={false}
              activeDot={{ r: 4, strokeWidth: 0, fill: "#3B82F6" }}
              connectNulls={false}
            />
            <Area
              type="monotone"
              dataKey="prediksi"
              name="Prediksi"
              stroke="#10B981"
              strokeWidth={2.5}
              strokeDasharray="5 5"
              fill="url(#gPrediksi)"
              dot={false}
              activeDot={{ r: 4, strokeWidth: 0, fill: "#10B981" }}
              connectNulls={false}
            />
          </ComposedChart>
        </div>
      </div>
    </div>
  );
}
