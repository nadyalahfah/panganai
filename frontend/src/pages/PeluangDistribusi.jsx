import React, { useState, useMemo } from 'react'
import { Truck, Target, BarChart2, RouteIcon, ChevronUp, ChevronDown, ChevronsUpDown, Filter, Clock } from 'lucide-react'
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer, Legend } from 'recharts'


// ── Demand Mock Data ──────────────────────────────────────────────────
const generateDemandData = (days) => {
  const data = []
  const baseDate = new Date('2026-03-15')
  for (let i = 0; i < days; i++) {
    const d = new Date(baseDate)
    d.setDate(d.getDate() + i)
    const demand = 2800 + Math.sin(i * 0.3) * 200 + Math.random() * 100
    const supply = 2600 + Math.cos(i * 0.25) * 180 + Math.random() * 80
    data.push({
      tanggal: d.toISOString().slice(0, 10),
      demand: Math.round(demand),
      supply: Math.round(supply),
      gap: Math.round(demand - supply),
    })
  }
  return data
}

function DemandTooltip({ active, payload, label }) {
  if (!active || !payload?.length) return null
  const demand = payload.find(p => p.dataKey === 'demand')?.value
  const supply = payload.find(p => p.dataKey === 'supply')?.value
  const gap = demand && supply ? demand - supply : 0
  const pct = demand ? ((gap / demand) * 100).toFixed(1) : 0
  return (
    <div className="custom-tooltip">
      <div className="tooltip-date">{label}</div>
      {payload.map((p, i) => (
        <div key={i} className="tooltip-item">
          <span className="tooltip-dot" style={{ background: p.color }} />
          <span>{p.name}: {p.value.toLocaleString('id-ID')} Ton</span>
        </div>
      ))}
      <div className="tooltip-item" style={{ borderTop: '1px solid rgba(255,255,255,0.15)', marginTop: 6, paddingTop: 6 }}>
        <span>Gap: {gap > 0 ? '-' : '+'}{Math.abs(gap).toLocaleString('id-ID')} Ton ({pct}%)</span>
      </div>
    </div>
  )
}

const ROUTES_DATA = [
  {
    rank: 1, asal: 'Lampung', tujuan: 'DKI Jakarta', provinsi_asal: 'Lampung', provinsi_tujuan: 'DKI Jakarta',
    komoditas: 'Cabai Merah Keriting', margin: 8500, roi: 18, durasi: 2, frekuensi: '2x/minggu',
    kapasitas: 8, status: 'open', risk: 'LOW',
    detail: 'Mitra logistik: PT. Ekspres Nusantara, waktu terbaik: Senin-Rabu 05:00-08:00 WIB',
  },
  {
    rank: 2, asal: 'Solok', tujuan: 'Medan', provinsi_asal: 'Sumatera Barat', provinsi_tujuan: 'Sumatera Utara',
    komoditas: 'Beras Medium I', margin: 5200, roi: 12, durasi: 3, frekuensi: '3x/minggu',
    kapasitas: 6, status: 'open', risk: 'LOW',
    detail: 'Mitra logistik: CV. Andalas Jaya, waktu terbaik: Selasa-Kamis 06:00-09:00 WIB',
  },
  {
    rank: 3, asal: 'Bandung', tujuan: 'Surabaya', provinsi_asal: 'Jawa Barat', provinsi_tujuan: 'Jawa Timur',
    komoditas: 'Minyak Goreng Curah', margin: 3000, roi: 8, durasi: 2, frekuensi: '1x/minggu',
    kapasitas: 9.5, status: 'moderate', risk: 'MED',
    detail: 'Catatan: Kemacetan tinggi di jalur Pantura pada akhir pekan. Pertimbangkan jalur tol.',
  },
  {
    rank: 4, asal: 'Blitar', tujuan: 'Makassar', provinsi_asal: 'Jawa Timur', provinsi_tujuan: 'Sulawesi Selatan',
    komoditas: 'Beras Medium I', margin: 6800, roi: 15, durasi: 5, frekuensi: '1x/minggu',
    kapasitas: 12, status: 'open', risk: 'LOW',
    detail: 'Via kapal PELNI. Mitra: PT. Sinar Bahari. Waktu terbaik: Jumat minggu pertama tiap bulan.',
  },
  {
    rank: 5, asal: 'Garut', tujuan: 'Batam', provinsi_asal: 'Jawa Barat', provinsi_tujuan: 'Kepulauan Riau',
    komoditas: 'Cabai Merah Keriting', margin: 9200, roi: 21, durasi: 4, frekuensi: '2x/minggu',
    kapasitas: 5, status: 'open', risk: 'LOW',
    detail: 'High ROI karena keterbatasan pasokan di Batam. Permintaan tinggi dari sektor F&B.',
  },
  {
    rank: 6, asal: 'Jember', tujuan: 'Bali', provinsi_asal: 'Jawa Timur', provinsi_tujuan: 'Bali',
    komoditas: 'Minyak Goreng Curah', margin: 2400, roi: 6, durasi: 1, frekuensi: '3x/minggu',
    kapasitas: 8, status: 'moderate', risk: 'MED',
    detail: 'Persaingan tinggi di rute ini. Diferensiasi via kualitas grading produk.',
  },
]

