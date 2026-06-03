import re

with open(r'd:\2026\pangan-ai\panganai\frontend\src\components\DistributionOptimizer.jsx', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Update getSmartReasoning
old_smart_reasoning = re.search(r'const getSmartReasoning = .*?\};', content, flags=re.DOTALL)
if old_smart_reasoning:
    new_smart_reasoning = """const getSmartReasoning = (commodity, province, forecastPct, riskLevel, currentPrice) => {
    const c = (commodity || '').toLowerCase();
    const p = province || '';
    const pct = forecastPct ? forecastPct.toFixed(1) : 0;
    
    const WESTERN = ['aceh', 'sumatera utara', 'sumatera barat', 'riau', 'jambi', 'sumatera selatan', 'bengkulu', 'lampung'];
    const JAVA = ['dki jakarta', 'jawa barat', 'jawa tengah', 'di yogyakarta', 'jawa timur', 'banten'];
    const EASTERN = ['ntt', 'nusa tenggara timur', 'maluku', 'maluku utara', 'papua', 'papua barat', 'papua tengah', 'papua selatan', 'papua pegunungan'];
    const KALIMANTAN = ['kalimantan barat', 'kalimantan tengah', 'kalimantan selatan', 'kalimantan timur', 'kalimantan utara'];
    const SULAWESI = ['sulawesi utara', 'gorontalo', 'sulawesi tengah', 'sulawesi barat', 'sulawesi selatan', 'sulawesi tenggara'];
    
    const pLow = p.toLowerCase();
    let geoMod = "";
    if (WESTERN.includes(pLow)) {
      geoMod = "Fokus pada pemantauan distribusi antar-kabupaten dan stabilitas pasokan pasar utama.";
    } else if (JAVA.includes(pLow) || pLow === 'jakarta') {
      geoMod = "Wilayah merupakan pusat konsumsi nasional. Monitoring distribusi dan kesiapan stok pasar strategis direkomendasikan.";
    } else if (EASTERN.includes(pLow)) {
      geoMod = "Wilayah memiliki tantangan logistik yang lebih tinggi. Evaluasi distribusi antar-pulau dan kesiapan pasokan regional direkomendasikan.";
    } else if (KALIMANTAN.some(k => pLow.includes(k) || pLow === 'kalimantan')) {
      geoMod = "Monitoring rantai distribusi lintas wilayah dan ketersediaan stok regional direkomendasikan.";
    } else if (SULAWESI.some(s => pLow.includes(s) || pLow === 'sulawesi' || pLow === 'gorontalo')) {
      geoMod = "Perlu pemantauan distribusi regional dan koordinasi pasokan antar-provinsi.";
    }
    
    let priceStr = "";
    if (currentPrice) {
      priceStr = `Harga saat ini Rp${currentPrice.toLocaleString('id-ID')}/kg dengan proyeksi kenaikan ${pct}%.`;
    } else {
      priceStr = `Proyeksi kenaikan mencapai ${pct}%.`;
    }

    let actionStr = "";
    if (riskLevel === 'High Risk Alert' || riskLevel === 'Intervensi Segera') {
      if (c.includes('cabai')) {
        actionStr = `Prioritas tindakan:\\n• Verifikasi stok distributor utama\\n• Koordinasi pasokan antar wilayah\\n• Monitoring sentra produksi terdekat`;
      } else if (c.includes('bawang')) {
        actionStr = `Prioritas tindakan:\\n• Pengecekan stok gudang penyimpanan\\n• Operasi pasar komoditas bawang\\n• Percepatan distribusi dari sentra panen`;
      } else if (c.includes('beras')) {
        actionStr = `Prioritas tindakan:\\n• Evaluasi stok Bulog\\n• Pertimbangkan operasi pasar\\n• Monitoring distribusi antar wilayah`;
      } else if (c.includes('telur') || c.includes('ayam')) {
        actionStr = `Prioritas tindakan:\\n• Monitoring pasokan peternak\\n• Evaluasi distribusi regional\\n• Penguatan koordinasi rantai pasok`;
      } else if (c.includes('minyak')) {
        actionStr = `Prioritas tindakan:\\n• Pengawasan stok distributor D1/D2\\n• Pemantauan kepatuhan HET\\n• Inspeksi pasar berkelanjutan`;
      } else {
        actionStr = `Intervensi segera direkomendasikan untuk menstabilkan gejolak harga.`;
      }
    } else if (riskLevel === 'Medium Risk Alert' || riskLevel === 'Monitoring Prioritas') {
      if (c.includes('cabai') || c.includes('bawang')) {
        actionStr = `Sinyal tekanan harga Hortikultura mulai muncul.\\nDisarankan pemantauan distribusi dan evaluasi pasokan.`;
      } else if (c.includes('beras')) {
        actionStr = `Terindikasi peningkatan tekanan harga.\\nEvaluasi ketersediaan stok dan distribusi direkomendasikan.`;
      } else if (c.includes('telur') || c.includes('ayam')) {
        actionStr = `Tekanan harga protein mulai terdeteksi.\\nPemantauan distribusi dan stok direkomendasikan.`;
      } else {
        actionStr = `Sinyal tekanan harga mulai muncul.\\nPemantauan distribusi dan evaluasi stok direkomendasikan.`;
      }
    } else {
      actionStr = `Kondisi pasar relatif stabil.\\nPemantauan berkala tetap direkomendasikan.`;
    }
    
    return `${priceStr}\\n\\n${actionStr}\\n\\n${geoMod}`;
  };"""
    content = content.replace(old_smart_reasoning.group(0), new_smart_reasoning)

# 2. Update finalDesc call
content = content.replace(
    "let finalDesc = getSmartReasoning(a.commodity || a.komoditas, a.province || a.provinsi, a.forecast_change_pct, displayLevel);",
    "let finalDesc = getSmartReasoning(a.commodity || a.komoditas, a.province || a.provinsi, a.forecast_change_pct, displayLevel, a.current_price);"
)

# 3. Fix Map Rendering
old_map = """            {/* Warning Markers (Market Alerts) */}
            {isAlertMode && activeData && PROV_COORDS[activeData.provinsi] && (
              <g>
                <circle 
                  cx={PROV_COORDS[activeData.provinsi][0]} 
                  cy={PROV_COORDS[activeData.provinsi][1]} 
                  r="6" fill={activeData.color} stroke="white" strokeWidth="2" 
                />
                <circle 
                  cx={PROV_COORDS[activeData.provinsi][0]} 
                  cy={PROV_COORDS[activeData.provinsi][1]} 
                  r="16" fill={activeData.color} opacity="0.3" className="pulse-anim"
                />
                <circle 
                  cx={PROV_COORDS[activeData.provinsi][0]} 
                  cy={PROV_COORDS[activeData.provinsi][1]} 
                  r="24" fill={activeData.color} opacity="0.1" className="pulse-anim"
                />
              </g>
            )}"""

new_map = """            {/* Warning Markers (Market Alerts) */}
            {isAlertMode && alerts.map((alt, idx) => {
              if (!PROV_COORDS[alt.provinsi]) return null;
              const [cx, cy] = PROV_COORDS[alt.provinsi];
              const isActive = idx === activeRec;
              return (
                <g key={idx} onClick={() => handleMarkerClick(idx)} style={{ cursor: 'pointer', transition: 'all 0.3s' }}>
                  {isActive && (
                    <circle cx={cx} cy={cy} r={24} fill={alt.color} opacity={0.1} className="pulse-anim" style={{ pointerEvents: 'none' }} />
                  )}
                  {isActive && (
                    <circle cx={cx} cy={cy} r={16} fill={alt.color} opacity={0.3} className="pulse-anim" style={{ pointerEvents: 'none' }} />
                  )}
                  <circle cx={cx} cy={cy} r={isActive ? 6 : 4} fill={alt.color} opacity={isActive ? 1 : 0.7} stroke={isActive ? "white" : "none"} strokeWidth={isActive ? 2 : 0} className="marker-hover" />
                </g>
              );
            })}"""

content = content.replace(old_map, new_map)

# 4. Fix Accordion Cards
old_card_regex = r'\{isAlertMode && alerts\.map\(\(alt, i\) => \(\s*<div\s*key=\{alt\.id\}.*?\}\)\s*\}\s*\)\}'
new_card = """{isAlertMode && alerts.map((alt, i) => {
          const isActive = activeRec === i;
          const isFlashing = flashingCard === i;
          return (
          <div 
            id={`alert-card-${i}`}
            key={alt.id || i} 
            className={`rec-card ${isActive ? 'active' : ''}`}
            onClick={() => setActiveRec(i)}
            style={{ 
              padding: 16, background: 'white', borderRadius: 8, 
              border: `1px solid ${isActive ? alt.color : (isFlashing ? alt.color : '#E5E7EB')}`,
              cursor: 'pointer', transition: 'all 0.3s',
              boxShadow: isFlashing ? `0 0 10px ${alt.color}40` : (isActive ? `0 4px 6px -1px ${alt.color}33` : '0 1px 2px rgba(0,0,0,0.05)')
            }}
          >
            <div style={{ display: 'flex', justifyContent: 'space-between', marginBottom: isActive ? 12 : 0, transition: 'all 0.3s' }}>
              <div style={{ display: 'flex', alignItems: 'center', gap: 8 }}>
                <AlertCircle size={16} color={alt.color} />
                <div style={{ color: '#0F172A' }}>
                  <div style={{ fontSize: 10, color: '#64748B', fontWeight: 'bold' }}>{alt.komoditas}</div>
                  <div style={{ fontWeight: isActive ? 'bold' : 'normal', fontSize: 14 }}>{alt.provinsi}</div>
                </div>
              </div>
              <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', fontSize: 11, fontWeight: 'bold', padding: '2px 8px', borderRadius: 12, background: `${alt.color}15`, color: alt.color }}>{alt.risk_level}</div>
            </div>

            {isActive && (
              <>
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 8, marginBottom: 12 }}>
                  <div style={{ background: '#F8FAFC', padding: 8, borderRadius: 6 }}>
                    <div style={{ fontSize: 11, color: '#64748B' }}>Harga Saat Ini</div>
                    <div style={{ fontSize: 14, fontWeight: 'bold', color: '#0F172A' }}>{formatRupiahShort(alt.current_price)}/kg</div>
                  </div>
                  <div style={{ background: '#F8FAFC', padding: 8, borderRadius: 6 }}>
                    <div style={{ fontSize: 11, color: '#64748B' }}>Dampak Prediksi</div>
                    <div style={{ fontSize: 14, fontWeight: 'bold', color: alt.color }}>+{alt.forecast_change_pct.toFixed(1)}%</div>
                  </div>
                </div>

                <div style={{ fontSize: 13, color: '#475569', lineHeight: 1.5, background: '#F1F5F9', padding: 12, borderRadius: 8, whiteSpace: 'pre-line' }}>
                  {alt.desc}
                </div>
              </>
            )}
          </div>
        )})}"""
content = re.sub(old_card_regex, new_card, content, flags=re.DOTALL)

with open(r'd:\2026\pangan-ai\panganai\frontend\src\components\DistributionOptimizer.jsx', 'w', encoding='utf-8') as f:
    f.write(content)
print("SUCCESS")
