import re

file_path = r'd:\2026\pangan-ai\panganai\frontend\src\components\DistributionOptimizer.jsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

target1 = """      let displayLevel = 'Priority Monitoring';
      if (a.risk_level === 'High Risk Alert') {
        color = '#EF4444';
        displayLevel = 'Immediate Intervention';
      } else if (a.risk_level === 'Medium Risk Alert') {
        displayLevel = 'Priority Monitoring';
      } else {
        displayLevel = a.risk_level;
      }
      
      let finalDesc = a.reason || "Projected price pressure detected. Market monitoring and intervention are recommended to mitigate expected price escalation.";
      if (finalDesc.includes("Because we do not possess verified demand data")) {
        finalDesc = "Projected price pressure detected. Market monitoring and intervention are recommended to mitigate expected price escalation.";
      }"""

replacement1 = """      let displayLevel = 'Monitoring Prioritas';
      if (a.risk_level === 'High Risk Alert') {
        color = '#EF4444';
        displayLevel = 'Intervensi Segera';
      } else if (a.risk_level === 'Medium Risk Alert') {
        displayLevel = 'Monitoring Prioritas';
      } else {
        displayLevel = 'Normal';
      }
      
      let finalDesc = '';
      if (a.risk_level === 'High Risk Alert') {
        finalDesc = `Prediksi kenaikan harga mencapai ${a.forecast_change_pct.toFixed(1)}%. Intervensi segera direkomendasikan untuk mencegah ketidakstabilan pasar.`;
      } else if (a.risk_level === 'Medium Risk Alert') {
        finalDesc = `Sinyal tekanan harga mulai muncul. Pemantauan distribusi dan evaluasi stok direkomendasikan.`;
      } else {
        finalDesc = `Kondisi pasar masih terkendali, namun pemantauan berkala disarankan.`;
      }"""
content = content.replace(target1, replacement1)

target_route = """      let priority = 'Medium';
      let color = '#F97316';
      if (r.route_score >= 80) { priority = 'High'; color = '#EF4444'; }
      else if (r.route_score < 60) { priority = 'Low'; color = '#3B82F6'; }"""
replacement_route = """      let priority = 'Sedang';
      let color = '#F97316';
      if (r.route_score >= 80) { priority = 'Tinggi'; color = '#EF4444'; }
      else if (r.route_score < 60) { priority = 'Rendah'; color = '#3B82F6'; }"""
content = content.replace(target_route, replacement_route)

content = content.replace("'Market Stabilization Engine' : 'Physical Redistribution Engine'", "'Mesin Stabilisasi Pasar' : 'Mesin Redistribusi Fisik'")
content = content.replace("'Recommended Market Interventions' : 'Recommendations'", "'Rekomendasi Intervensi Pasar' : 'Rekomendasi Rute'")
content = content.replace("Est. Deficit", "Est. Defisit")
content = content.replace("Priority Intervention Area", "Wilayah Prioritas Intervensi")
content = content.replace("Baseline Market State", "Harga Saat Ini")
content = content.replace("Expected Impact (+7D)", "Dampak Prediksi (+7 Hari)")

content = content.replace("{formatRupiahShort(alt.current_price)}", "{formatRupiahShort(alt.current_price)}/kg")
content = content.replace("{formatRupiahShort(alt.current_price)}/kg/kg", "{formatRupiahShort(alt.current_price)}/kg")

content = re.sub(
    r'<div style=\{\{\s*fontSize:\s*11,\s*fontWeight:\s*\'bold\',\s*padding:\s*\'2px 8px\',\s*borderRadius:\s*12,\s*background:\s*`\$\{rec\.priorityColor\}15`,\s*color:\s*rec\.priorityColor\s*\}\}>\s*\{rec\.priority\}\s*Priority\s*</div>',
    r"<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', fontSize: 11, fontWeight: 'bold', padding: '2px 8px', borderRadius: 12, background: `${rec.priorityColor}15`, color: rec.priorityColor }}>Prioritas {rec.priority}</div>",
    content
)

content = re.sub(
    r'<div style=\{\{\s*fontSize:\s*11,\s*fontWeight:\s*\'bold\',\s*padding:\s*\'2px 8px\',\s*borderRadius:\s*12,\s*background:\s*`\$\{alt\.color\}15`,\s*color:\s*alt\.color\s*\}\}>\s*\{alt\.risk_level\}\s*</div>',
    r"<div style={{ display: 'flex', alignItems: 'center', justifyContent: 'center', textAlign: 'center', fontSize: 11, fontWeight: 'bold', padding: '2px 8px', borderRadius: 12, background: `${alt.color}15`, color: alt.color }}>{alt.risk_level}</div>",
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("Done")
