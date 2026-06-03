import re

path = r'd:\2026\pangan-ai\panganai\frontend\src\components\DistributionOptimizer.jsx'
with open(path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Smart reasoning function
smart_reasoning_fn = """
  const getSmartReasoning = (commodity, province, forecastPct, riskLevel) => {
    const c = (commodity || '').toLowerCase();
    const p = province || '';
    const pct = forecastPct ? forecastPct.toFixed(1) : 0;
    
    if (riskLevel === 'High Risk Alert' || riskLevel === 'Intervensi Segera') {
      if (c.includes('cabai') || c.includes('merah') || c.includes('rawit')) {
        return `Prediksi kenaikan harga ${commodity} di ${p}\\nmencapai ${pct}%.\\n\\nPrioritas tindakan:\\n\\n• Verifikasi stok distributor utama\\n• Koordinasi pasokan antar wilayah\\n• Monitoring sentra produksi terdekat`;
      } else if (c.includes('beras')) {
        return `Potensi tekanan harga ${commodity}\\ndi ${p} mencapai ${pct}%.\\n\\nPrioritas tindakan:\\n\\n• Evaluasi stok Bulog\\n• Pertimbangkan operasi pasar\\n• Monitoring distribusi antar wilayah`;
      } else if (c.includes('telur') || c.includes('ayam')) {
        return `Potensi kenaikan harga ${commodity}\\ndi ${p} mencapai ${pct}%.\\n\\nPrioritas tindakan:\\n\\n• Monitoring pasokan peternak\\n• Evaluasi distribusi regional\\n• Penguatan koordinasi rantai pasok`;
      } else {
        return `Prediksi kenaikan harga mencapai ${pct}%.\\nIntervensi segera direkomendasikan.`;
      }
    } else if (riskLevel === 'Medium Risk Alert' || riskLevel === 'Monitoring Prioritas') {
      if (c.includes('cabai') || c.includes('merah') || c.includes('rawit')) {
        return `Sinyal tekanan harga mulai muncul pada ${commodity}\\ndi ${p}.\\n\\nDisarankan pemantauan distribusi dan evaluasi pasokan.`;
      } else if (c.includes('beras')) {
        return `Terindikasi peningkatan tekanan harga.\\n\\nEvaluasi ketersediaan stok dan distribusi direkomendasikan.`;
      } else if (c.includes('telur') || c.includes('ayam')) {
        return `Tekanan harga mulai terdeteksi.\\n\\nPemantauan distribusi dan stok direkomendasikan.`;
      } else {
        return `Sinyal tekanan harga mulai muncul.\\nPemantauan distribusi dan evaluasi stok direkomendasikan.`;
      }
    } else {
      if (c.includes('beras')) return `Kondisi pasokan dan harga relatif stabil.`;
      if (c.includes('telur') || c.includes('ayam')) return `Kondisi pasar relatif terkendali.`;
      return `Kondisi pasar relatif stabil.\\nPemantauan berkala tetap direkomendasikan.`;
    }
  };
"""

content = re.sub(
    r'(export default function DistributionOptimizer.*?{)',
    r'\1\n' + smart_reasoning_fn,
    content,
    flags=re.DOTALL
)

old_mapping = """      let finalDesc = '';
      if (a.risk_level === 'High Risk Alert') {
        finalDesc = `Prediksi kenaikan harga mencapai ${a.forecast_change_pct.toFixed(1)}%. Intervensi segera direkomendasikan untuk mencegah ketidakstabilan pasar.`;
      } else if (a.risk_level === 'Medium Risk Alert') {
        finalDesc = `Sinyal tekanan harga mulai muncul. Pemantauan distribusi dan evaluasi stok direkomendasikan.`;
      } else {
        finalDesc = `Kondisi pasar masih terkendali, namun pemantauan berkala disarankan.`;
      }

      return {
        id: i,
        provinsi: a.province || '',
        risk_level: displayLevel,
        color: color,
        forecast_change_pct: a.forecast_change_pct,
        current_price: a.current_price,
        forecast_price: a.forecast_price,
        desc: finalDesc
      };"""

new_mapping = """      let finalDesc = getSmartReasoning(a.commodity || a.komoditas, a.province || a.provinsi, a.forecast_change_pct, displayLevel);
      return {
        id: i,
        komoditas: a.commodity || a.komoditas || 'Komoditas',
        provinsi: a.province || a.provinsi || '',
        risk_level: displayLevel,
        color: color,
        forecast_change_pct: a.forecast_change_pct,
        current_price: a.current_price,
        forecast_price: a.forecast_price,
        desc: finalDesc
      };"""
content = content.replace(old_mapping, new_mapping)

state_logic = """  const [activeRec, setActiveRec] = useState(0);"""
new_state_logic = """  const [activeRec, setActiveRec] = useState(0);
  const [flashingCard, setFlashingCard] = useState(null);

  const handleMarkerClick = (idx) => {
    setActiveRec(idx);
    setFlashingCard(idx);
    setTimeout(() => setFlashingCard(null), 1500);
    const card = document.getElementById(`alert-card-${idx}`);
    if (card) {
      card.scrollIntoView({ behavior: 'smooth', block: 'center' });
    }
  };"""
content = content.replace(state_logic, new_state_logic)

new_map_marker = """            {/* Warning Markers (Market Alerts) */}
            {isAlertMode && alerts.map((alt, idx) => {
              if (!PROV_COORDS[alt.provinsi]) return null;
              const [cx, cy] = PROV_COORDS[alt.provinsi];
              const isActive = idx === activeRec;
              return (
                <g key={idx} onClick={() => handleMarkerClick(idx)} style={{ cursor: 'pointer', transition: 'all 0.3s' }}>
                  {isActive && (
                    <circle cx={cx} cy={cy} r={12} fill={alt.color} opacity={0.2} className="pulse-fast" style={{ pointerEvents: 'none' }} />
                  )}
                  <circle cx={cx} cy={cy} r={isActive ? 6 : 4} fill={alt.color} opacity={isActive ? 1 : 0.7} className="marker-hover" />
                </g>
              );
            })}"""
content = re.sub(
    r'\{\/\* Warning Markers \(Market Alerts\) \*\/\}.*?<\/g>\s*\}\)',
    new_map_marker,
    content,
    flags=re.DOTALL
)

old_alert_card = """            {isAlertMode && alerts.map((alt, i) => (
              <div key={i} className={`rec-card ${activeRec === i ? 'active' : ''}`} onClick={() => setActiveRec(i)}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: 12 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{ width: 36, height: 36, borderRadius: 10, background: `${alt.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <AlertCircle size={16} color={alt.color} />
                    </div>
                    <div style={{ color: '#0F172A' }}>
                      <div style={{ fontSize: 10, color: '#64748B', fontWeight: 'normal' }}>Wilayah Prioritas Intervensi</div>
                      {alt.provinsi}
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', fontSize: 11, fontWeight: 'bold', padding: '2px 8px', borderRadius: 12, background: `${alt.color}15`, color: alt.color }}>
                    {alt.risk_level}
                  </div>
                </div>
                
                <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
                  <div style={{ background: '#F8FAFC', padding: 8, borderRadius: 6 }}>
                    <div style={{ fontSize: 11, color: '#64748B' }}>Harga Saat Ini</div>
                    <div style={{ fontSize: 14, fontWeight: 'bold', color: '#0F172A' }}>{formatRupiahShort(alt.current_price)}/kg</div>
                  </div>
                  <div style={{ background: '#F8FAFC', padding: 8, borderRadius: 6 }}>
                    <div style={{ fontSize: 11, color: '#64748B' }}>Dampak Prediksi (+7 Hari)</div>
                    <div style={{ fontSize: 14, fontWeight: 'bold', color: alt.color }}>+{alt.forecast_change_pct.toFixed(1)}%</div>
                  </div>
                </div>
                
                <div style={{ fontSize: 13, color: '#475569', background: '#F1F5F9', padding: 12, borderRadius: 8, lineHeight: 1.5 }}>
                  <span style={{ fontWeight: 600, color: '#0F172A', display: 'block', marginBottom: 4 }}>Rekomendasi Kebijakan:</span>
                  {alt.desc}
                </div>
              </div>
            ))}"""

new_alert_card = """            {isAlertMode && alerts.map((alt, i) => {
              const isActive = activeRec === i;
              const isFlashing = flashingCard === i;
              return (
              <div id={`alert-card-${i}`} key={i} className={`rec-card ${isActive ? 'active' : ''}`} onClick={() => setActiveRec(i)} style={isFlashing ? { border: `2px solid ${alt.color}`, boxShadow: `0 0 10px ${alt.color}40`, transition: 'all 0.3s' } : { transition: 'all 0.3s' }}>
                <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'space-between', marginBottom: isActive ? 12 : 0 }}>
                  <div style={{ display: 'flex', alignItems: 'center', gap: 12 }}>
                    <div style={{ width: 36, height: 36, borderRadius: 10, background: `${alt.color}15`, display: 'flex', alignItems: 'center', justifyContent: 'center' }}>
                      <AlertCircle size={16} color={alt.color} />
                    </div>
                    <div style={{ color: '#0F172A' }}>
                      <div style={{ fontSize: 10, color: '#64748B', fontWeight: 'bold' }}>{alt.komoditas}</div>
                      <div style={{ fontWeight: 'normal', fontSize: 14 }}>{alt.provinsi}</div>
                    </div>
                  </div>
                  <div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', fontSize: 11, fontWeight: 'bold', padding: '2px 8px', borderRadius: 12, background: `${alt.color}15`, color: alt.color }}>
                    {alt.risk_level}
                  </div>
                </div>
                
                {isActive && (
                  <>
                    <div style={{ display: 'grid', gridTemplateColumns: '1fr 1fr', gap: 12, marginBottom: 12 }}>
                      <div style={{ background: '#F8FAFC', padding: 8, borderRadius: 6 }}>
                        <div style={{ fontSize: 11, color: '#64748B' }}>Harga Saat Ini</div>
                        <div style={{ fontSize: 14, fontWeight: 'bold', color: '#0F172A' }}>{formatRupiahShort(alt.current_price)}/kg</div>
                      </div>
                      <div style={{ background: '#F8FAFC', padding: 8, borderRadius: 6 }}>
                        <div style={{ fontSize: 11, color: '#64748B' }}>Dampak Prediksi (+7 Hari)</div>
                        <div style={{ fontSize: 14, fontWeight: 'bold', color: alt.color }}>+{alt.forecast_change_pct.toFixed(1)}%</div>
                      </div>
                    </div>
                    
                    <div style={{ fontSize: 13, color: '#475569', background: '#F1F5F9', padding: 12, borderRadius: 8, lineHeight: 1.5, whiteSpace: 'pre-line' }}>
                      {alt.desc}
                    </div>
                  </>
                )}
              </div>
            )})}"""
content = content.replace(old_alert_card, new_alert_card)

with open(path, 'w', encoding='utf-8') as f:
    f.write(content)

print("SUCCESS")
