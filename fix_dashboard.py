import re

with open("frontend/src/pages/Dashboard.jsx", "r", encoding="utf-8") as f:
    content = f.read()

# 1. Imports
content = content.replace('import MetricCard from "../components/MetricCard";\nimport KpiCard from "../components/KpiCard";', 
'import KpiCard from "../components/KpiCard";')

content = content.replace('import AlertCard from "../components/AlertCard";',
'import AlertCard from "../components/AlertCard";\nimport { ShieldCheck } from "lucide-react";')

content = content.replace('import IndonesiaMap from "../components/IndonesiaMap";', '')
content = content.replace('import SectionWrapper from "../components/SectionWrapper";', 'import SectionWrapper from "../components/SectionWrapper";\nimport IndonesiaMap from "../components/IndonesiaMap";')

# 2. Add execKPI and topActions
use_memo_block = """  const forecastInsight = useMemo(() => {"""
new_use_memo_block = """  const execKPI = useMemo(() => {
    let statusNasional = 'AMAN';
    let statusColor = '#10B981';
    let statusIcon = ShieldCheck;
    
    if (alerts.some(a => a.kenaikan_pct > 15)) {
      statusNasional = 'KRITIS';
      statusColor = '#EF4444';
      statusIcon = AlertTriangle;
    } else if (alerts.some(a => a.kenaikan_pct >= 5)) {
      statusNasional = 'WASPADA';
      statusColor = '#F97316';
      statusIcon = AlertCircle;
    }

    const komoditasRisikoSet = new Set(alerts.filter(a => a.kenaikan_pct >= 5).map(a => a.komoditas));
    const provinsiPrioritasSet = new Set(alerts.filter(a => a.kenaikan_pct >= 5).map(a => a.provinsi));
    const aksiPrioritasCount = alerts.filter(a => a.kenaikan_pct >= 5).length;

    return {
      statusNasional,
      statusColor,
      statusIcon,
      komoditasRisiko: komoditasRisikoSet.size,
      provinsiPrioritas: provinsiPrioritasSet.size,
      aksiPrioritas: Math.min(aksiPrioritasCount, 5)
    };
  }, [alerts]);

  const topActions = useMemo(() => {
    return alerts
      .filter(a => a.kenaikan_pct >= 5)
      .sort((a, b) => b.kenaikan_pct - a.kenaikan_pct)
      .slice(0, 3)
      .map(a => {
        let level = a.kenaikan_pct > 15 ? 'KRITIS' : 'WASPADA';
        let action = a.kenaikan_pct > 15 ? 'Operasi Pasar & Percepatan Distribusi' : 'Intervensi Terbatas & Monitoring';
        let color = a.kenaikan_pct > 15 ? '#EF4444' : '#F97316';
        let bg = a.kenaikan_pct > 15 ? '#FEF2F2' : '#FFF7ED';
        return { ...a, level, action, color, bg };
      });
  }, [alerts]);

  const forecastInsight = useMemo(() => {"""
content = content.replace(use_memo_block, new_use_memo_block)

