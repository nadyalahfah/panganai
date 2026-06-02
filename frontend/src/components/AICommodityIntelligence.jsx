import React, { useState, useEffect, useMemo } from "react";
import {
  BrainCircuit,
  AlertTriangle,
  Lightbulb,
  ShieldAlert,
  Bot,
  Activity,
  RefreshCw,
} from "lucide-react";
import SectionWrapper from "./SectionWrapper";
import { getAIInsight } from "../services/aiInsightService";

function toNum(v) {
  const n = Number(v);
  return Number.isFinite(n) ? n : 0;
}

function classifyRisk(changePct) {
  const abs = Math.abs(toNum(changePct));
  if (abs >= 20) return "kritis";
  if (abs >= 10) return "berisiko_tinggi";
  if (abs >= 5) return "waspada";
  return "aman";
}

function formatRiskLabel(risk) {
  return {
    kritis: "Kritis",
    berisiko_tinggi: "Berisiko Tinggi",
    waspada: "Waspada",
    aman: "Aman",
  }[risk] || risk;
}

function formatDirection(changePct) {
  if (changePct > 0) return "naik";
  if (changePct < 0) return "turun";
  return "stabil";
}

function formatProvinceList(rows, limit = 5) {
  if (!rows.length) return "-";
  const shown = rows.slice(0, limit).map((row) => {
    const name = row.provinsi || row.name || "-";
    const direction = formatDirection(row._pct);
    return `${name} (${formatRiskLabel(row._risk)}, ${direction} ${Math.abs(row._pct).toFixed(2)}%)`;
  });
  const remaining = rows.length - shown.length;
  return remaining > 0 ? `${shown.join("; ")}; +${remaining} provinsi lain` : shown.join("; ");
}

const RANK = {
  kritis: 4,
  berisiko_tinggi: 3,
  waspada: 2,
  aman: 1,
};

function extractNationalContext(predChart, horizonDays) {
  const historis = Array.isArray(predChart?.historis) ? predChart.historis : [];
  const prediksi = Array.isArray(predChart?.harian) ? predChart.harian : [];
  if (!historis.length) {
    return {
      currentPrice: 0,
      previousPrice: 0,
      forecastPrice: 0,
      currentChangePct: 0,
      forecastChangePct: 0,
    };
  }

  const lastHist = historis[historis.length - 1] || {};
  const prevHist = historis[Math.max(0, historis.length - 2)] || lastHist;
  const forecastIdx = Math.max(0, Math.min((horizonDays || 7) - 1, prediksi.length - 1));
  const forecastRow = prediksi[forecastIdx] || prediksi[prediksi.length - 1] || {};

  const currentPrice = toNum(lastHist.harga ?? lastHist.nilai);
  const previousPrice = toNum(prevHist.harga ?? prevHist.nilai);
  const forecastPrice = toNum(
    forecastRow.harga ?? forecastRow.prediksi ?? forecastRow.nilai,
  );

  const currentChangePct =
    previousPrice > 0 ? ((currentPrice - previousPrice) / previousPrice) * 100 : 0;
  const forecastChangePct =
    currentPrice > 0 ? ((forecastPrice - currentPrice) / currentPrice) * 100 : 0;

  return {
    currentPrice,
    previousPrice,
    forecastPrice,
    currentChangePct,
    forecastChangePct,
  };
}

