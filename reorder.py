import re

with open("frontend/src/pages/Dashboard.jsx", "r", encoding="utf-8") as f:
    code = f.read()

return_start = code.find("  return (\n    <div>")
return_end = code.find("  );\n}", return_start) + 6

top = code[:return_start]

new_return = """  return (
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
          <h2>PanganAI Executive Command Center</h2>
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

      {/* ── SECTION 2: Early Warning System ── */}
      {loading ? (
        <div className="skeleton" style={{ height: 400, borderRadius: 8, marginBottom: 24 }} />
      ) : (
        <EarlyWarningSystem alerts={alerts} />
      )}

      {/* ── SECTION 3: Commodity Price Forecast ── */}
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

      {/* ── SECTION 4: Supply & Distribution Optimizer ── */}
      <DistributionOptimizer 
        komoditasList={KOMODITAS_LIST} 
        selKomoditas={selKomoditas} 
        onKomoditasChange={setSelKomoditas} 
        semuaProv={semuaProv} 
      />

      {/* ── SECTION 5: Policy Recommendation Engine ── */}
      {loading ? (
        <div className="skeleton" style={{ height: 400, borderRadius: 8, marginBottom: 24 }} />
      ) : (
        <PolicyRecommendation alerts={alerts} />
      )}

      {/* ── SECTION 6: AI Commodity Intelligence ── */}
      {loading ? (
        <div className="skeleton" style={{ height: 400, borderRadius: 8 }} />
      ) : (
        <AICommodityIntelligence alerts={alerts} />
      )}
    </div>
  );
}
"""

with open("frontend/src/pages/Dashboard.jsx", "w", encoding="utf-8") as f:
    f.write(top + new_return)
