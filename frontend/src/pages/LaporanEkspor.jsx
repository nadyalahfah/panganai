import { useState } from 'react'
import {
  FileSpreadsheet, FileText, Map, FileBarChart,
  CheckCircle, Clock, AlertTriangle, Download, Server,
  Database, Cpu, Globe, Bot, ChevronDown, ChevronUp,
} from 'lucide-react'

const EXPORT_CARDS = [
  {
    icon: FileText,
    title: 'Forecast Report',
    format: '.csv',
    size: '~0.8 MB',
    lastGen: '14 Apr 2026, 00:30',
    includes: 'Harga aktual + prediksi, confidence score',
    color: '#3B82F6',
    auto: true,
    versions: ['13 Apr 2026', '12 Apr 2026', '11 Apr 2026 (arsip)'],
  },
  {
    icon: FileSpreadsheet,
    title: 'Alert Report',
    format: '.xlsx',
    size: '~1.2 MB',
    lastGen: '14 Apr 2026, 00:30',
    includes: 'Daftar provinsi kritis, level urgensi, action plan',
    color: '#EF4444',
    auto: true,
    versions: ['13 Apr 2026', '12 Apr 2026', '11 Apr 2026 (arsip)'],
  },
  {
    icon: Map,
    title: 'Distribution Report',
    format: '.geojson',
    size: '~1.8 MB',
    lastGen: '14 Apr 2026, 00:30',
    includes: 'Rute optimal, surplus-defisit geospasial',
    color: '#F97316',
    auto: true,
    versions: ['13 Apr 2026', '12 Apr 2026', '11 Apr 2026 (arsip)'],
  },
]

export default function LaporanEkspor() {
  const [loadingCard, setLoadingCard] = useState(null)
  const [expandedCard, setExpandedCard] = useState(null)

  const handleDownload = (idx, title) => {
    setLoadingCard(idx)
    setTimeout(() => {
      setLoadingCard(null)
      alert(`✅ ${title} berhasil diunduh (simulasi)`)
    }, 1800)
  }

  return (
    <div>
      <div className="page-header">
        <h2>AI Reports Center</h2>
        <p>Unduh data dan hasil analisis pipeline AI untuk pengambilan keputusan</p>
      </div>

      {/* Export Cards */}
      <div className="section-title" style={{ marginBottom: 14 }}>📥 Unduh Data & Laporan</div>
      <div className="export-grid" style={{ marginBottom: 28 }}>
        {EXPORT_CARDS.map((card, idx) => (
          <div key={idx} className="export-card fade-in">
            <div className="export-card-icon" style={{ background: `${card.color}15`, color: card.color }}>
              <card.icon size={22} />
            </div>
            <div className="export-card-title">{card.title}</div>
            <div className="export-card-meta">
              <div>Format: <b>{card.format}</b> &nbsp;·&nbsp; {card.size}</div>
              <div style={{ marginTop: 4 }}>Dibuat: {card.lastGen}</div>
              {card.period && <div>Periode: <b>{card.period}</b></div>}
              <div style={{ marginTop: 4, fontSize: 11 }}>{card.includes}</div>
              <div style={{ marginTop: 4, display: 'flex', alignItems: 'center', gap: 5 }}>
                {card.auto
                  ? <><CheckCircle size={11} color="#16A34A" /> <span style={{ color: '#16A34A', fontSize: 10, fontWeight: 600 }}>Auto-generated harian</span></>
                  : <><Clock size={11} color="#B45309" /> <span style={{ color: '#B45309', fontSize: 10, fontWeight: 600 }}>1x per bulan</span></>
                }
              </div>
            </div>

            <button
              className="export-btn"
              onClick={() => handleDownload(idx, card.title)}
              disabled={loadingCard === idx}
              style={{ background: loadingCard === idx ? 'var(--gray-400)' : card.color }}
            >
              {loadingCard === idx ? (
                <><span style={{ display: 'inline-block', width: 12, height: 12, border: '2px solid white', borderTopColor: 'transparent', borderRadius: '50%', animation: 'spin 0.8s linear infinite' }} /> Mengunduh...</>
              ) : (
                <><Download size={14} /> Unduh {card.format}</>
              )}
            </button>

            {/* Versions */}
            <button
              onClick={() => setExpandedCard(expandedCard === idx ? null : idx)}
              style={{
                marginTop: 8, width: '100%', background: 'none', border: 'none', cursor: 'pointer',
                fontSize: 11, color: 'var(--text-muted)', display: 'flex', alignItems: 'center', gap: 4,
                justifyContent: 'center', fontFamily: 'Inter, system-ui, sans-serif',
              }}
            >
              {expandedCard === idx ? <ChevronUp size={11} /> : <ChevronDown size={11} />}
              Versi sebelumnya
            </button>
            {expandedCard === idx && (
              <div style={{ marginTop: 6, background: 'var(--gray-50)', borderRadius: 6, padding: '8px 10px' }}>
                {card.versions.map((v, i) => (
                  <div key={i} style={{
                    fontSize: 11, color: 'var(--text-secondary)', padding: '3px 0',
                    borderBottom: i < card.versions.length - 1 ? '1px solid var(--border)' : 'none',
                    display: 'flex', justifyContent: 'space-between',
                  }}>
                    <span>• {v}</span>
                    <button style={{
                      background: 'none', border: 'none', cursor: 'pointer', color: 'var(--primary)',
                      fontSize: 10, fontWeight: 600, fontFamily: 'Inter, system-ui, sans-serif',
                    }}>
                      Unduh
                    </button>
                  </div>
                ))}
              </div>
            )}
          </div>
        ))}
      </div>



      <style>{`
        @keyframes spin { to { transform: rotate(360deg); } }
      `}</style>
    </div>
  )
}
