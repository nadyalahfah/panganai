import { useState, useEffect, useMemo } from "react";
import {
  Map,
  TrendingUp,
  DollarSign,
  AlertTriangle,
  Package,
  RefreshCw,
  X,
  Info,
} from "lucide-react";
import MetricCard from "../components/MetricCard";
import GrafikPrediksi from "../components/GrafikPrediksi";
import IndonesiaMap from "../components/IndonesiaMap";
import DistributionOptimizer from "../components/DistributionOptimizer";
import EarlyWarningSystem from "../components/EarlyWarningSystem";
import AICommodityIntelligence from "../components/AICommodityIntelligence";
import {
  API_BASE,
  fetchDashboardDetail,
  fetchDashboardInitial,
  formatRupiahShort,
} from "../api";

const FIXED_REFERENCE_DATE = "2026-05-19";
export default function Dashboard({ onAlertsLoaded }) {
  const [komoditasList, setKomoditasList] = useState([]);
  const [alerts, setAlerts] = useState([]);
  const [stats, setStats] = useState([]);
  const [provinsiList, setProvinsiList] = useState([]);
  const [selKomoditas, setSelKomoditas] = useState("");
  const [selProvinsi, setSelProvinsi] = useState("");
  const [geoMode, setGeoMode] = useState("map");
  const [predPeriod, setPredPeriod] = useState("30");
  const [lastUpdated, setLastUpdated] = useState(null);
  const [datasetMaxDate, setDatasetMaxDate] = useState(FIXED_REFERENCE_DATE);
  const [debouncedSelection, setDebouncedSelection] = useState({
    komoditas: "",
    provinsi: "",
  });
  const [detailData, setDetailData] = useState(null);
  const [loadingInitial, setLoadingInitial] = useState(true);
  const [loadingDetail, setLoadingDetail] = useState(false);
  const [error, setError] = useState(null);
  const [showGuideBanner, setShowGuideBanner] = useState(true);

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
        const preferredKomSlug = "cabai-merah-keriting";
        const hasPreferredKom = komoditasData.some(
          (k) => k?.slug === preferredKomSlug,
        );
        const defaultKom = hasPreferredKom
          ? preferredKomSlug
          : initData.default_selection?.komoditas ||
            komoditasData?.[0]?.slug ||
            "";

        if (!komoditasData.length || !provData.length) {
          throw new Error(
            "Backend deploy belum memuat dataset. Cek /api/health: storage_ready, dataset_loaded, dan model_loaded harus true.",
          );
        }

        setAlerts(alertData);
        onAlertsLoaded?.(alertData.filter((a) => a.kenaikan_pct > 10));
        setStats(statsData);
        setProvinsiList(provData);
        setKomoditasList(komoditasData);
        setSelKomoditas(defaultKom);
        setSelProvinsi(defaultProv);
        setDatasetMaxDate(FIXED_REFERENCE_DATE);
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
      setDebouncedSelection({ komoditas: selKomoditas, provinsi: selProvinsi });
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
      ringkasan:
        detailData?.prediksi_nasional?.ringkasan ||
        detailData?.prediksi?.ringkasan ||
        {},
      harian:
        detailData?.prediksi_nasional?.harian ||
        detailData?.prediksi?.harian ||
        [],
      historis: detailData?.historis_nasional || detailData?.historis || [],
    }),
    [detailData],
  );

  const semuaProv = detailData?.prediksi_semua || [];
  const loading = loadingInitial || loadingDetail;

  const selectedKomoditasName = useMemo(
    () =>
      komoditasList.find((k) => k.slug === selKomoditas)?.nama || selKomoditas,
    [komoditasList, selKomoditas],
  );

  const avgNasional = useMemo(() => {
    const historicalNational = detailData?.historis_nasional || [];
    const byReferenceDate = historicalNational.find(
      (r) => r?.tanggal === FIXED_REFERENCE_DATE,
    );
    if (byReferenceDate?.harga != null) {
      return byReferenceDate.harga;
    }

    const s = stats.find((x) => x.komoditas === selectedKomoditasName);
    return s?.harga_rata_nasional || null;
  }, [detailData, stats, selectedKomoditasName]);

  const alertsByKomoditas = useMemo(() => {
    if (!selKomoditas || !alerts?.length) return [];
    return alerts.filter((a) => a.komoditas === selectedKomoditasName);
  }, [alerts, selKomoditas, selectedKomoditasName]);

  const alertNaikCount = alertsByKomoditas.filter(
    (a) => a.kenaikan_pct > 10,
  ).length;
  const alertWarnCount = alertsByKomoditas.filter(
    (a) => a.kenaikan_pct >= 5 && a.kenaikan_pct <= 10,
  ).length;

  const mapData = useMemo(() => {
    const isThirtyDays = predPeriod === "30";
    return (semuaProv || []).map((r) => ({
      name: r.provinsi,
      harga: r.harga_sekarang,
      prediksi: isThirtyDays ? r.prediksi_30h : r.prediksi_7h,
      changePct: isThirtyDays ? r.ubah_30_pct : r.ubah_7_pct,
    }));
  }, [semuaProv, predPeriod]);

  const ewsAlerts = useMemo(() => {
    const isThirtyDays = predPeriod === "30";
    return (semuaProv || [])
      .map((r) => {
        const pct = Number(isThirtyDays ? r.ubah_30_pct : r.ubah_7_pct) || 0;
        const pred = isThirtyDays ? r.prediksi_30h : r.prediksi_7h;
        return {
          provinsi: r.provinsi,
          komoditas: selectedKomoditasName,
          harga_sekarang: r.harga_sekarang,
          prediksi_7h: r.prediksi_7h,
          prediksi_30h: r.prediksi_30h,
          kenaikan_pct: pct,
          risk_level:
            Math.abs(pct) >= 20
              ? "CRITICAL"
              : Math.abs(pct) >= 10
                ? "HIGH"
                : Math.abs(pct) >= 5
                  ? "WATCH"
                  : "LOW",
          ai_reasoning:
            pct === 0
              ? `Harga ${selectedKomoditasName} di ${r.provinsi} diproyeksikan stabil pada horizon ${predPeriod} hari.`
              : `Harga ${selectedKomoditasName} di ${r.provinsi} diproyeksikan ${pct > 0 ? "naik" : "turun"} ${Math.abs(pct).toFixed(1)}% pada horizon ${predPeriod} hari (ke sekitar Rp${Number(pred || 0).toLocaleString("id-ID")}).`,
        };
      })
      .filter((a) => Math.abs(a.kenaikan_pct) >= 5)
      .sort((a, b) => Math.abs(b.kenaikan_pct) - Math.abs(a.kenaikan_pct));
  }, [semuaProv, predPeriod, selectedKomoditasName]);

  const formatTs = (d) =>
    d
      ? d.toLocaleTimeString("id-ID", { hour: "2-digit", minute: "2-digit" })
      : "-";

  const dismissGuideBanner = () => {
    setShowGuideBanner(false);
  };

  if (error) {
    return (
      <div>
        <div className="page-header">
          <h2>Dashboard</h2>
          <p>Monitoring harga pangan nasional</p>
        </div>
        <div className="error-state">
          <div className="error-icon">!</div>
          <h3>Tidak dapat terhubung ke server</h3>
          <p>{error}</p>
          <p style={{ marginTop: 8, fontSize: 12 }}>
            API yang dipakai: <code>{API_BASE}</code>
          </p>
        </div>
      </div>
    );
  }

  return (
    <div>
      {showGuideBanner && (
        <div
          className="dashboard-guide-banner"
          style={{
            marginBottom: 14,
            border: "1px solid #BFDBFE",
            background: "linear-gradient(90deg, #EFF6FF 0%, #F8FAFC 100%)",
            borderRadius: 12,
            padding: "12px 14px",
            display: "flex",
            justifyContent: "space-between",
            alignItems: "flex-start",
            gap: 12,
          }}
        >
          <div className="dashboard-guide-content" style={{ display: "flex", gap: 10 }}>
            <Info
              className="dashboard-guide-icon"
              size={16}
              color="#1D4ED8"
              style={{ marginTop: 2, flexShrink: 0 }}
            />
            <div>
              <div
                className="dashboard-guide-title"
                style={{
                  fontSize: 14,
                  fontWeight: 700,
                  color: "#0F172A",
                  marginBottom: 3,
                }}
              >
                Panduan Singkat Dashboard
              </div>
              <div className="dashboard-guide-text" style={{ fontSize: 12, color: "#334155", lineHeight: 1.5 }}>
                Pilih <strong>Komoditas</strong> dan{" "}
                <strong>Rentang Prediksi 7/30 hari</strong> di kanan atas.
                <strong> Peta Risiko</strong> menampilkan level risiko per
                provinsi, sedangkan
                <strong> Prediksi Harga</strong> menampilkan tren harga aktual
                dan proyeksi.
              </div>
            </div>
          </div>
          <button
            type="button"
            onClick={dismissGuideBanner}
            aria-label="Tutup panduan"
            style={{
              border: "none",
              background: "transparent",
              color: "#475569",
              cursor: "pointer",
              padding: 2,
              lineHeight: 1,
            }}
          >
            <X size={16} />
          </button>
        </div>
      )}

      <div
        className="dashboard-title-row"
        style={{
          display: "flex",
          alignItems: "flex-start",
          justifyContent: "space-between",
          marginBottom: 20,
          background: "#fcfcfc",
        }}
      >
        <div className="page-header" style={{ marginBottom: 0 }}>
          <div className="dashboard-title-line" style={{ display: "flex", alignItems: "center", gap: 12 }}>
            <h2>Pusat Komando Eksekutif PanganAI</h2>
            {komoditasList.length > 0 && (
              <span
                style={{
                  background: "#E2E8F0",
                  padding: "4px 10px",
                  borderRadius: 20,
                  fontSize: 12,
                  fontWeight: 600,
                  color: "#475569",
                }}
              >
                {komoditasList.length} Komoditas Aktif
              </span>
            )}
          </div>
          <p>Pemantauan dan Prediksi Pangan Nasional Berbasis AI</p>
        </div>
      </div>

      <div className="dashboard-summary-row flex items-center gap-2" style={{ marginBottom: 24 }}>
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
                footer={`${alertNaikCount} peringatan kritis`}
              />
              <MetricCard
                label="Komoditas Dipantau"
                value={komoditasList.length}
                icon={Package}
                color="#10B981"
                footer="Bawang Merah, Bawang Putih, Beras, Minyak, Cabai Merah, Telur Ayam"
              />
              <MetricCard
                label="Harga Nasional"
                value={avgNasional ? formatRupiahShort(avgNasional) : "-"}
                icon={DollarSign}
                color="#F97316"
                footer={selectedKomoditasName || "-"}
              />
            </>
          )}
        </div>

        <div
          className="dashboard-filter-panel"
          style={{
            display: "flex",
            flexDirection: "column",
            alignItems: "flex-end",
            gap: 8,
          }}
        >
          <div className="dashboard-filter-select-row" style={{ display: "flex", alignItems: "center", gap: 10 }}>
            <select
              className="filter-select"
              value={selKomoditas}
              onChange={(e) => setSelKomoditas(e.target.value)}
              style={{ minWidth: 280 }}
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
              ></div>
            )}
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
      </div>

      <div className="chart-card" style={{ marginBottom: 24 }}>
        <div className="chart-card-header">
          <div className="toggle-group">
            <button
              className={`toggle-btn-item${geoMode === "map" ? " active" : ""}`}
              onClick={() => setGeoMode("map")}
            >
              Peta Risiko
            </button>
            <button
              className={`toggle-btn-item${geoMode === "forecast" ? " active" : ""}`}
              onClick={() => setGeoMode("forecast")}
            >
              Harga Nasional
            </button>
          </div>
        </div>

        {loading || predChart.harian.length === 0 ? (
          <div className="skeleton" style={{ height: 340, borderRadius: 8 }} />
        ) : geoMode === "forecast" ? (
          <GrafikPrediksi
            historis={predChart.historis}
            prediksi={predChart.harian.slice(0, predPeriod === "30" ? 30 : 7)}
            komoditas={selectedKomoditasName}
            het={null}
            historyDays={45}
            tanggalHariIni={datasetMaxDate}
          />
        ) : (
          <IndonesiaMap
            data={mapData}
            komoditas={selectedKomoditasName}
            horizon={Number(predPeriod)}
            baseDate={datasetMaxDate}
            monitoredProvinces={provinsiList}
          />
        )}
      </div>

      {loading ? (
        <div
          className="skeleton"
          style={{ height: 400, borderRadius: 8, marginBottom: 24 }}
        />
      ) : (
        <AICommodityIntelligence
          alerts={alertsByKomoditas}
          selectedKomoditas={selectedKomoditasName}
          horizonDays={Number(predPeriod)}
          semuaProv={semuaProv}
          geoMode={geoMode}
          predChart={predChart}
        />
      )}

      {loading ? (
        <div
          className="skeleton"
          style={{ height: 400, borderRadius: 8, marginBottom: 24 }}
        />
      ) : (
        <>
          <div
            style={{
              marginBottom: 12,
              border: "1px solid #C7D2FE",
              background: "linear-gradient(90deg, #EEF2FF 0%, #F8FAFC 100%)",
              borderRadius: 10,
              padding: "10px 12px",
            }}
          >
            <div
              style={{
                fontSize: 13,
                fontWeight: 700,
                color: "#1E3A8A",
                marginBottom: 6,
              }}
            >
              Panduan Aksi Early Warning
            </div>
            <div style={{ fontSize: 12, color: "#334155", lineHeight: 1.6 }}>
              <strong>Intervensi Pasokan</strong>: lakukan operasi pasar,
              percepat distribusi dari wilayah surplus, dan koordinasi stok
              cadangan untuk meredam lonjakan harga.
              <br />
              <strong>Inspeksi Lapangan</strong>: validasi penyebab kenaikan di
              pasar/sentra produksi (pasokan, logistik, cuaca, dan rantai
              distribusi) lalu siapkan tindak lanjut cepat.
              <br />
              <strong>Monitor Lanjut</strong>: tingkatkan frekuensi pemantauan
              (intra-hari/harian), cek pergerakan harga antar pasar, dan
              siapkan skenario respons bila tren memburuk.
              <br />
              <strong>Pantau</strong>: pemantauan berkala harian pada komoditas
              dengan gejolak ringan agar tidak meningkat ke level risiko lebih
              tinggi.
            </div>
          </div>
          <EarlyWarningSystem
            alerts={ewsAlerts}
            horizonDays={Number(predPeriod)}
          />
        </>
      )}

      <DistributionOptimizer
        selectedKomoditas={selectedKomoditasName}
        horizonDays={Number(predPeriod)}
        semuaProv={semuaProv}
      />
    </div>
  );
}
