import { useState, useEffect, useMemo } from "react";
import {
  Map,
  BarChart2,
  TrendingUp,
  Bell,
  Activity,
  BarChart,
  DollarSign,
  AlertTriangle,
  Package,
  Truck,
  RefreshCw,
  ArrowUpRight,
  ArrowDownRight,
} from "lucide-react";
import {
  BarChart as ReBarChart,
  Bar,
  XAxis,
  YAxis,
  CartesianGrid,
  Tooltip,
  ResponsiveContainer,
  LineChart,
  Line,
  Legend,
  ReferenceLine,
} from "recharts";
import MetricCard from "../components/MetricCard";
import KpiCard from "../components/KpiCard";
import GrafikHistoris from "../components/GrafikHistoris";
import GrafikPrediksi from "../components/GrafikPrediksi";
import IndonesiaMap from "../components/IndonesiaMap";
import DistributionOptimizer from "../components/DistributionOptimizer";
import EarlyWarningSystem from "../components/EarlyWarningSystem";
import PolicyRecommendation from "../components/PolicyRecommendation";
import AICommodityIntelligence from "../components/AICommodityIntelligence";
import AlertCard from "../components/AlertCard";
import {
  fetchAlert,
  fetchStatistikNasional,
  fetchHargaHistoris,
  fetchProvinsi,
  fetchPrediksiSemua,
  fetchPrediksi,
  formatRupiah,
  formatPct,
  formatTanggalShort,
  formatRupiahShort,
} from "../api";

const KOMODITAS_LIST = [
  "Beras Medium I",
  "Minyak Goreng Curah",
  "Cabai Merah Keriting",
];

const HET_MOCK = {
  "Beras Medium I": 10900,
  "Minyak Goreng Curah": 14000,
  "Cabai Merah Keriting": 45000,
};

const DISTRIB_MOCK = [
  {
    from: "Lampung",
    to: "DKI Jakarta",
    komoditas: "Cabai Merah",
    margin: 8500,
    roi: 18,
    status: "open",
  },
  {
    from: "Solok",
    to: "Sumatera Utara",
    komoditas: "Beras Medium I",
    margin: 5200,
    roi: 12,
    status: "open",
  },
  {
    from: "Jawa Barat",
    to: "Jawa Timur",
    komoditas: "Minyak Goreng Curah",
    margin: 3000,
    roi: 8,
    status: "moderate",
  },
];

function BarTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null;
  return (
    <div className="custom-tooltip">
      <div className="tooltip-date" style={{ marginBottom: 6 }}>
        {label}
      </div>
      {payload.map((p, i) => (
        <div key={i} className="tooltip-item">
          <span className="tooltip-dot" style={{ background: p.fill }} />
          <span>
            {p.name}: {formatRupiah(p.value)}
          </span>
        </div>
      ))}
    </div>
  );
}

