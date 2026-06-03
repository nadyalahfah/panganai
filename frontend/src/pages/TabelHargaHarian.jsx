import React, { useState, useMemo } from 'react'
import { Search, Download, ChevronUp, ChevronDown, ChevronsUpDown, TrendingUp, TrendingDown, Minus, MapPin, Activity, AlertCircle, Bot } from 'lucide-react'
import SparklineChart from '../components/SparklineChart'

// Real API augmented with mock enrichment data
const RAW_DATA = [
  {
    komoditas: 'Beras Medium I', kategori: 'Beras Premium', satuan: '/kg',
    harga: 14200, kemarin: 14150, sparkColors: '#3B82F6',
    spark: [13800, 13900, 14000, 14050, 14100, 14150, 14200].map(v => ({ v })),
    hap: 13500, hap_daerah: 'Jawa Barat',
  },
  {
    komoditas: 'Minyak Goreng Curah', kategori: 'Curah Grade A', satuan: '/liter',
    harga: 15800, kemarin: 16200, sparkColors: '#F97316',
    spark: [16500, 16400, 16200, 16000, 15900, 16200, 15800].map(v => ({ v })),
    hap: 15500, hap_daerah: 'DKI Jakarta',
  },
  {
    komoditas: 'Cabai Merah Keriting', kategori: 'Grade A Super', satuan: '/kg',
    harga: 45000, kemarin: 43800, sparkColors: '#EF4444',
    spark: [41000, 42000, 43000, 43200, 43800, 44500, 45000].map(v => ({ v })),
    hap: 42000, hap_daerah: 'Jawa Timur',
  },
  {
    komoditas: 'Telur Ayam Ras', kategori: 'Berkualitas Baik', satuan: '/kg',
    harga: 28500, kemarin: 29000, sparkColors: '#EAB308',
    spark: [29500, 29200, 29000, 28800, 28600, 29000, 28500].map(v => ({ v })),
    hap: 27000, hap_daerah: 'Jawa Tengah',
  },
  {
    komoditas: 'Bawang Merah', kategori: 'Lokal Premium', satuan: '/kg',
    harga: 32000, kemarin: 31500, sparkColors: '#8B5CF6',
    spark: [30000, 30500, 31000, 31200, 31500, 31800, 32000].map(v => ({ v })),
    hap: 30000, hap_daerah: 'Jawa Timur',
  },
  {
    komoditas: 'Gula Pasir', kategori: 'Premium Lokal', satuan: '/kg',
    harga: 17500, kemarin: 17500, sparkColors: '#6B7280',
    spark: [17200, 17300, 17350, 17400, 17450, 17500, 17500].map(v => ({ v })),
    hap: 17000, hap_daerah: 'Nasional',
  },
  {
    komoditas: 'Tepung Terigu', kategori: 'Protein Sedang', satuan: '/kg',
    harga: 12000, kemarin: 12200, sparkColors: '#10B981',
    spark: [12500, 12400, 12300, 12200, 12100, 12200, 12000].map(v => ({ v })),
    hap: 11500, hap_daerah: 'Nasional',
  },
  {
    komoditas: 'Daging Ayam Ras', kategori: 'Segar Karkas', satuan: '/kg',
    harga: 38000, kemarin: 37500, sparkColors: '#EC4899',
    spark: [36000, 36500, 37000, 37200, 37500, 37800, 38000].map(v => ({ v })),
    hap: 36000, hap_daerah: 'Jawa Timur',
  },
]