export default function AICommodityIntelligence({
  alerts,
  selectedKomoditas,
  horizonDays = 7,
  semuaProv = [],
  geoMode = "map",
  predChart = null,
}) {
  const [loading, setLoading] = useState(false);
  const [briefing, setBriefing] = useState(null);
  const [error, setError] = useState(null);
  const [refreshNonce, setRefreshNonce] = useState(0);

  // Cache to prevent re-generation delays
  const [cache, setCache] = useState({});

  useEffect(() => {
    if (!selectedKomoditas) return;
    if (geoMode !== "forecast" && !(semuaProv || []).length) {
      setBriefing(null);
      setError(null);
      setLoading(false);
      return;
    }

    const key = JSON.stringify({
      komoditas: selectedKomoditas,
      horizon: horizonDays,
      mode: geoMode,
      refreshNonce,
      alertsSize: alerts?.length || 0,
      provSize: semuaProv?.length || 0,
      histSize: predChart?.historis?.length || 0,
      predSize: predChart?.harian?.length || 0,
    });

    if (cache[key]) {
      setBriefing(cache[key]);
      setError(null);
      return;
    }

    let isMounted = true;

    async function loadBriefing() {
      setLoading(true);
      setError(null);

      try {
        const mapRows = (semuaProv || []).map((row) => {
          const pct =
            horizonDays === 30
              ? toNum(row.ubah_30_pct ?? row.kenaikan_pct)
              : toNum(row.ubah_7_pct ?? row.kenaikan_pct);
          return {
            ...row,
            provinsi: row.provinsi || row.name,
            harga_sekarang: row.harga_sekarang ?? row.harga,
            prediksi:
              horizonDays === 30
                ? row.prediksi_30h ?? row.prediksi
                : row.prediksi_7h ?? row.prediksi,
            _pct: pct,
            _risk: classifyRisk(pct),
          };
        });

        const alertRows = (alerts || []).map((a) => {
          const pct =
            horizonDays === 30
              ? toNum(a.ubah_30_pct ?? a.kenaikan_pct)
              : toNum(a.kenaikan_pct ?? a.ubah_7_pct);
          return {
            ...a,
            _pct: pct,
            _risk: classifyRisk(pct),
          };
        });

        const sourceRows = geoMode === "forecast" ? alertRows : mapRows;
        const enriched = sourceRows
          .map((a) => ({
            ...a,
            _pct: toNum(a._pct),
            _risk: a._risk || classifyRisk(a._pct),
          }))
          .sort((a, b) => {
            const rankDiff = RANK[b._risk] - RANK[a._risk];
            if (rankDiff !== 0) return rankDiff;
            return Math.abs(b._pct) - Math.abs(a._pct);
          });

        const critical = enriched.filter((x) => x._risk === "kritis");
        const high = enriched.filter((x) => x._risk === "berisiko_tinggi");
        const watch = enriched.filter((x) => x._risk === "waspada");
        const safe = enriched.filter((x) => x._risk === "aman");

        let contextMode = geoMode === "forecast" ? "harga_nasional" : "peta_risiko";
        let payload;

        if (contextMode === "peta_risiko") {
          const primary = enriched[0];
          const secondary =
            (primary?._risk === "kritis" && high[0]) ||
            (primary?._risk !== "kritis" && enriched[1]) ||
            null;

          if (!primary) {
            throw new Error("Tidak ada data risiko untuk komoditas terpilih");
          }

          const contextLines = [
            "Konteks tampilan saat ini: PETA RISIKO provinsi. Analisis wajib merujuk ke warna/status pada peta, bukan daftar alert global.",
            `Horizon prediksi: ${horizonDays} hari.`,
            "Legenda visual peta: Aman <5%, Waspada 5-10%, Berisiko Tinggi 10-20%, Kritis >20% perubahan absolut.",
            `Jumlah provinsi sesuai peta: Kritis ${critical.length}, Berisiko Tinggi ${high.length}, Waspada ${watch.length}, Aman ${safe.length}.`,
            `Provinsi Kritis pada peta: ${formatProvinceList(critical)}.`,
            `Provinsi Berisiko Tinggi pada peta: ${formatProvinceList(high)}.`,
            `Provinsi Waspada pada peta: ${formatProvinceList(watch)}.`,
            `Provinsi Aman dominan pada peta: ${formatProvinceList(safe, 4)}.`,
            `Kasus utama berdasarkan warna/risiko peta: ${primary.provinsi || primary.name || "-"} (${formatRiskLabel(primary._risk)}, ${formatDirection(primary._pct)} ${Math.abs(primary._pct).toFixed(2)}%).`,
            secondary
              ? `Kasus kedua berdasarkan peta: ${secondary.provinsi || secondary.name || "-"} (${formatRiskLabel(secondary._risk)}, ${formatDirection(secondary._pct)} ${Math.abs(secondary._pct).toFixed(2)}%).`
              : "Tidak ada kasus kedua prioritas tinggi.",
            "Gaya output PETA RISIKO yang harus dipertahankan:",
            "summary: satu paragraf eksekutif. Awali dengan arah prediksi komoditas dan horizon, lalu frasa 'Berdasarkan peta risiko,' serta distribusi kategori dan contoh provinsi utama.",
            "risk: satu paragraf. Fokus pada provinsi prioritas dan volatilitas/tekanan harga; jangan melebar ke narasi nasional yang tidak terlihat di peta.",
            "recommendation: satu paragraf praktis. Sarankan pemantauan intensif di provinsi Berisiko Tinggi/Kritis, validasi lapangan, dan pengawasan berkala untuk Waspada.",
            "Gunakan istilah kategori persis: Kritis, Berisiko Tinggi, Waspada, Aman.",
            "Instruksi output: sebutkan distribusi warna/status peta secara faktual. Jangan menyebut jumlah provinsi yang tidak sama dengan data peta.",
            "Jangan mengklaim penyebab eksternal spesifik seperti gangguan pasokan/cuaca bila tidak ada di data; gunakan frasa kehati-hatian seperti indikasi tekanan harga.",
            "Jika ada provinsi turun tetapi masuk risiko tinggi/kritis, jelaskan sebagai volatilitas/penurunan tajam, bukan lonjakan harga.",
            refreshNonce > 0 ? `Permintaan refresh manual ke-${refreshNonce}.` : "",
          ];

          payload = {
            commodity: selectedKomoditas,
            current_price: toNum(primary.harga_sekarang ?? primary.harga),
            forecast_price:
              horizonDays === 30
                ? toNum(primary.prediksi_30h ?? primary.prediksi)
                : toNum(primary.prediksi_7h ?? primary.prediksi),
            change_percent: toNum(primary._pct),
            recommendation_data: contextLines.join("\n"),
          };
        } else {
          const national = extractNationalContext(predChart, horizonDays);
          const contextLines = [
            "Konteks tampilan saat ini: GRAFIK HARGA NASIONAL.",
            `Horizon prediksi: ${horizonDays} hari.`,
            `Harga saat ini: ${national.currentPrice}. Harga sebelumnya: ${national.previousPrice}.`,
            `Perubahan hari ini terhadap hari sebelumnya: ${national.currentChangePct.toFixed(2)}%.`,
            `Harga prediksi horizon: ${national.forecastPrice}. Perubahan prediksi vs harga saat ini: ${national.forecastChangePct.toFixed(2)}%.`,
            `Ringkasan risiko provinsi pendukung (untuk konteks): Kritis ${critical.length}, Berisiko Tinggi ${high.length}, Waspada ${watch.length}, Aman ${safe.length}.`,
            "Instruksi output ringkasan: jelaskan kenapa harga hari ini naik/turun/stabil, bagaimana arah prediksi, risiko yang mungkin muncul, lalu rekomendasi tindakan.",
            refreshNonce > 0 ? `Permintaan refresh manual ke-${refreshNonce}.` : "",
          ];

          payload = {
            commodity: selectedKomoditas,
            current_price: national.currentPrice,
            forecast_price: national.forecastPrice,
            change_percent: national.forecastChangePct,
            recommendation_data: contextLines.join("\n"),
          };
        }

        const result = await getAIInsight(payload);

        if (isMounted) {
          setCache((prev) => ({ ...prev, [key]: result }));
          setBriefing(result);
        }
      } catch (err) {
        if (isMounted) {
          console.error("AI Insight Error:", err);
          setError("Ringkasan AI sementara tidak tersedia.");
        }
      } finally {
        if (isMounted) {
          setLoading(false);
        }
      }
    }

    loadBriefing();

    return () => {
      isMounted = false;
    };
  }, [selectedKomoditas, horizonDays, geoMode, alerts, semuaProv, predChart, cache, refreshNonce]);

  if (!selectedKomoditas) return null;

  return (
    <SectionWrapper
      icon={Bot}
      title="Ringkasan Eksekutif AI"
      badge="AZURE OPENAI"
      subtitle="Dihasilkan oleh Azure OpenAI GPT-4.1-mini"
      rightContent={
        <button
          type="button"
          onClick={() => setRefreshNonce((v) => v + 1)}
          disabled={loading}
          style={{
            display: "inline-flex",
            alignItems: "center",
            gap: 6,
            border: "1px solid #CBD5E1",
            background: loading ? "#F1F5F9" : "#FFFFFF",
            color: "#0F172A",
            borderRadius: 8,
            padding: "8px 12px",
            fontSize: 12,
            fontWeight: 700,
            cursor: loading ? "not-allowed" : "pointer",
          }}
        >
          <RefreshCw size={14} className={loading ? "animate-spin" : ""} />
          Refresh Rekomendasi
        </button>
      }
    >
      <div style={{ minHeight: 300 }}>
        {loading ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            <div
              style={{
                fontSize: 14,
                color: "#64748B",
                fontStyle: "italic",
                display: "flex",
                alignItems: "center",
                gap: 8,
              }}
            >
              <Activity size={16} className="animate-pulse" /> Menyusun
              Ringkasan Eksekutif AI...
            </div>
            <div
              className="skeleton"
              style={{ height: 100, borderRadius: 8 }}
            />
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "1fr 1fr",
                gap: 20,
              }}
            >
              <div
                className="skeleton"
                style={{ height: 160, borderRadius: 8 }}
              />
              <div
                className="skeleton"
                style={{ height: 160, borderRadius: 8 }}
              />
            </div>
          </div>
        ) : error ? (
          <div
            style={{
              padding: 40,
              textAlign: "center",
              color: "#EF4444",
              fontSize: 15,
              background: "#FEF2F2",
              borderRadius: 10,
              border: "1px solid #FECACA",
            }}
          >
            <AlertTriangle size={24} style={{ margin: "0 auto 12px auto" }} />
            {error}
          </div>
        ) : briefing ? (
          <div style={{ display: "flex", flexDirection: "column", gap: 24 }}>
            {/* Ringkasan Eksekutif */}
            <div
              style={{
                background: "#F0F9FF",
                border: "1px solid #BAE6FD",
                padding: 24,
                borderRadius: 10,
              }}
            >
              <div
                style={{
                  display: "flex",
                  alignItems: "center",
                  gap: 8,
                  marginBottom: 12,
                }}
              >
                <BrainCircuit size={18} color="#0284C7" />
                <span
                  style={{ fontSize: 13, color: "#0369A1", fontWeight: 800 }}
                >
                  RINGKASAN
                </span>
              </div>
              <div
                style={{
                  fontSize: 15,
                  color: "#0C4A6E",
                  lineHeight: 1.6,
                  fontWeight: 500,
                }}
              >
                {briefing.summary}
              </div>
            </div>

            {/* 2 Columns */}
            <div
              style={{
                display: "grid",
                gridTemplateColumns: "repeat(auto-fit, minmax(300px, 1fr))",
                gap: 20,
              }}
            >
              {/* Faktor Risiko */}
              <div
                style={{
                  background: "#FEF2F2",
                  padding: 20,
                  borderRadius: 10,
                  border: "1px solid #FECACA",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    marginBottom: 16,
                  }}
                >
                  <ShieldAlert size={18} color="#EF4444" />
                  <span
                    style={{ fontSize: 13, color: "#B91C1C", fontWeight: 800 }}
                  >
                    RISIKO
                  </span>
                </div>
                <div
                  style={{ fontSize: 14, color: "#7F1D1D", lineHeight: 1.5 }}
                >
                  {briefing.risk}
                </div>
              </div>

              {/* Rekomendasi Tindakan */}
              <div
                style={{
                  background: "#F0FDF4",
                  padding: 20,
                  borderRadius: 10,
                  border: "1px solid #BBF7D0",
                }}
              >
                <div
                  style={{
                    display: "flex",
                    alignItems: "center",
                    gap: 8,
                    marginBottom: 16,
                  }}
                >
                  <Lightbulb size={18} color="#10B981" />
                  <span
                    style={{ fontSize: 13, color: "#14532D", fontWeight: 800 }}
                  >
                    REKOMENDASI
                  </span>
                </div>
                <div
                  style={{ fontSize: 14, color: "#14532D", lineHeight: 1.5 }}
                >
                  {briefing.recommendation}
                </div>
              </div>
            </div>
          </div>
        ) : null}
      </div>
    </SectionWrapper>
  );
}