export default function Dashboard({ onAlertsLoaded }) {
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState([]);
  const [provinsiList, setProvinsiList] = useState([]);
  const [chartData, setChartData] = useState({});
  const [semuaProv, setSemuaProv] = useState([]);
  const [predChart, setPredChart] = useState({
    ringkasan: {},
    harian: [],
    historis: [],
  });
  const [selKomoditas, setSelKomoditas] = useState(KOMODITAS_LIST[0]);
  const [geoMode, setGeoMode] = useState("forecast"); // 'forecast' | 'map'
  const [predPeriod, setPredPeriod] = useState("30"); // '7' | '30'
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);
  const [lastUpdated, setLastUpdated] = useState(null);

  useEffect(() => {
    async function load() {
      try {
        setLoading(true);
        setError(null);
        const [alertData, statsData, provData] = await Promise.all([
          fetchAlert(),
          fetchStatistikNasional(),
          fetchProvinsi(),
        ]);
        setAlerts(alertData);
        onAlertsLoaded?.(alertData.filter((a) => a.kenaikan_pct > 10));
        setStats(statsData);
        setProvinsiList(provData);

        // Historical charts for all 3 commodities (5 provinces each)
        const chartPromises = KOMODITAS_LIST.map(async (komoditas) => {
          const allData = [];
          for (const prov of provData.slice(0, 5)) {
            try {
              const d = await fetchHargaHistoris(komoditas, prov);
              allData.push(...d);
            } catch {}
          }
          return [komoditas, allData];
        });
        const results = await Promise.all(chartPromises);
        const newChartData = {};
        results.forEach(([k, d]) => {
          newChartData[k] = d;
        });
        setChartData(newChartData);
        setLastUpdated(new Date());
      } catch (err) {
        setError(err.message);
      } finally {
        setLoading(false);
      }
    }
    load();
  }, []);

  // Load geospatial / prediction data when commodity changes
  useEffect(() => {
    async function loadKomoditas() {
      if (!provinsiList.length) return;
      try {
        const [semua, histData, predData] = await Promise.all([
          fetchPrediksiSemua(selKomoditas),
          fetchHargaHistoris(selKomoditas, provinsiList[0]),
          fetchPrediksi(selKomoditas, provinsiList[0]),
        ]);
        setSemuaProv(semua);
        setPredChart({
          ringkasan: predData.ringkasan,
          harian: predData.harian,
          historis: histData,
        });
      } catch {}
    }
    loadKomoditas();
  }, [selKomoditas, provinsiList]);

  // KPIs from real stats
  const avgNasional = useMemo(() => {
    const s = stats.find((s) => s.komoditas === selKomoditas);
    return s?.harga_rata_nasional || null;
  }, [stats, selKomoditas]);

  const alertNaikCount = alerts.filter((a) => a.kenaikan_pct > 10).length;
  const alertWarnCount = alerts.filter(
    (a) => a.kenaikan_pct >= 5 && a.kenaikan_pct <= 10,
  ).length;

  // Bar chart data for provinces (top 15 by price)
  const barData = useMemo(() => {
    return [...semuaProv]
      .sort((a, b) => (b.harga_sekarang || 0) - (a.harga_sekarang || 0))
      .slice(0, 15)
      .map((r) => ({
        name: r.provinsi.replace(/^(DI|DKI) /, "").substring(0, 15),
        harga: r.harga_sekarang,
        prediksi: r.prediksi_7h,
      }));
  }, [semuaProv]);

  // Prediction trend chart
  const trendChartData = useMemo(() => {
    const result = [];
    const days = predPeriod === "7" ? 7 : 30;
    if (predChart.historis.length > 0) {
      predChart.historis.slice(-30).forEach((d) => {
        result.push({ tanggal: d.tanggal, aktual: d.harga, prediksi: null });
      });
    }
    if (predChart.harian.length > 0) {
      const slice = predChart.harian.slice(0, days);
      if (result.length > 0) {
        const last = result[result.length - 1];
        result.push({
          tanggal: slice[0]?.tanggal,
          aktual: null,
          prediksi: last.aktual || slice[0]?.prediksi,
        });
      }
      slice.slice(1).forEach((d) => {
        result.push({ tanggal: d.tanggal, aktual: null, prediksi: d.prediksi });
      });
    }
    return result;
  }, [predChart, predPeriod]);

  const formatTs = (d) =>
    d
      ? d.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" })
      : "—";

  if (error) {
    return (
      <div>
        <div className="page-header">
          <h2>Dashboard</h2>
          <p>Monitoring harga pangan nasional</p>
        </div>
        <div className="error-state">
          <div className="error-icon">⚠️</div>
          <h3>Tidak dapat terhubung ke server</h3>
          <p>{error}</p>
          <p style={{ marginTop: 8, fontSize: 12 }}>
            Pastikan backend berjalan di <code>localhost:8000</code>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {/* ── Page Header ── */}
      <div
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          marginBottom: 20,
          background: "#fcfcfc",
        }}
      >
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h2>Dashboard</h2>
          <p>Monitoring harga pangan nasional — Data PIHPS Bank Indonesia</p>
        </div>
      </div>

      {/* ── Section A: KPI Metrics ── */}
      <div className="flex items-center gap-2">
        <div className="metrics-grid flex-1 gap-2">
          {loading ? (
            <>
              {[0, 1, 2, 3].map((i) => (
                <div key={i} className="skeleton skeleton-card" />
              ))}
            </>
          ) : (
            <>
              <MetricCard
                label="Provinsi Dipantau"
                value={provinsiList.length}
                icon={Map}
                color="#3B82F6"
                footer="Seluruh Indonesia"
              />
              <MetricCard
                label="Alert Kritis"
                value={alertNaikCount}
                icon={AlertTriangle}
                color="#EF4444"
                trendPct={alertNaikCount > 0 ? alertNaikCount * 2 : 0}
                footer={`${alertWarnCount} peringatan sedang`}
              />
              <MetricCard
                label="Komoditas Dipantau"
                value={KOMODITAS_LIST.length}
                icon={Package}
                color="#10B981"
                footer="Beras, Minyak, Cabai"
              />
              <MetricCard
                label="Harga Rata-rata"
                value={avgNasional ? formatRupiahShort(avgNasional) : "—"}
                icon={DollarSign}
                color="#F97316"
                footer={selKomoditas}
              />
            </>
          )}
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <select
            className="filter-select"
            value={selKomoditas}
            onChange={(e) => setSelKomoditas(e.target.value)}
            style={{ minWidth: 200 }}
          >
            {KOMODITAS_LIST.map((k) => (
              <option key={k} value={k}>
                {k}
              </option>
            ))}
          </select>
          {lastUpdated && (
            <div
              style={{
                display: "flex",
                alignItems: "center",
                gap: 5,
                fontSize: 11,
                color: "var(--text-muted)",
              }}
            >
              <RefreshCw size={11} /> {formatTs(lastUpdated)}
            </div>
          )}
        </div>
      </div>

      {/* ── Section B: Forecast & Map ── */}
      <div className="chart-card" style={{ marginBottom: 24 }}>
        <div className="chart-card-header">
          <div className="chart-card-title">
            <TrendingUp size={16} /> Prediksi Harga Komoditas — {selKomoditas}
          </div>
          <div className="toggle-group">
            <button
              className={`toggle-btn-item${geoMode === "forecast" ? " active" : ""}`}
              onClick={() => setGeoMode("forecast")}
            >
              Prediksi Harga
            </button>
            <button
              className={`toggle-btn-item${geoMode === "map" ? " active" : ""}`}
              onClick={() => setGeoMode("map")}
            >
              Peta Risiko
            </button>
          </div>
        </div>

        {loading || predChart.harian.length === 0 ? (
          <div className="skeleton" style={{ height: 340, borderRadius: 8 }} />
        ) : geoMode === "forecast" ? (
          <GrafikPrediksi
            historis={predChart.historis}
            prediksi={predChart.harian.slice(0, 30)}
            komoditas={selKomoditas}
            het={HET_MOCK[selKomoditas]}
            historyDays={45}
            tanggalHariIni={new Date().toISOString().split('T')[0]}
          />
        ) : (
          <IndonesiaMap data={barData} komoditas={selKomoditas} />
        )}
      </div>

      {/* ── Section C: Status Cards ── */}
      <div className="status-grid">
        {/* Prediksi */}
        <div className="status-card">
          <div className="status-card-header">
            <div
              className="status-card-icon"
              style={{ background: "rgba(16,185,129,0.1)" }}
            >
              <TrendingUp size={18} color="#10B981" />
            </div>
            <div className="status-card-title">Prediksi Harga</div>
          </div>
          <div className="status-card-body">
            <div className="status-card-value">
              {predChart.ringkasan.tren_7h || "—"}
            </div>
            <div className="status-card-sub">
              H+7: {formatRupiah(predChart.ringkasan.prediksi_7h)}
            </div>
            <div className="status-card-sub">
              H+30: {formatRupiah(predChart.ringkasan.prediksi_30h)}
            </div>
          </div>
          <div className="status-card-footer">Model: LSTM + Prophet</div>
        </div>

        {/* Alert */}
        <div className="status-card">
          <div className="status-card-header">
            <div
              className="status-card-icon"
              style={{ background: "rgba(239,68,68,0.1)" }}
            >
              <Bell size={18} color="#EF4444" />
            </div>
            <div className="status-card-title">Alert System</div>
          </div>
          <div className="status-card-body">
            <div
              className="status-card-value"
              style={{ color: "var(--danger)" }}
            >
              {alertNaikCount} Kritis
            </div>
            <div className="status-card-sub">{alertWarnCount} Peringatan</div>
            <div className="status-card-sub">
              {alerts.length - alertNaikCount - alertWarnCount} Info
            </div>
          </div>
          <div className="status-card-footer">
            Kenaikan prediksi &gt; 30 hari
          </div>
        </div>

        {/* Market Trend */}
        <div className="status-card">
          <div className="status-card-header">
            <div
              className="status-card-icon"
              style={{ background: "rgba(249,115,22,0.1)" }}
            >
              <Activity size={18} color="#F97316" />
            </div>
            <div className="status-card-title">Market Trend</div>
          </div>
          <div className="status-card-body">
            <div className="status-card-value">
              {stats.filter((s) => s.tren_30h_mayoritas === "NAIK").length >
              stats.length / 2
                ? "↑ Mayoritas Naik"
                : "→ Variatif"}
            </div>
            <div className="status-card-sub">
              {stats.length} komoditas dianalisis
            </div>
            <div className="status-card-sub">
              {provinsiList.length} provinsi dipantau
            </div>
          </div>
          <div className="status-card-footer">Update per hari</div>
        </div>
      </div>

      {/* ── Section D: KPI Cards ── */}
      <div
        style={{
          display: "grid",
          gridTemplateColumns: "repeat(4, 1fr)",
          gap: 14,
          marginBottom: 24,
        }}
      >
        {stats.slice(0, 4).map((s, i) => {
          const isNaik = s.tren_30h_mayoritas === "NAIK";
          return (
            <KpiCard
              key={s.komoditas}
              label={s.komoditas}
              value={formatRupiah(s.harga_rata_nasional)}
              icon={DollarSign}
              color={isNaik ? "#EF4444" : "#10B981"}
              trend={isNaik ? "up" : "down"}
              trendText={isNaik ? "Tren naik 30H" : "Tren turun 30H"}
            />
          );
        })}
      </div>

      {/* ── Section E: Distribution Recommendations ── */}
      <DistributionOptimizer 
        komoditasList={KOMODITAS_LIST} 
        selKomoditas={selKomoditas} 
        onKomoditasChange={setSelKomoditas} 
        semuaProv={semuaProv} 
      />

      {/* ── Section F: Price Trend Chart ── */}
      <div className="chart-card" style={{ marginBottom: 24 }}>
        <div className="chart-card-header">
          <div className="chart-card-title">
            📈 Tren Harga & Prediksi — {selKomoditas}
          </div>
          <div className="toggle-group">
            <button
              className={`toggle-btn-item${predPeriod === "7" ? " active" : ""}`}
              onClick={() => setPredPeriod("7")}
            >
              7 Hari
            </button>
            <button
              className={`toggle-btn-item${predPeriod === "30" ? " active" : ""}`}
              onClick={() => setPredPeriod("30")}
            >
              30 Hari
            </button>
          </div>
        </div>
        {loading || trendChartData.length === 0 ? (
          <div className="skeleton" style={{ height: 280, borderRadius: 8 }} />
        ) : (
          <ResponsiveContainer width="100%" height={280}>
            <LineChart
              data={trendChartData}
              margin={{ top: 5, right: 12, left: 0, bottom: 5 }}
            >
              <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
              <XAxis
                dataKey="tanggal"
                tickFormatter={formatTanggalShort}
                tick={{ fontSize: 10, fill: "#9CA3AF" }}
                interval="preserveStartEnd"
                minTickGap={50}
              />
              <YAxis
                tickFormatter={formatRupiahShort}
                tick={{ fontSize: 10, fill: "#9CA3AF" }}
                width={65}
              />
              <Tooltip
                formatter={(v) => formatRupiah(v)}
                labelFormatter={formatTanggalShort}
              />
              <Legend wrapperStyle={{ fontSize: 12 }} />
              <Line
                type="monotone"
                dataKey="aktual"
                name="Aktual"
                stroke="#3B82F6"
                strokeWidth={2.5}
                dot={false}
                connectNulls={false}
              />
              <Line
                type="monotone"
                dataKey="prediksi"
                name="Prediksi"
                stroke="#F97316"
                strokeWidth={2.5}
                strokeDasharray="6 4"
                dot={false}
                connectNulls={false}
              />
            </LineChart>
          </ResponsiveContainer>
        )}
      </div>

      {/* ── Section G: Historical Charts ── */}
      <div className="section-header">
        <div className="section-title">📊 Tren Historis Nasional</div>
      </div>
      <div className="charts-grid">
        {loading ? (
          <>
            {[0, 1, 2].map((i) => (
              <div key={i} className="skeleton skeleton-chart" />
            ))}
          </>
        ) : (
          KOMODITAS_LIST.map((k) => (
            <GrafikHistoris key={k} data={chartData[k] || []} komoditas={k} />
          ))
        )}
      </div>

      {/* ── Section H: Early Warning System ── */}
      {loading ? (
        <div className="skeleton" style={{ height: 400, borderRadius: 8, marginBottom: 24 }} />
      ) : (
        <EarlyWarningSystem alerts={alerts} />
      )}

      {/* ── Section I: Rekomendasi Kebijakan ── */}
      {loading ? (
        <div className="skeleton" style={{ height: 400, borderRadius: 8, marginBottom: 24 }} />
      ) : (
        <PolicyRecommendation alerts={alerts} />
      )}

      {/* ── Section J: AI Commodity Intelligence ── */}
      {loading ? (
        <div className="skeleton" style={{ height: 400, borderRadius: 8 }} />
      ) : (
        <AICommodityIntelligence alerts={alerts} />
      )}
    </div>
  );
}