# 3. Replace the entire return (...) block
return_start = content.find("  return (\n    <div>")
if return_start != -1:
    new_return = """  return (
    <div>
      {/* ── Page Header ── */}
      <div style={{ display: "flex", alignItems: "flex-start", justifyContent: "space-between", marginBottom: 20, background: "#fcfcfc" }}>
        <div className="page-header" style={{ marginBottom: 0 }}>
          <h2>Dashboard</h2>
          <p>Monitoring harga pangan nasional — Data PIHPS Bank Indonesia</p>
        </div>
        <div style={{ display: "flex", alignItems: "center", gap: 10 }}>
          <select className="filter-select" value={selKomoditas} onChange={(e) => setSelKomoditas(e.target.value)} style={{ minWidth: 200 }}>
            {KOMODITAS_LIST.map((k) => <option key={k} value={k}>{k}</option>)}
          </select>
          {lastUpdated && (
            <div style={{ display: "flex", alignItems: "center", gap: 5, fontSize: 11, color: "var(--text-muted)" }}>
              <RefreshCw size={11} /> {formatTs(lastUpdated)}
            </div>
          )}
        </div>
      </div>

      {/* ── Section 1: Executive KPI Strip ── */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(220px, 1fr))', gap: 16, marginBottom: 24 }}>
        <div style={{ background: 'white', padding: 20, borderRadius: 12, border: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', gap: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: `${execKPI.statusColor}15`, color: execKPI.statusColor, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <execKPI.statusIcon size={24} />
          </div>
          <div>
            <div style={{ fontSize: 12, color: '#64748B', fontWeight: 600, marginBottom: 4 }}>STATUS NASIONAL</div>
            <div style={{ fontSize: 20, fontWeight: 800, color: execKPI.statusColor }}>{execKPI.statusNasional}</div>
          </div>
        </div>
        <div style={{ background: 'white', padding: 20, borderRadius: 12, border: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', gap: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: '#EFF6FF', color: '#3B82F6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Package size={24} />
          </div>
          <div>
            <div style={{ fontSize: 12, color: '#64748B', fontWeight: 600, marginBottom: 4 }}>KOMODITAS RISIKO TINGGI</div>
            <div style={{ fontSize: 20, fontWeight: 800, color: '#0F172A' }}>{execKPI.komoditasRisiko} Komoditas</div>
          </div>
        </div>
        <div style={{ background: 'white', padding: 20, borderRadius: 12, border: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', gap: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: '#EFF6FF', color: '#3B82F6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Map size={24} />
          </div>
          <div>
            <div style={{ fontSize: 12, color: '#64748B', fontWeight: 600, marginBottom: 4 }}>PROVINSI PRIORITAS</div>
            <div style={{ fontSize: 20, fontWeight: 800, color: '#0F172A' }}>{execKPI.provinsiPrioritas} Provinsi</div>
          </div>
        </div>
        <div style={{ background: 'white', padding: 20, borderRadius: 12, border: '1px solid #E2E8F0', display: 'flex', alignItems: 'center', gap: 16, boxShadow: '0 1px 3px rgba(0,0,0,0.05)' }}>
          <div style={{ width: 48, height: 48, borderRadius: 12, background: '#EFF6FF', color: '#3B82F6', display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
            <Briefcase size={24} />
          </div>
          <div>
            <div style={{ fontSize: 12, color: '#64748B', fontWeight: 600, marginBottom: 4 }}>AKSI PRIORITAS</div>
            <div style={{ fontSize: 20, fontWeight: 800, color: '#0F172A' }}>{execKPI.aksiPrioritas} Aksi</div>
          </div>
        </div>
      </div>

      {/* ── Section 2: Top Priority Actions Today ── */}
      {topActions.length > 0 && (
        <div style={{ marginBottom: 24 }}>
          <h3 style={{ fontSize: 16, fontWeight: 800, color: '#0F172A', marginBottom: 12, display: 'flex', alignItems: 'center', gap: 8 }}>
            <AlertTriangle size={18} color="#EF4444" /> Top Priority Actions Today
          </h3>
          <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(300px, 1fr))', gap: 16 }}>
            {topActions.map((action, i) => (
              <div key={i} style={{ background: 'white', padding: 16, borderRadius: 12, border: `1px solid ${action.color}40`, borderLeft: `4px solid ${action.color}`, boxShadow: '0 1px 3px rgba(0,0,0,0.05)', display: 'flex', flexDirection: 'column', gap: 8 }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'flex-start' }}>
                  <div>
                    <div style={{ fontSize: 15, fontWeight: 800, color: '#0F172A' }}>{action.komoditas}</div>
                    <div style={{ fontSize: 13, color: '#64748B', fontWeight: 600 }}>{action.provinsi}</div>
                  </div>
                  <div style={{ background: action.bg, color: action.color, padding: '4px 8px', borderRadius: 6, fontSize: 11, fontWeight: 800 }}>
                    {action.level}
                  </div>
                </div>
                <div style={{ fontSize: 13, color: '#1E293B', fontWeight: 600, marginTop: 4, display: 'flex', alignItems: 'center', gap: 6 }}>
                  <Target size={14} color="#3B82F6" /> {action.action}
                </div>
              </div>
            ))}
          </div>
        </div>
      )}

      {/* ── Section 3: Forecast Analysis ── */}
      <SectionWrapper
        icon={TrendingUp}
        title="Forecast Analysis"
        subtitle={selKomoditas}
        rightContent={
          <div className="toggle-group">
            <button className={`toggle-btn-item${predPeriod === "7" ? " active" : ""}`} onClick={() => setPredPeriod("7")}>7 Hari</button>
            <button className={`toggle-btn-item${predPeriod === "30" ? " active" : ""}`} onClick={() => setPredPeriod("30")}>30 Hari</button>
          </div>
        }
      >
        {loading || !forecastInsight || trendChartData.length === 0 ? (
          <div className="skeleton" style={{ height: 400, borderRadius: 8 }} />
        ) : (
          <div style={{ display: 'flex', flexDirection: 'column', gap: 24 }}>
            <div style={{ display: 'grid', gridTemplateColumns: 'repeat(auto-fit, minmax(200px, 1fr))', gap: 16 }}>
              <KpiCard label="HARGA SAAT INI" value={formatRupiah(forecastInsight.currentPrice)} />
              <KpiCard label="PREDIKSI HARGA" value={formatRupiah(forecastInsight.forecastPrice)} />
              <KpiCard label="ESTIMASI PERUBAHAN" value={`${forecastInsight.changePct > 0 ? '+' : ''}${forecastInsight.changePct.toFixed(1)}%`} trend={forecastInsight.changePct > 0 ? 'up' : forecastInsight.changePct < 0 ? 'down' : 'neutral'} trendText={forecastInsight.changePct > 0 ? 'Naik' : forecastInsight.changePct < 0 ? 'Turun' : 'Stabil'} />
              <KpiCard label="RENTANG WAKTU" value={`${forecastInsight.days} Hari`} />
            </div>

            <div style={{ display: 'flex', gap: 24, flexWrap: 'wrap' }}>
              <div style={{ flex: '1 1 60%', minWidth: 400 }}>
                <div style={{ padding: '20px', border: '1px solid #E2E8F0', borderRadius: 12, background: 'white' }}>
                  <div style={{ fontSize: 14, fontWeight: 700, color: '#0F172A', marginBottom: 16 }}>Forecast Analysis — {selKomoditas}</div>
                  <ResponsiveContainer width="100%" height={280}>
                    <LineChart data={trendChartData} margin={{ top: 5, right: 12, left: 0, bottom: 5 }}>
                      <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
                      <XAxis dataKey="tanggal" tickFormatter={formatTanggalShort} tick={{ fontSize: 10, fill: "#9CA3AF" }} interval="preserveStartEnd" minTickGap={50} />
                      <YAxis tickFormatter={formatRupiahShort} tick={{ fontSize: 10, fill: "#9CA3AF" }} width={65} />
                      <Tooltip formatter={(v) => formatRupiah(v)} labelFormatter={formatTanggalShort} />
                      <Legend wrapperStyle={{ fontSize: 12 }} />
                      <Line type="monotone" dataKey="aktual" name="Aktual" stroke="#3B82F6" strokeWidth={3} dot={false} connectNulls={false} />
                      <Line type="monotone" dataKey="prediksi" name="Prediksi" stroke="#F97316" strokeWidth={3} strokeDasharray="6 4" dot={false} connectNulls={false} />
                    </LineChart>
                  </ResponsiveContainer>
                </div>
              </div>

              <div style={{ flex: '1 1 30%', minWidth: 300, display: 'flex', flexDirection: 'column', gap: 16 }}>
                <div style={{ background: '#F8FAFC', padding: 20, borderRadius: 12, border: '1px solid #E2E8F0' }}>
                  <div style={{ fontSize: 12, fontWeight: 800, color: '#0F172A', letterSpacing: 0.5, marginBottom: 12, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <Activity size={16} color="#3B82F6" /> INSIGHT PREDIKSI
                  </div>
                  <div style={{ display: 'flex', flexDirection: 'column', gap: 12 }}>
                    <div>
                      <div style={{ fontSize: 11, color: '#64748B', fontWeight: 600 }}>ARAH HARGA</div>
                      <div style={{ fontSize: 14, fontWeight: 700, color: forecastInsight.trendDirColor }}>{forecastInsight.trendDir}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: 11, color: '#64748B', fontWeight: 600 }}>TINGKAT RISIKO</div>
                      <div style={{ fontSize: 14, fontWeight: 800, color: forecastInsight.riskColor }}>{forecastInsight.riskLevel}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: 11, color: '#64748B', fontWeight: 600 }}>DAMPAK</div>
                      <div style={{ fontSize: 13, fontWeight: 600, color: '#334155', lineHeight: 1.4 }}>{forecastInsight.impact}</div>
                    </div>
                    <div>
                      <div style={{ fontSize: 11, color: '#64748B', fontWeight: 600 }}>TINGKAT KEPERCAYAAN</div>
                      <div style={{ fontSize: 14, fontWeight: 800, color: '#0F172A' }}>{forecastInsight.confidence}%</div>
                    </div>
                  </div>
                </div>

                <div style={{ background: '#EFF6FF', padding: 20, borderRadius: 12, border: '1px solid #BFDBFE', flex: 1 }}>
                  <div style={{ fontSize: 12, fontWeight: 800, color: '#1D4ED8', letterSpacing: 0.5, marginBottom: 8, display: 'flex', alignItems: 'center', gap: 6 }}>
                    <AlertTriangle size={16} /> RINGKASAN AI
                  </div>
                  <div style={{ fontSize: 13, color: '#1E3A8A', lineHeight: 1.5, fontWeight: 600 }}>
                    {forecastInsight.reasoning}
                  </div>
                </div>
              </div>
            </div>
          </div>
        )}
      </SectionWrapper>

      {/* ── Section 4: Risk Map ── */}
      <SectionWrapper
        icon={MapPin}
        title="Peta Risiko Nasional"
        subtitle={`Heatmap Harga — ${selKomoditas}`}
      >
        <IndonesiaMap data={barData} komoditas={selKomoditas} />
      </SectionWrapper>

      {/* ── Section 5: Distribution Optimizer ── */}
      <DistributionOptimizer 
        komoditasList={KOMODITAS_LIST} 
        selKomoditas={selKomoditas} 
        onKomoditasChange={setSelKomoditas} 
        semuaProv={semuaProv} 
      />

      {/* ── Section 6: Early Warning System ── */}
      {loading ? (
        <div className="skeleton" style={{ height: 450, borderRadius: 12, marginBottom: 24 }} />
      ) : (
        <EarlyWarningSystem alerts={alerts} />
      )}

      {/* ── Section 7: Policy Recommendation Engine ── */}
      {loading ? (
        <div className="skeleton" style={{ height: 300, borderRadius: 12, marginBottom: 24 }} />
      ) : (
        <PolicyRecommendation alerts={alerts} />
      )}

      {/* ── Section 8: AI Commodity Intelligence ── */}
      {loading ? (
        <div className="skeleton" style={{ height: 300, borderRadius: 12 }} />
      ) : (
        <AICommodityIntelligence alerts={alerts} />
      )}
    </div>
  );
}
"""
    content = content[:return_start] + new_return

with open("frontend/src/pages/Dashboard.jsx", "w", encoding="utf-8") as f:
    f.write(content)

