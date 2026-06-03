import re

file_path = r"d:\2026\pangan-ai\panganai\frontend\src\components\DistributionOptimizer.jsx"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# 1. Inject generateDynamicReasoning
reasoning_fn = """
const generateDynamicReasoning = (komoditas, src, dst, surplus, deficit, routeScore, priority, risk) => {
  const k = (komoditas || '').toLowerCase();
  const s = src || '';
  const d = dst || '';
  
  const srcJawa = s.includes('Jawa') || s.includes('Banten') || s.includes('Jakarta') || s.includes('Yogyakarta');
  const dstJawa = d.includes('Jawa') || d.includes('Banten') || d.includes('Jakarta') || d.includes('Yogyakarta');
  const antarPulau = srcJawa !== dstJawa;
  
  if (k.includes('beras')) {
    if (antarPulau && risk > 5) return `Beras Medium direkomendasikan dikirim dari ${s} karena surplus regional tinggi dan kebutuhan ${d} diproyeksikan meningkat (Risiko +${risk.toFixed(1)}%). Distribusi lintas pulau ini mendesak.`;
    if (antarPulau) return `Redistribusi Beras dari ${s} ke ${d} direkomendasikan untuk menyeimbangkan stok antar pulau sebelum gejolak harga meluas.`;
    if (surplus > deficit) return `Pasokan Beras dari ${s} sangat mencukupi untuk sepenuhnya menutup defisit di ${d} secara intra-regional.`;
    return `Pasokan Beras dari ${s} dapat dialihkan ke ${d} untuk optimalisasi stok lokal dengan tingkat kelayakan distribusi yang tinggi (Skor: ${routeScore}).`;
  }
  
  if (k.includes('cabai')) {
    if (risk > 15) return `Lonjakan risiko harga Cabai ekstrem (+${risk.toFixed(1)}%) di ${d} membutuhkan intervensi pasokan segera dari surplus ${s}.`;
    if (routeScore > 85) return `Kondisi kritis: Stabilitas harga Cabai di ${d} terancam. Surplus dari ${s} adalah opsi redistribusi paling logis dan cepat saat ini.`;
    if (antarPulau) return `Cabai dari ${s} direkomendasikan untuk distribusi lintas pulau guna mengamankan defisit di ${d} dan meredam fluktuasi harga.`;
    return `Redistribusi Cabai intra-regional dari ${s} ke ${d} sangat disarankan untuk meratakan ketersediaan stok jangka pendek.`;
  }
  
  if (k.includes('bawang')) {
    if (antarPulau) return `Bawang Merah memerlukan redistribusi lintas pulau karena defisit ${d} cukup besar dan kapasitas pasokan ${s} terpantau aman.`;
    if (risk > 10) return `Risiko kelangkaan Bawang Merah di ${d} terpantau tinggi (+${risk.toFixed(1)}%). Pengiriman dari ${s} diwajibkan sebagai prioritas ${priority}.`;
    if (surplus > deficit) return `Surplus Bawang di ${s} cukup besar untuk secara total menutupi kekurangan pasokan yang diproyeksikan di ${d}.`;
    return `Rute redistribusi Bawang Merah ini dinilai layak (Skor: ${routeScore}) untuk mencegah defisit berkelanjutan di pasar ${d}.`;
  }

  if (k.includes('telur') || k.includes('ayam')) {
    if (dstJawa) return `Kebutuhan pasokan di pusat padat populasi seperti ${d} mulai meningkat tajam. Pasokan dari ${s} masih dalam level aman untuk dialihkan.`;
    if (risk > 10) return `Prediksi harga naik +${risk.toFixed(1)}% di ${d}. Disarankan redistribusi segera dari pasokan ${s}.`;
    if (antarPulau) return `Distribusi protein via jalur pengiriman dari ${s} ke ${d} diperlukan untuk meratakan stok nasional.`;
    return `Rute intra-regional ini memiliki kelayakan (Skor: ${routeScore}) untuk memperkuat rantai pasok antara ${s} dan ${d}.`;
  }

  // Generic fallback variations
  if (routeScore > 80) return `Dengan route score ${routeScore} dan risiko harga rendah, jalur pengiriman dari ${s} ke ${d} ini layak menjadi prioritas distribusi tahap pertama.`;
  if (antarPulau) return `Redistribusi logistik lintas pulau dari ${s} menuju titik defisit ${d} dinilai sangat strategis.`;
  if (risk > 5) return `Fluktuasi harga di ${d} (+${risk.toFixed(1)}%) perlu direspon dengan pemindahan surplus dari ${s} untuk menjaga stabilitas.`;
  return `Pemindahan surplus pasokan dari lumbung ${s} ke wilayah defisit ${d} merupakan opsi optimal untuk keseimbangan pasar.`;
};

export default function DistributionOptimizer"""

