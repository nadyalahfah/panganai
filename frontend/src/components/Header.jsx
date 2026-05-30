import { useLocation } from 'react-router-dom'
import { Bell, Moon, Sun } from 'lucide-react'
import { useState } from 'react'
import { PiUserCircle } from 'react-icons/pi'

const PAGE_META = {
  '/': { breadcrumb: ['Overview'], title: 'Dashboard' },
  '/prediksi': { breadcrumb: ['AI Analytics'], title: 'Prediksi Harga' },
  '/demand': { breadcrumb: ['AI Analytics'], title: 'Demand Analysis' },
  '/alert': { breadcrumb: ['AI Analytics'], title: 'Alert System' },
  '/distribusi': { breadcrumb: ['Recommendations'], title: 'Supply & Distribution Optimizer' },
  '/harga-harian': { breadcrumb: ['Data & Reports'], title: 'Market Intelligence Center' },
  '/laporan': { breadcrumb: ['Data & Reports'], title: 'AI Reports Center' },
}

export default function Header({ sidebarWidth, alertCount }) {
  const location = useLocation()
  const [darkMode, setDarkMode] = useState(false)

  const meta = PAGE_META[location.pathname] || { breadcrumb: [], title: 'PanganAI' }

  return (
    <header
      className="header-bar"
      style={{ left: sidebarWidth }}
    >
      <div className="header-left">
        <div className="header-breadcrumb">
          <span>PanganAI</span>
          {meta.breadcrumb.map((crumb) => (
            <span key={crumb}>
              <span className="header-breadcrumb-sep">/</span>
              <span>{crumb}</span>
            </span>
          ))}
        </div>
        <div className="header-title">{meta.title}</div>
      </div>

      <div className="header-right">
        {/* Notification */}
        <button
          className="header-icon-btn"
          aria-label="Notifikasi"
          title="Notifikasi"
        >
          <Bell size={16} />
          {alertCount > 0 && (
            <span className="notification-badge">
              {alertCount > 99 ? '99+' : alertCount}
            </span>
          )}
        </button>

        {/* Dark mode toggle */}
        <button
          className="header-icon-btn"
          aria-label="Toggle tema"
          title="Toggle gelap/terang"
          onClick={() => setDarkMode((d) => !d)}
        >
          {darkMode ? <Sun size={16} /> : <Moon size={16} />}
        </button>

        {/* User */}
        <div className="header-user" role="button" tabIndex={0}>
          <div className="header-avatar">
           <PiUserCircle color='#6B7280' size={28}/> 
          </div>
        </div>
      </div>
    </header>
  )
}