const STATUS_CONFIG = {
  open:     { badge: '✅ Terbuka', color: '#16A34A', bg: 'rgba(34,197,94,0.1)' },
  moderate: { badge: '⚠️ Moderate', color: '#B45309', bg: 'rgba(234,179,8,0.12)' },
  closed:   { badge: '❌ Tertutup', color: '#DC2626', bg: 'rgba(239,68,68,0.1)' },
}

const RISK_CONFIG = {
  LOW: { label: '🟢 Low', color: '#16A34A' },
  MED: { label: '🟡 Medium', color: '#B45309' },
  HIGH: { label: '🔴 High', color: '#DC2626' },
}

export default function PeluangDistribusi() {
  const [sortKey, setSortKey] = useState('roi')
  const [sortDir, setSortDir] = useState('desc')
  const [filterStatus, setFilterStatus] = useState('Semua')
  const [filterKomoditas, setFilterKomoditas] = useState('Semua')
  const [expandedRow, setExpandedRow] = useState(null)
  const [period, setPeriod] = useState('30')

  const komoditasOptions = ['Semua', ...new Set(ROUTES_DATA.map(r => r.komoditas))]
  const statusOptions = ['Semua', 'open', 'moderate']

  
  const demandData = useMemo(() => generateDemandData(parseInt(period)), [period])
  const totalDemand = demandData.reduce((s, d) => s + d.demand, 0)
  const totalSupply = demandData.reduce((s, d) => s + d.supply, 0)
  const avgGap = ((totalDemand - totalSupply) / totalDemand * 100).toFixed(1)
  const efisiensi = (totalSupply / totalDemand * 100).toFixed(1)

  const sorted = useMemo(() => {
    return [...ROUTES_DATA]
      .filter(r => filterStatus === 'Semua' || r.status === filterStatus)
      .filter(r => filterKomoditas === 'Semua' || r.komoditas === filterKomoditas)
      .sort((a, b) => {
        const va = a[sortKey], vb = b[sortKey]
        if (va < vb) return sortDir === 'asc' ? -1 : 1
        if (va > vb) return sortDir === 'asc' ? 1 : -1
        return 0
      })
  }, [sortKey, sortDir, filterStatus, filterKomoditas])

  const handleSort = (key) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('desc') }
  }

  const SortIcon = ({ col }) => {
    if (sortKey !== col) return <ChevronsUpDown size={11} style={{ opacity: 0.4 }} />
    return sortDir === 'asc' ? <ChevronUp size={11} /> : <ChevronDown size={11} />
  }

  const highMargin = ROUTES_DATA.filter(r => r.roi >= 15).length
  const avgMargin = Math.round(ROUTES_DATA.reduce((s, r) => s + r.margin, 0) / ROUTES_DATA.length)
  const bestROI = Math.max(...ROUTES_DATA.map(r => r.roi))
  const openRoutes = ROUTES_DATA.filter(r => r.status === 'open').length

  return (
    <div>
      <div className="page-header">
        <h2>Supply & Distribution Optimizer</h2>
        <p>Supply-Demand Overview, Gap Analysis, dan Rekomendasi Rute Distribusi</p>
      </div>

      <h3 style={{ fontSize: 16, fontWeight: 800, color: '#0F172A', marginBottom: 12 }}>Supply-Demand Overview</h3>
      {/* Demand KPI Row */}
      <div style={{ display: 'grid', gridTemplateColumns: 'repeat(4, 1fr)', gap: 14, marginBottom: 24 }}>
        {[
          { label: 'Total Demand', value: `${(totalDemand/1000).toFixed(1)}K Ton`, color: '#3B82F6' },
          { label: 'Total Supply', value: `${(totalSupply/1000).toFixed(1)}K Ton`, color: '#10B981' },
          { label: 'Gap Rata-rata', value: `${avgGap}%`, color: '#EF4444' },
          { label: 'Efisiensi', value: `${efisiensi}%`, color: '#F97316' },
        ].map((c, i) => (
          <div key={i} className="kpi-card fade-in">
            <div className="kpi-label">{c.label}</div>
            <div className="kpi-value font-mono" style={{ color: c.color, fontSize: 22 }}>{c.value}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>Periode {period} hari</div>
          </div>
        ))}
      </div>

      <div style={{ display: 'flex', alignItems: 'center', gap: 12, marginBottom: 18 }}>
        <span style={{ fontSize: 13, fontWeight: 600, color: 'var(--text-secondary)', display: 'flex', alignItems: 'center', gap: 5 }}>
          <Clock size={14} /> Filter Periode:
        </span>
        <div className="toggle-group">
          {['7', '14', '30'].map(p => (
            <button key={p} className={`toggle-btn-item${period === p ? ' active' : ''}`} onClick={() => setPeriod(p)}>
              {p} Hari
            </button>
          ))}
        </div>
      </div>

      <h3 style={{ fontSize: 16, fontWeight: 800, color: '#0F172A', marginBottom: 12 }}>Gap Analysis</h3>
      {/* Area Chart */}
      <div className="chart-card" style={{ marginBottom: 32 }}>
        <ResponsiveContainer width="100%" height={280}>
          <AreaChart data={demandData} margin={{ top: 10, right: 16, left: 0, bottom: 5 }}>
            <defs>
              <linearGradient id="gDemand" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#3B82F6" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#3B82F6" stopOpacity={0} />
              </linearGradient>
              <linearGradient id="gSupply" x1="0" y1="0" x2="0" y2="1">
                <stop offset="5%" stopColor="#10B981" stopOpacity={0.2} />
                <stop offset="95%" stopColor="#10B981" stopOpacity={0} />
              </linearGradient>
            </defs>
            <CartesianGrid strokeDasharray="3 3" stroke="#F3F4F6" />
            <XAxis dataKey="tanggal" tick={{ fontSize: 10, fill: '#9CA3AF' }} interval="preserveStartEnd" minTickGap={40} />
            <YAxis tick={{ fontSize: 10, fill: '#9CA3AF' }} tickFormatter={v => `${v.toLocaleString('id-ID')}T`} width={60} />
            <Tooltip content={<DemandTooltip />} />
            <Legend wrapperStyle={{ fontSize: 12 }} />
            <Area type="monotone" dataKey="demand" name="Demand (Ton)" stroke="#3B82F6" strokeWidth={2.5} fill="url(#gDemand)" />
            <Area type="monotone" dataKey="supply" name="Supply (Ton)" stroke="#10B981" strokeWidth={2.5} fill="url(#gSupply)" />
          </AreaChart>
        </ResponsiveContainer>
      </div>

      <h3 style={{ fontSize: 16, fontWeight: 800, color: '#0F172A', marginBottom: 12 }}>Recommended Distribution Routes</h3>
      {/* Summary Cards */}
      <div className="metrics-grid" style={{ marginBottom: 24 }}>
        {[
          { label: 'Margin Tinggi (>15% ROI)', value: `${highMargin} Rute`, color: '#10B981', icon: Target },
          { label: 'Margin Rata-rata', value: `Rp ${avgMargin.toLocaleString()}/kg`, color: '#3B82F6', icon: BarChart2 },
          { label: 'ROI Terbaik Minggu Ini', value: `${bestROI}%`, color: '#F97316', icon: Target },
          { label: 'Rute Terbuka', value: `${openRoutes} / ${ROUTES_DATA.length}`, color: '#22C55E', icon: Truck },
        ].map((c, i) => (
          <div key={i} className="metric-card fade-in">
            <div className="metric-icon" style={{ background: `${c.color}18`, color: c.color }}>
              <c.icon size={20} />
            </div>
            <div className="metric-label">{c.label}</div>
            <div className="metric-value" style={{ fontSize: 20 }}>{c.value}</div>
          </div>
        ))}
      </div>

      {/* Filters */}
      <div className="filter-bar">
        <select className="filter-select" value={filterKomoditas} onChange={e => setFilterKomoditas(e.target.value)} style={{ minWidth: 200 }}>
          {komoditasOptions.map(k => <option key={k} value={k}>{k}</option>)}
        </select>
        <select className="filter-select" value={filterStatus} onChange={e => setFilterStatus(e.target.value)} style={{ minWidth: 150 }}>
          {statusOptions.map(s => <option key={s} value={s}>{s === 'Semua' ? 'Semua Status' : s === 'open' ? '✅ Terbuka' : '⚠️ Moderate'}</option>)}
        </select>
        <span style={{ fontSize: 12, color: 'var(--text-muted)' }}>{sorted.length} rute ditemukan</span>
      </div>

      {/* Routes Table */}
      <div className="data-table-wrapper fade-in">
        <div className="table-scroll">
          <table className="data-table">
            <thead>
              <tr>
                {[
                  ['rank', 'Rank'],
                  ['asal', 'Asal'],
                  ['tujuan', 'Tujuan'],
                  ['komoditas', 'Komoditas'],
                  ['margin', 'Margin (Rp/kg)'],
                  ['roi', 'ROI (%)'],
                  ['durasi', 'Durasi (Hari)'],
                  ['status', 'Status'],
                  [null, 'Detail'],
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
              {sorted.map((r) => {
                const statusCfg = STATUS_CONFIG[r.status]
                const riskCfg = RISK_CONFIG[r.risk]
                const isExpanded = expandedRow === r.rank
                return (
                  <React.Fragment key={r.rank}>
                    <tr style={{ cursor: 'pointer' }} onClick={() => setExpandedRow(isExpanded ? null : r.rank)}>
                      <td>
                        <div style={{
                          width: 28, height: 28, borderRadius: 7, background: 'var(--primary-light)',
                          color: 'var(--primary-dark)', display: 'flex', alignItems: 'center', justifyContent: 'center',
                          fontWeight: 800, fontSize: 12,
                        }}>{r.rank}</div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600, fontSize: 13 }}>{r.asal}</div>
                        <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{r.provinsi_asal}</div>
                      </td>
                      <td>
                        <div style={{ fontWeight: 600, fontSize: 13 }}>{r.tujuan}</div>
                        <div style={{ fontSize: 10, color: 'var(--text-muted)' }}>{r.provinsi_tujuan}</div>
                      </td>
                      <td style={{ fontSize: 12 }}>{r.komoditas}</td>
                      <td>
                        <span className="font-mono" style={{ fontWeight: 700, color: 'var(--primary-dark)', fontSize: 13 }}>
                          Rp {r.margin.toLocaleString('id-ID')}
                        </span>
                      </td>
                      <td>
                        <span style={{
                          background: r.roi >= 15 ? 'rgba(16,185,129,0.12)' : 'rgba(59,130,246,0.1)',
                          color: r.roi >= 15 ? 'var(--primary-dark)' : '#2563EB',
                          fontWeight: 700, fontSize: 12, padding: '3px 8px', borderRadius: 20,
                        }}>
                          {r.roi}%
                        </span>
                      </td>
                      <td style={{ fontSize: 12 }}>
                        {r.durasi}H &nbsp;
                        <span style={{ color: 'var(--text-muted)', fontSize: 10 }}>{r.frekuensi}</span>
                      </td>
                      <td>
                        <span style={{ background: statusCfg.bg, color: statusCfg.color, fontWeight: 600, fontSize: 11, padding: '3px 8px', borderRadius: 20 }}>
                          {statusCfg.badge}
                        </span>
                      </td>
                      <td>
                        <button style={{
                          background: 'none', border: 'none', cursor: 'pointer', color: 'var(--primary)',
                          fontWeight: 600, fontSize: 12, display: 'flex', alignItems: 'center', gap: 3,
                        }}>
                          {isExpanded ? <ChevronUp size={14} /> : <ChevronDown size={14} />}
                          {isExpanded ? 'Tutup' : 'Detail'}
                        </button>
                      </td>
                    </tr>
                    {isExpanded && (
                      <tr key={`detail-${r.rank}`}>
                        <td colSpan={9} style={{ background: 'rgba(16,185,129,0.03)', padding: '12px 16px' }}>
                          <div style={{ fontSize: 12, color: 'var(--text-secondary)', lineHeight: 1.6 }}>
                            <strong>📋 Detail Rute #{r.rank}:</strong> {r.detail}
                            <span style={{ marginLeft: 12, color: riskCfg.color, fontWeight: 600 }}>
                              Risk Score: {riskCfg.label}
                            </span>
                            <span style={{ marginLeft: 12, color: 'var(--text-muted)' }}>
                              Kapasitas: {r.kapasitas} Ton/truk
                            </span>
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
