import re

file_path = r"d:\2026\pangan-ai\panganai\frontend\src\pages\PeluangDistribusi.jsx"
with open(file_path, "r", encoding="utf-8") as f:
    content = f.read()

# Status
content = content.replace("badge: '✅ Terbuka'", "badge: '✅ Direkomendasikan'")

# Headers
content = content.replace("<h2>Supply & Distribution Optimizer</h2>", "<h2>Optimizer Pasokan & Distribusi</h2>")
content = content.replace("<p>Supply-Demand Overview, Gap Analysis, dan Rekomendasi Rute Distribusi (Forecast-Aware)</p>", "<p>Tinjauan Pasokan-Permintaan, Analisis Kesenjangan, dan Rekomendasi Rute Distribusi (Berbasis Prediksi)</p>")
content = content.replace(">Optimizer Performance Metrics</h3>", ">Metrik Performa Optimizer</h3>")
content = content.replace(">Top Surplus vs Deficit Provinces</h3>", ">Provinsi Surplus dan Defisit Terbesar</h3>")
content = content.replace(">Route Details Table</h3>", ">Tabel Detail Rute</h3>")

# KPI Labels
content = content.replace("label: 'Physical Routes'", "label: 'Rute Fisik'")
content = content.replace("label: 'Market Alerts'", "label: 'Peringatan Pasar'")
content = content.replace("label: 'Supported Commodities'", "label: 'Komoditas Terdukung'")
content = content.replace("label: 'Provinces Covered'", "label: 'Provinsi Tercakup'")
content = content.replace("label: 'Avg Route Score'", "label: 'Rata-rata Skor Rute'")

# KPI Rendering
kpi_renderer_old = """<div style={{ fontSize: 28, fontWeight: 800, color: '#0F172A', fontFamily: 'monospace' }}>{c.value}</div>
          </div>"""
kpi_renderer_new = """<div style={{ fontSize: 28, fontWeight: 800, color: '#0F172A', fontFamily: 'monospace' }}>
              {c.value} {c.label === 'Rata-rata Skor Rute' && <span style={{fontSize: 14, color: '#64748B'}}>/ 100</span>}
            </div>
            {c.label === 'Rata-rata Skor Rute' && (
              <div style={{ fontSize: 10, color: '#64748B', lineHeight: 1.4, marginTop: -4 }}>
                Berdasarkan: Kebutuhan Wilayah, Kapasitas Surplus, Risiko Harga
              </div>
            )}
          </div>"""
content = content.replace(kpi_renderer_old, kpi_renderer_new)

# Chart fixes
content = content.replace("margin={{ top: 10, right: 10, left: 20, bottom: 20 }}", "margin={{ top: 10, right: 10, left: 20, bottom: 80 }}")
content = content.replace("<Legend wrapperStyle={{ fontSize: 12 }} />", "<Legend verticalAlign=\"top\" wrapperStyle={{ fontSize: 12, paddingBottom: 20 }} />")

# Table headers
content = content.replace("['asal', 'Asal (Source)']", "['asal', 'Asal']")
content = content.replace("['tujuan', 'Tujuan (Dest)']", "['tujuan', 'Tujuan']")
content = content.replace("['route_score', 'Route Score']", "['route_score', 'Skor Rute']")
content = content.replace("Generating Forecast-Aware Routes...", "Membuat Rute Berbasis Prediksi...")

with open(file_path, "w", encoding="utf-8") as f:
    f.write(content)

print("PeluangDistribusi.jsx updated!")
