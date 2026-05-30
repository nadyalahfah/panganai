import { useState } from 'react'
import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom'
import Sidebar from './components/Sidebar'
import Header from './components/Header'
import Toast from './components/Toast'
import Dashboard from './pages/Dashboard'
import Prediksi from './pages/Prediksi'
import Alert from './pages/Alert'
import PeluangDistribusi from './pages/PeluangDistribusi'
import TabelHargaHarian from './pages/TabelHargaHarian'
import LaporanEkspor from './pages/LaporanEkspor'

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false)
  const [alerts, setAlerts] = useState([])

  const sidebarWidth = sidebarCollapsed
    ? 'var(--sidebar-collapsed-width)'
    : 'var(--sidebar-width)'

  return (
    <BrowserRouter>
      <Toast />
      <div className="app-layout">
        <Sidebar
          collapsed={sidebarCollapsed}
          onToggle={() => setSidebarCollapsed((c) => !c)}
        />
        <div
          style={{
            marginLeft: sidebarWidth,
            flex: 1,
            minWidth: 0,
            transition: 'margin-left 0.25s ease',
          }}
        >

          <main className="main-content">
            <Routes>
              <Route path="/" element={<Dashboard onAlertsLoaded={setAlerts} />} />
              <Route path="/prediksi" element={<Prediksi />} />
              <Route path="/alert" element={<Alert />} />
              <Route path="/distribusi" element={<PeluangDistribusi />} />
              <Route path="/harga-harian" element={<TabelHargaHarian />} />
              <Route path="/laporan" element={<LaporanEkspor />} />
              <Route path="*" element={<Navigate to="/" replace />} />
            </Routes>
          </main>
        </div>
      </div>
    </BrowserRouter>
  )
}

export default App
