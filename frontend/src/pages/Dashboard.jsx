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
import GrafikPrediksi from "../components/GrafikPrediksi";
import IndonesiaMap from "../components/IndonesiaMap";
import DistributionOptimizer from "../components/DistributionOptimizer";
import EarlyWarningSystem from "../components/EarlyWarningSystem";
import PolicyRecommendation from "../components/PolicyRecommendation";
import AICommodityIntelligence from "../components/AICommodityIntelligence";
import AlertCard from "../components/AlertCard";
import {
  fetchDashboardDetail,
  fetchDashboardInitial,
  formatRupiah,
  formatPct,
  formatTanggalShort,
  formatRupiahShort,
} from "../api";


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
  const [komoditasList, setKomoditasList] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState([]);
  const [provinsiList, setProvinsiList] = useState([]);
  const [selKomoditas, setSelKomoditas] = useState("");
  const [selProvinsi, setSelProvinsi] = useState("");
  const [geoMode, setGeoMode] = useState("forecast"); // 'forecast' | 'map'
  const [mapHorizon, setMapHorizon] = useState(7); // 1, 7, 30
  const [predPeriod, setPredPeriod] = useState("30"); // '7' | '30'
  const [lastUpdated, setLastUpdated] = useState(null);
  const [datasetMaxDate, setDatasetMaxDate] = useState(null);
  const [debouncedSelection, setDebouncedSelection] = useState({
    komoditas: "",
    provinsi: "",
  });
  const [detailData, setDetailData] = useState(null);
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState(null);

  useEffect(() => {
    const controller = new AbortController();
    async function run() {
      try {
        setLoadingInitial(true);
        setError(null);
        const initData = await fetchDashboardInitial(controller.signal);
        const alertData = initData.alert || [];
        const statsData = initData.statistik_nasional || [];
        const provData = initData.provinsi || [];
        const komoditasData = initData.komoditas || [];
        const defaultProv =
          initData.default_selection?.provinsi || provData?.[0]?.slug || "";
        const defaultKom =
          initData.default_selection?.komoditas || komoditasData?.[0]?.slug || "";

        setAlerts(alertData);
        onAlertsLoaded?.(alertData.filter((a) => a.kenaikan_pct > 10));
        setStats(statsData);
        setProvinsiList(provData);
        setKomoditasList(komoditasData);
        setSelKomoditas(defaultKom);
        setSelProvinsi(defaultProv);
        setDatasetMaxDate(initData.metadata?.dataset_max_date);
        setLastUpdated(new Date());
      } catch (err) {
        if (err.name !== "AbortError") setError(err.message);
      } finally {
        setLoadingInitial(false);
      }
    }
    run();
    return () => controller.abort();
  }, [onAlertsLoaded]);

  useEffect(() => {
    const timer = setTimeout(() => {
      setDebouncedSelection({
        komoditas: selKomoditas,
        provinsi: selProvinsi,
      });
    }, 350);
    return () => clearTimeout(timer);
  }, [selKomoditas, selProvinsi]);

  useEffect(() => {
    if (!debouncedSelection.komoditas || !debouncedSelection.provinsi) return;
    const controller = new AbortController();
    async function run() {
      try {
        setLoadingDetail(true);
        const detail = await fetchDashboardDetail(
          debouncedSelection.komoditas,
          debouncedSelection.provinsi,
          controller.signal,
        );
        setDetailData(detail);
        setLastUpdated(new Date());
      } catch (err) {
        if (err.name !== "AbortError") setError(err.message);
      } finally {
        setLoadingDetail(false);
      }
    }
    run();
    return () => controller.abort();
  }, [debouncedSelection]);

  const predChart = useMemo(
    () => ({
      ringkasan: detailData?.prediksi?.ringkasan || {},
      harian: detailData?.prediksi?.harian || [],
      historis: detailData?.historis || [],
    }),
    [detailData],
  );

  const semuaProv = detailData?.prediksi_semua || [];
  const loading = loadingInitial || loadingDetail;

  // KPIs from real stats
  const avgNasional = useMemo(() => {
    const selectedKomoditasName = komoditasList.find((k) => k.slug === selKomoditas)?.nama;
    const s = stats.find((x) => x.komoditas === selectedKomoditasName);
    return s?.harga_rata_nasional || null;
  }, [stats, selKomoditas, komoditasList]);

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

  // Full data for map without truncation
  const mapData = useMemo(() => {
    return (semuaProv || []).map((r) => ({
      name: r.provinsi,
      harga: r.harga_sekarang,
      prediksi: mapHorizon === 1 ? r.prediksi_1h : mapHorizon === 7 ? r.prediksi_7h : r.prediksi_30h,
    }));
  }, [semuaProv, mapHorizon]);

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
          <div style={{display: "flex", alignItems: "center", gap: 12}}><h2>PanganAI Executive Command Center</h2>{komoditasList.length > 0 && <span style={{background: "#E2E8F0", padding: "4px 10px", borderRadius: 20, fontSize: 12, fontWeight: 600, color: "#475569"}}>{komoditasList.length} Komoditas Aktif</span>}</div>
          <p>AI-Powered National Food Monitoring & Forecasting</p>
        </div>
      </div>

      {/* ── SECTION 1: Executive KPI Summary ── */}
      <div className="flex items-center gap-2" style={{ marginBottom: 24 }}>
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
                value={komoditasList.length}
                icon={Package}
                color="#10B981"
                footer="Beras, Minyak, Cabai"
              />
              <MetricCard
                label="Harga Rata-rata"
                value={avgNasional ? formatRupiahShort(avgNasional) : "—"}
                icon={DollarSign}
                color="#F97316"
                footer={komoditasList.find((k) => k.slug === selKomoditas)?.nama || "-"}
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
            {komoditasList.map((k) => (
              <option key={k.slug || k.nama} value={k.slug || k.nama}>
                {k.nama || k.slug}
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

      {/* ── SECTION 2: Commodity Price Forecast ── */}
      <div className="chart-card" style={{ marginBottom: 24 }}>
        <div className="chart-card-header">
          <div className="chart-card-title">
            <TrendingUp size={16} /> Prediksi Harga Komoditas — {selKomoditas}
          </div>
          <div className="toggle-group">
            {geoMode === "map" && (
              <select 
                className="filter-select" 
                value={mapHorizon} 
                onChange={(e) => setMapHorizon(Number(e.target.value))}
                style={{ marginRight: 8, padding: "4px 8px", fontSize: 12 }}
              >
                <option value={1}>1 Day</option>
                <option value={7}>7 Days</option>
                <option value={30}>30 Days</option>
              </select>
            )}
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
            komoditas={komoditasList.find((k) => k.slug === selKomoditas)?.nama || selKomoditas}
            het={null}
            historyDays={45}
            tanggalHariIni={new Date().toISOString().split('T')[0]}
          />
        ) : (
          <IndonesiaMap data={mapData} komoditas={selKomoditas} horizon={mapHorizon} baseDate={datasetMaxDate} />
        )}
      </div>

      {/* ── SECTION 3: AI Commodity Intelligence ── */}
      {loading ? (
        <div className="skeleton" style={{ height: 400, borderRadius: 8, marginBottom: 24 }} />
      ) : (
        <AICommodityIntelligence alerts={alerts} />
      )}

      {/* ── SECTION 4: Early Warning System ── */}
      {loading ? (
        <div className="skeleton" style={{ height: 400, borderRadius: 8, marginBottom: 24 }} />
      ) : (
        <EarlyWarningSystem alerts={alerts} />
      )}

      {/* ── SECTION 5: Supply & Distribution Optimizer ── */}
      <DistributionOptimizer 
        komoditasList={komoditasList} 
        selKomoditas={selKomoditas} 
        onKomoditasChange={setSelKomoditas} 
        semuaProv={semuaProv} 
      />

      {/* ── SECTION 6: Policy Recommendation Engine ── */}
      {loading ? (
        <div className="skeleton" style={{ height: 400, borderRadius: 8 }} />
      ) : (
        <PolicyRecommendation alerts={alerts} />
      )}
    </div>
  );
}