content = content.replace("export default function DistributionOptimizer", reasoning_fn)

# 2. Update recs mapping block
recs_old = """      return {
        id: i,
        source: { provinsi: r.source_province || r.provinsi_asal || r.asal || '', prediksi_7h: r.forecast_price || 0 },
        dest: { provinsi: r.destination_province || r.provinsi_tujuan || r.tujuan || '', prediksi_7h: r.forecast_price || 0 },
        surplus: '+' + Math.round(r.surplus_ton || 0).toLocaleString('id-ID') + ' Ton',
        deficit: '-' + Math.round(r.deficit_ton || 0).toLocaleString('id-ID') + ' Ton',
        priority: priority,
        priorityColor: color,
        desc: r.reason || `Optimized route from ${r.source_province} to ${r.destination_province} based on backend Need Score.`
      };"""

recs_new = """      const src = r.source_province || r.provinsi_asal || r.asal || 'Asal';
      const dst = r.destination_province || r.provinsi_tujuan || r.tujuan || 'Tujuan';
      const fRisk = r.forecast_change_pct || 0;
      const sTon = r.surplus_ton || 0;
      const dTon = r.deficit_ton || 0;
      
      const dynamicReasoning = generateDynamicReasoning(r.commodity || r.komoditas, src, dst, sTon, dTon, r.route_score || 0, priority, fRisk);

      return {
        id: i,
        source: { provinsi: src, prediksi_7h: r.forecast_price || 0 },
        dest: { provinsi: dst, prediksi_7h: r.forecast_price || 0 },
        surplus: '+' + Math.round(sTon).toLocaleString('id-ID') + ' Ton',
        deficit: '-' + Math.round(dTon).toLocaleString('id-ID') + ' Ton',
        priority: priority,
        priorityColor: color,
        desc: dynamicReasoning
      };"""

content = content.replace(recs_old, recs_new)

# 3. Replace Map rendering
svg_old = """            {/* Connection Lines (Physical Routes) */}
            {!isAlertMode && activeData && PROV_COORDS[activeData.source.provinsi] && PROV_COORDS[activeData.dest.provinsi] && (
              <g>
                <path 
                  d={`M${PROV_COORDS[activeData.source.provinsi][0]},${PROV_COORDS[activeData.source.provinsi][1]} 
                       Q${PROV_COORDS[activeData.source.provinsi][0]},${PROV_COORDS[activeData.dest.provinsi][1] - 80} 
                       ${PROV_COORDS[activeData.dest.provinsi][0]},${PROV_COORDS[activeData.dest.provinsi][1]}`}
                  fill="none"
                  stroke={activeData.priorityColor}
                  strokeWidth={2.5}
                  strokeDasharray="6 4"
                  className="dash-anim"
                />
                
                {/* Source Marker */}
                <circle 
                  cx={PROV_COORDS[activeData.source.provinsi][0]} 
                  cy={PROV_COORDS[activeData.source.provinsi][1]} 
                  r="5" fill="#10B981" stroke="white" strokeWidth="1.5" 
                />
                <circle 
                  cx={PROV_COORDS[activeData.source.provinsi][0]} 
                  cy={PROV_COORDS[activeData.source.provinsi][1]} 
                  r="12" fill="#10B981" opacity="0.2" className="pulse-anim"
                />
                
                {/* Dest Marker */}
                <circle 
                  cx={PROV_COORDS[activeData.dest.provinsi][0]} 
                  cy={PROV_COORDS[activeData.dest.provinsi][1]} 
                  r="5" fill={activeData.priorityColor} stroke="white" strokeWidth="1.5" 
                />
                <circle 
                  cx={PROV_COORDS[activeData.dest.provinsi][0]} 
                  cy={PROV_COORDS[activeData.dest.provinsi][1]} 
                  r="12" fill={activeData.priorityColor} opacity="0.2" className="pulse-anim"
                />
              </g>
            )}

            {/* Warning Markers (Market Alerts) */}"""

