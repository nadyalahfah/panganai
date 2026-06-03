import { useState } from "react";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { Menu, X } from "lucide-react";
import Sidebar from "./components/Sidebar";
import Toast from "./components/Toast";
import Dashboard from "./pages/Dashboard";
import Prediksi from "./pages/Prediksi";
import Alert from "./pages/Alert";
import PeluangDistribusi from "./pages/PeluangDistribusi";
import TabelHargaHarian from "./pages/TabelHargaHarian";
import LaporanEkspor from "./pages/LaporanEkspor";

function App() {
  const [sidebarCollapsed, setSidebarCollapsed] = useState(false);
  const [mobileSidebarOpen, setMobileSidebarOpen] = useState(false);
  const [alerts, setAlerts] = useState([]);

  const sidebarWidth = sidebarCollapsed
    ? "var(--sidebar-collapsed-width)"
    : "var(--sidebar-width)";

  return (
    <BrowserRouter>
      <Toast />
      <div className="app-layout">
        <div className="mobile-topbar">
          <button
            className="mobile-menu-btn"
            type="button"
            onClick={() => setMobileSidebarOpen((open) => !open)}
            aria-label={mobileSidebarOpen ? "Tutup navigasi" : "Buka navigasi"}
            aria-expanded={mobileSidebarOpen}
          >
            {mobileSidebarOpen ? <X size={20} /> : <Menu size={20} />}
          </button>
          <div className="mobile-brand flex items-center gap-2">
            <img src="/logo-panganai.svg" alt="logo-panganai" width={25} />
            <div className="flex flex-col gap-0.5">
              <strong>PanganAI</strong>
              <span>Monitoring & Prediksi</span>
            </div>
          </div>
        </div>
        {mobileSidebarOpen && (
          <button
            className="mobile-sidebar-backdrop"
            type="button"
            aria-label="Tutup navigasi"
            onClick={() => setMobileSidebarOpen(false)}
          />
        )}
        <Sidebar
          collapsed={sidebarCollapsed}
          mobileOpen={mobileSidebarOpen}
          onCloseMobile={() => setMobileSidebarOpen(false)}
          onToggle={() => setSidebarCollapsed((c) => !c)}
        />
        <div
          className="app-main-shell"
          style={{
            marginLeft: sidebarWidth,
            flex: 1,
            minWidth: 0,
            transition: "margin-left 0.25s ease",
          }}
        >
          <main className="main-content">
            <Routes>
              <Route
                path="/"
                element={<Dashboard onAlertsLoaded={setAlerts} />}
              />
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
  );
}

export default App;
