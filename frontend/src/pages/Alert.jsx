import { useState, useEffect, useMemo } from 'react'
import { Bell, AlertTriangle, TrendingUp, Filter, Search, ChevronUp, ChevronDown, ChevronsUpDown } from 'lucide-react'
import {
  fetchAlert, formatRupiah, formatPct, getKomoditasClass, getTrenClass,
} from '../api'

export default function Alert() {
  const [alerts, setAlerts] = useState([])
  const [filter, setFilter] = useState('Semua')
  const [search, setSearch] = useState('')
  const [sortKey, setSortKey] = useState('kenaikan_pct')
  const [sortDir, setSortDir] = useState('desc')
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState(null)

  useEffect(() => {
    async function load() {
      try {
        setLoading(true)
        const data = await fetchAlert()
        setAlerts(data)
      } catch (err) {
        setError(err.message)
      } finally {
        setLoading(false)
      }
    }
    load()
  }, [])

  const komoditasOptions = ['Semua', ...new Set(alerts.map(a => a.komoditas))]

  const filtered = useMemo(() => {
    let list = alerts
    if (filter !== 'Semua') list = list.filter(a => a.komoditas === filter)
    if (search) list = list.filter(a =>
      a.provinsi.toLowerCase().includes(search.toLowerCase()) ||
      a.komoditas.toLowerCase().includes(search.toLowerCase())
    )
    return [...list].sort((a, b) => {
      let va = a[sortKey], vb = b[sortKey]
      if (typeof va === 'string') { va = va.toLowerCase(); vb = vb.toLowerCase() }
      if (va < vb) return sortDir === 'asc' ? -1 : 1
      if (va > vb) return sortDir === 'asc' ? 1 : -1
      return 0
    })
  }, [alerts, filter, search, sortKey, sortDir])

  const handleSort = (key) => {
    if (sortKey === key) setSortDir(d => d === 'asc' ? 'desc' : 'asc')
    else { setSortKey(key); setSortDir('desc') }
  }

  const SortIcon = ({ col }) => {
    if (sortKey !== col) return <ChevronsUpDown size={11} style={{ opacity: 0.4 }} />
    return sortDir === 'asc' ? <ChevronUp size={11} /> : <ChevronDown size={11} />
  }

  const totalProvinsi = new Set(filtered.map(a => a.provinsi)).size
  const avgKenaikan = filtered.length > 0
    ? filtered.reduce((sum, a) => sum + a.kenaikan_pct, 0) / filtered.length : 0
  const komoditasCounts = {}
  alerts.forEach(a => { komoditasCounts[a.komoditas] = (komoditasCounts[a.komoditas] || 0) + 1 })
  const topKomoditas = Object.entries(komoditasCounts).sort((a, b) => b[1] - a[1])[0]

  const getUrgencyBadge = (pct) => {
    if (pct > 15) return <span className="badge badge-danger">🔴 Kritis</span>
    if (pct > 10) return <span className="badge badge-accent">🟠 Tinggi</span>
    if (pct > 5) return <span className="badge badge-warning">🟡 Sedang</span>
    return <span className="badge badge-success">🟢 Rendah</span>
  }



  const getRowClass = (pct) => {
    if (pct > 15) return 'row-naik'
    if (pct > 10) return 'row-warn'
    return ''
  }

  if (error) {
    return (
      <div>
        <div className="page-header"><h2>Alert System</h2></div>
        <div className="error-state">
          <div className="error-icon">⚠️</div>
          <h3>Tidak dapat terhubung ke server</h3>
          <p>{error}</p>
        </div>
      </div>
    )
  }

  return (
    <div>
      <div className="page-header">
        <h2>Alert System</h2>
        <p>Peringatan provinsi dengan prediksi kenaikan harga signifikan dalam 30 hari ke depan</p>
      </div>

      {/* ── Summary Cards ── */}
      {loading ? (
        <div className="alert-summary">{[0,1,2].map(i => <div key={i} className="skeleton skeleton-card" />)}</div>
      ) : (
        <div className="alert-summary">
          <div className="alert-summary-item fade-in">
            <div className="summary-label">Total Provinsi Alert</div>
            <div className="summary-value font-mono" style={{ color: 'var(--danger)' }}>{totalProvinsi}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>dari {new Set(alerts.map(a => a.provinsi)).size} total</div>
          </div>
          <div className="alert-summary-item fade-in">
            <div className="summary-label">Rata-rata Kenaikan</div>
            <div className="summary-value font-mono" style={{ color: 'var(--accent)' }}>{formatPct(avgKenaikan)}</div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>prediksi 30 hari</div>
          </div>
          <div className="alert-summary-item fade-in">
            <div className="summary-label">Komoditas Terbanyak</div>
            <div className="summary-value" style={{ fontSize: 18, color: 'var(--text-primary)' }}>
              {topKomoditas ? topKomoditas[0] : '—'}
            </div>
            <div style={{ fontSize: 11, color: 'var(--text-muted)', marginTop: 4 }}>
              {topKomoditas ? `${topKomoditas[1]} alert` : ''}
            </div>
          </div>
        </div>
      )}

      {/* ── Filters ── */}
      <div className="filter-bar">
        <div className="search-wrapper">
          <Search size={14} className="search-icon" />
          <input
            type="text"
            className="search-input"
            placeholder="Cari provinsi atau komoditas..."
            value={search}
            onChange={e => setSearch(e.target.value)}
          />
        </div>
        <select className="filter-select" value={filter} onChange={e => setFilter(e.target.value)} style={{ minWidth: 180 }}>
          {komoditasOptions.map(k => <option key={k} value={k}>{k}</option>)}
        </select>
        <span style={{ fontSize: 12, color: 'var(--text-muted)', marginLeft: 4 }}>
          {filtered.length} dari {alerts.length} alert
        </span>
      </div>

      {/* ── Table ── */}
      {loading ? (
        <div className="skeleton skeleton-table" />
      ) : (
        <div className="data-table-wrapper fade-in">
          <div className="table-scroll">
            <table className="data-table">
              <thead>
                <tr>
                  {[
                    ['komoditas', 'Komoditas'],
                    ['provinsi', 'Provinsi'],
                    ['harga_sekarang', 'Harga Saat Ini'],
                    ['kenaikan_pct', 'Prediksi Kenaikan (%)'],
                    [null, 'Tingkat Risiko'],
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
                {filtered.map((a, i) => (
                  <tr key={`${a.komoditas}-${a.provinsi}-${i}`} className={getRowClass(a.kenaikan_pct)}>
                    <td>
                      <span className={`komoditas-badge ${getKomoditasClass(a.komoditas)}`}>{a.komoditas}</span>
                    </td>
                    <td style={{ fontWeight: 600 }}>{a.provinsi}</td>
                    <td className="font-mono">{formatRupiah(a.harga_sekarang)}</td>
                    <td>
                      <span className={`pct-badge ${a.kenaikan_pct > 10 ? 'danger' : a.kenaikan_pct >= 5 ? 'warning' : 'success'}`}>
                        ↑ {formatPct(a.kenaikan_pct)}
                      </span>
                    </td>
                    <td>{getUrgencyBadge(a.kenaikan_pct)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