svg_new = """            {/* Connection Lines (Physical Routes) */}
            {!isAlertMode && recommendations.length > 0 && recommendations.map((r, idx) => {
              if (!PROV_COORDS[r.source.provinsi] || !PROV_COORDS[r.dest.provinsi]) return null;
              const isActive = activeRec === idx;
              const opacity = isActive ? 1 : 0.25;
              const zIndex = isActive ? 100 : idx;
              
              return (
                <g key={`route-${idx}`} style={{ zIndex }}>
                  <path 
                    d={`M${PROV_COORDS[r.source.provinsi][0]},${PROV_COORDS[r.source.provinsi][1]} 
                         Q${PROV_COORDS[r.source.provinsi][0]},${PROV_COORDS[r.dest.provinsi][1] - (80 + idx * 5)} 
                         ${PROV_COORDS[r.dest.provinsi][0]},${PROV_COORDS[r.dest.provinsi][1]}`}
                    fill="none"
                    stroke={r.priorityColor}
                    strokeWidth={isActive ? 2.5 : 1.5}
                    strokeDasharray="6 4"
                    opacity={opacity}
                    className="dash-anim"
                  />
                  
                  {/* Source Marker */}
                  <circle 
                    cx={PROV_COORDS[r.source.provinsi][0]} 
                    cy={PROV_COORDS[r.source.provinsi][1]} 
                    r={isActive ? 5 : 4} fill="#10B981" stroke="white" strokeWidth={isActive ? 1.5 : 0.5} opacity={opacity + 0.3}
                  />
                  {isActive && (
                    <circle 
                      cx={PROV_COORDS[r.source.provinsi][0]} 
                      cy={PROV_COORDS[r.source.provinsi][1]} 
                      r="12" fill="#10B981" opacity="0.2" className="pulse-anim" style={{pointerEvents: 'none'}}
                    />
                  )}
                  
                  {/* Dest Marker */}
                  <circle 
                    cx={PROV_COORDS[r.dest.provinsi][0]} 
                    cy={PROV_COORDS[r.dest.provinsi][1]} 
                    r={isActive ? 5 : 4} fill={r.priorityColor} stroke="white" strokeWidth={isActive ? 1.5 : 0.5} opacity={opacity + 0.3}
                  />
                  {isActive && (
                    <circle 
                      cx={PROV_COORDS[r.dest.provinsi][0]} 
                      cy={PROV_COORDS[r.dest.provinsi][1]} 
                      r="12" fill={r.priorityColor} opacity="0.2" className="pulse-anim" style={{pointerEvents: 'none'}}
                    />
                  )}
                  
                  <title>{`${r.source.provinsi} -> ${r.dest.provinsi} | Prioritas: ${r.priority}`}</title>
                </g>
              );
            })}

            {/* Warning Markers (Market Alerts) */}"""

content = content.replace(svg_old, svg_new)

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("DistributionOptimizer.jsx updated!")