export default function TabelHargaHarian() {
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState('komoditas')
  const [sortDir, setSortDir] = useState('asc')
  const [expandedRow, setExpandedRow] = useState(null)

  const handleSort = (key) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('asc') }
  }

  const SortIcon = ({ col }) => {
    if (sortKey !== col) return <ChevronsUpDown size={11} style={{ opacity: 0.4 }} />
    return sortDir === 'asc' ? <ChevronUp size={11} /> : <ChevronDown size={11} />
  }

  const data = useMemo(() => {
    return RAW_DATA
      .map(r => ({
        ...r,
        pct: r.kemarin ? ((r.harga - r.kemarin) / r.kemarin * 100) : 0,
      }))
      .filter(r =>
        r.komoditas.toLowerCase().includes(search.toLowerCase()) ||
        r.kategori.toLowerCase().includes(search.toLowerCase())
      )
      .sort((a, b) => {
        const va = a[sortKey], vb = b[sortKey]
        if (typeof va === 'string') return sortDir === 'asc' ? va.localeCompare(vb) : vb.localeCompare(va)
        if (va < vb) return sortDir === 'asc' ? -1 : 1
        if (va > vb) return sortDir === 'asc' ? 1 : -1
        return 0
      })
  }, [search, sortKey, sortDir])

  const getRowClass = (pct) => {
    if (pct > 2) return 'row-naik'
    if (pct < -1) return 'row-ok'
    return 'row-warn'
  }

  const handleExport = () => {
    const headers = ['Komoditas', 'Kategori', 'Satuan', 'Harga', 'Kemarin', '% Perubahan', 'HAP', 'Daerah HAP']
    const rows = data.map(r => [r.komoditas, r.kategori, r.satuan, r.harga, r.kemarin, r.pct.toFixed(2), r.hap, r.hap_daerah])
    const csv = [headers, ...rows].map(r => r.join(',')).join('\n')
    const blob = new Blob([csv], { type: 'text/csv' })
    const url = URL.createObjectURL(blob)
    const a = document.createElement('a')
    a.href = url; a.download = 'harga_harian.csv'; a.click()
    URL.revokeObjectURL(url)
  }

  // --- AI Insights Logic ---
  const topRising = useMemo(() => data.length > 0 ? data.reduce((max, r) => r.pct > max.pct ? r : max, data[0]) : null, [data])
  const mostStable = useMemo(() => data.length > 0 ? data.reduce((min, r) => Math.abs(r.pct) < Math.abs(min.pct) ? r : min, data[0]) : null, [data])
  const highestRiskProvince = useMemo(() => {
    if (data.length === 0) return 'N/A'
    const provs = {}
    data.forEach(r => {
      if (r.hap_daerah && r.hap_daerah !== 'Nasional') {
        if (!provs[r.hap_daerah]) provs[r.hap_daerah] = { sum: 0, count: 0 }
        provs[r.hap_daerah].sum += r.pct
        provs[r.hap_daerah].count += 1
      }
    })
    let highest = { name: 'N/A', avg: -Infinity }
    for (const [name, stats] of Object.entries(provs)) {
      const avg = stats.sum / stats.count
      if (avg > highest.avg) highest = { name, avg }
    }
    return highest.name
  }, [data])
  const marketCondition = useMemo(() => {
    if (data.length === 0) return 'Stabil'
    const avgPct = data.reduce((sum, r) => sum + r.pct, 0) / data.length
    if (avgPct > 2) return 'Risiko Tinggi'
    if (avgPct > 0.5) return 'Waspada'
    return 'Stabil'
  }, [data])
  const aiExplanation = useMemo(() => {
    if (!topRising) return 'Data tidak tersedia untuk analisis.'
    const statusText = marketCondition === 'Risiko Tinggi' ? 'diperlukan operasi pasar segera' : marketCondition === 'Waspada' ? 'diperlukan monitoring distribusi secara berkala' : 'dinamika masih dalam batas aman'
    const provText = highestRiskProvince !== 'N/A' ? `${highestRiskProvince} menjadi wilayah dengan risiko kenaikan harga terbesar. ` : ''
    return `${topRising.komoditas} menunjukkan kenaikan tertinggi dalam periode pengamatan (+${topRising.pct.toFixed(1)}%). ${provText}Kondisi pasar saat ini berada pada status ${marketCondition} sehingga ${statusText}.`
  }, [topRising, highestRiskProvince, marketCondition])

  return (
    <div>
      <div className="page-header">
        <h2>Market Intelligence Center</h2>
        <p>Eksplorasi harga pangan nasional dan insight AI untuk mendukung pengambilan keputusan.</p>
      </div>

      {/* Market Intelligence Summary Cards */}
      <div className="section-title" style={{ marginBottom: 14 }}>Market Intelligence Summary</div>
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 16, marginBottom: 16 }}>
        {/* Top Rising */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 10, padding: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)', fontSize: 12, fontWeight: 600, marginBottom: 8 }}>
            <TrendingUp size={14} color="var(--danger)" /> KOMODITAS PALING NAIK
          </div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
            {topRising ? topRising.komoditas : '-'}
          </div>
          <div style={{ fontSize: 13, color: 'var(--danger)', fontWeight: 600, marginTop: 4 }}>
            {topRising ? `+${topRising.pct.toFixed(1)}%` : ''}
          </div>
        </div>

        {/* Most Stable */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 10, padding: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)', fontSize: 12, fontWeight: 600, marginBottom: 8 }}>
            <Minus size={14} color="var(--success)" /> KOMODITAS PALING STABIL
          </div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
            {mostStable ? mostStable.komoditas : '-'}
          </div>
          <div style={{ fontSize: 13, color: 'var(--success)', fontWeight: 600, marginTop: 4 }}>
            {mostStable ? `${mostStable.pct > 0 ? '+' : ''}${mostStable.pct.toFixed(1)}%` : ''}
          </div>
        </div>

        {/* Highest Risk Province */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 10, padding: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)', fontSize: 12, fontWeight: 600, marginBottom: 8 }}>
            <MapPin size={14} color="var(--warning)" /> PROVINSI RISIKO TERTINGGI
          </div>
          <div style={{ fontSize: 15, fontWeight: 700, color: 'var(--text-primary)' }}>
            {highestRiskProvince}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
            Berdasarkan rata-rata kenaikan
          </div>
        </div>

        {/* Market Condition */}
        <div style={{ background: 'var(--bg-card)', border: '1px solid var(--border)', borderRadius: 10, padding: 16 }}>
          <div style={{ display: 'flex', alignItems: 'center', gap: 6, color: 'var(--text-muted)', fontSize: 12, fontWeight: 600, marginBottom: 8 }}>
            <Activity size={14} color={marketCondition === 'Risiko Tinggi' ? 'var(--danger)' : marketCondition === 'Waspada' ? 'var(--warning)' : 'var(--success)'} /> KONDISI PASAR
          </div>
          <div style={{ fontSize: 15, fontWeight: 700, color: marketCondition === 'Risiko Tinggi' ? 'var(--danger)' : marketCondition === 'Waspada' ? 'var(--warning)' : 'var(--success)' }}>
            {marketCondition}
          </div>
          <div style={{ fontSize: 12, color: 'var(--text-secondary)', marginTop: 4 }}>
            Status agregat komoditas
          </div>
        </div>
      </div>

      {/* AI Market Insight Panel */}
      <div style={{ background: '#F0F9FF', border: '1px solid #BAE6FD', borderRadius: 10, padding: 16, marginBottom: 24, display: 'flex', gap: 12 }}>
        <div style={{ background: '#3B82F6', color: 'white', width: 32, height: 32, borderRadius: '50%', display: 'flex', alignItems: 'center', justifyContent: 'center', flexShrink: 0 }}>
          <Bot size={18} />
        </div>
        <div>
          <div style={{ fontWeight: 700, fontSize: 13, color: '#0369A1', marginBottom: 4 }}>AI Market Insight</div>
          <div style={{ fontSize: 13, color: '#0F172A', lineHeight: 1.6 }}>
            {aiExplanation}
          </div>
        </div>
      </div>

      <div className="data-table-wrapper fade-in">
        <div className="table-toolbar">
          <div className="table-toolbar-left">
            <div className="search-wrapper">
              <Search size={14} className="search-icon" />
              <input
                type="text"
                className="search-input"
                placeholder="Cari komoditas atau kategori..."
                value={search}
                onChange={e => setSearch(e.target.value)}
              />
            </div>
            <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{data.length} komoditas</span>
          </div>
          <div className="table-toolbar-right">
            <button
              onClick={handleExport}
              style={{
                display: 'flex', alignItems: 'center', gap: 6,
                padding: '6px 12px', border: '1px solid var(--border)',
                borderRadius: 7, background: 'var(--bg-card)', cursor: 'pointer',
                fontSize: 12, fontWeight: 600, color: 'var(--text-secondary)',
                fontFamily: 'Inter, system-ui, sans-serif',
              }}
            >
              <Download size={13} /> Export CSV
            </button>
          </div>
        </div>

        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                {[
                  ['komoditas', 'Komoditas'],
                  ['harga', 'Harga Hari Ini'],
                  ['kemarin', 'Kemarin'],
                  ['pct', '% Perubahan'],
                  [null, 'Tren'],
                  [null, 'Status'],
                ].map(([key, label]) => (
                  <th key={label} onClick={() => key && handleSort(key)} style={{ cursor: key ? 'pointer' : 'default' }}>
                    <span style={{ display: 'flex', alignItems: 'center', gap: 4 }}>
                      {label} {key && <SortIcon col={key} />}
                    </span>
                  </th>
                ))}
              </tr>
            </thead>
            <tbody>
              {data.map((r, i) => {
                const isExpanded = expandedRow === i
                return (
                  <React.Fragment key={r.komoditas}>
                    <tr
                      className={getRowClass(r.pct)}
                      onClick={() => setExpandedRow(isExpanded ? null : i)}
                      style={{ cursor: 'pointer' }}
                    >
                      <td>
                        <div style={{ fontWeight: 700, fontSize: 13 }}>{r.komoditas}</div>
                      </td>
                      <td className="font-mono" style={{ fontWeight: 700, fontSize: 14 }}>
                        {r.harga.toLocaleString('id-ID')}
                      </td>
                      <td className="font-mono" style={{ color: 'var(--text-secondary)' }}>
                        {r.kemarin.toLocaleString('id-ID')}
                      </td>
                      <td>
                        <span style={{
                          fontWeight: 700, fontSize: 12,
                          color: r.pct > 2 ? 'var(--danger)' : r.pct < -1 ? 'var(--success)' : 'var(--warning)',
                          display: 'flex', alignItems: 'center', gap: 3,
                        }}>
                          {r.pct > 0.1 ? <TrendingUp size={12}/> : r.pct < -0.1 ? <TrendingDown size={12}/> : <Minus size={12}/>}
                          {r.pct > 0 ? '+' : ''}{r.pct.toFixed(1)}%
                        </span>
                      </td>
                      <td>
                        <SparklineChart data={r.spark} color={r.sparkColors} />
                      </td>
                      <td>
                        <span style={{
                          padding: '4px 8px', borderRadius: 12, fontSize: 11, fontWeight: 600,
                          background: r.pct > 2 ? '#FEF2F2' : r.pct < -1 ? '#F0FDF4' : '#FFF7ED',
                          color: r.pct > 2 ? 'var(--danger)' : r.pct < -1 ? 'var(--success)' : 'var(--warning)',
                        }}>
                          {r.pct > 2 ? 'Kritis' : r.pct < -1 ? 'Aman' : 'Waspada'}
                        </span>
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr key={`detail-${i}`}>
                        <td colSpan={6} style={{ background: 'rgba(59,130,246,0.03)', padding: '12px 16px' }}>
                          <div style={{ fontSize: 12, lineHeight: 1.7 }}>
                            <strong>{r.komoditas}</strong> | Kategori: {r.kategori} | Satuan: {r.satuan} &nbsp;·&nbsp;
                            HAP: Rp {r.hap.toLocaleString('id-ID')}/{r.satuan.replace('/','')} ({r.hap_daerah}) &nbsp;·&nbsp;
                            Variansi vs HAP: <span style={{ color: r.harga > r.hap ? 'var(--danger)' : 'var(--success)', fontWeight: 700 }}>
                              {r.harga > r.hap ? '+' : ''}{((r.harga - r.hap) / r.hap * 100).toFixed(1)}%
                            </span>
                            &nbsp;dari harga acuan pemerintah.
                          </div>
                        </td>
                      </tr>
                    )}
                  </React.Fragment>
                )
              })}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
