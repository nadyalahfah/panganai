import { NavLink, useLocation } from "react-router-dom";
import {
  LayoutDashboard,
  TrendingUp,
  Bell,
  BarChart2,
  Gift,
  Truck,
  Table2,
  FileText,
  ChevronLeft,
  ChevronRight,
  Wheat,
} from "lucide-react";
import { PiUserCircle } from "react-icons/pi";

const NAV_GROUPS = [
  {
    label: "Overview",
    items: [{ to: "/", label: "Dashboard", icon: LayoutDashboard }],
  },
  {
    label: "AI Analytics",
    items: [
      { to: "/prediksi", label: "Prediksi Harga", icon: TrendingUp },
      { to: "/alert", label: "Alert System", icon: Bell },
    ],
  },
  {
    label: "Recommendations",
    items: [{ to: "/distribusi", label: "Supply & Distribution", icon: Truck }],
  },
  {
    label: "Data & Reports",
    items: [
      {
        to: "/harga-harian",
        label: "Market Intelligence Center",
        icon: Table2,
      },
      { to: "/laporan", label: "AI Reports Center", icon: FileText },
    ],
  },
];

export default function Sidebar({
  collapsed,
  mobileOpen = false,
  onCloseMobile,
  onToggle,
}) {
  return (
    <aside
      className={`sidebar${collapsed ? " collapsed" : ""}${mobileOpen ? " mobile-open" : ""}`}
    >
      {/* Logo */}
      <div className="sidebar-logo">
        <div className="sidebar-logo-text flex items-center gap-2">
          <img src="/logo-panganai.svg" alt="logo-panganai" width={30} />
          <div>
            <h1>PanganAI</h1>
            <p>Monitoring & Prediksi</p>
          </div>
        </div>
      </div>

      {/* Toggle button */}
      <div className="sidebar-toggle">
        <button
          className="toggle-btn"
          onClick={onToggle}
          aria-label={collapsed ? "Expand sidebar" : "Collapse sidebar"}
          title={collapsed ? "Expand sidebar" : "Collapse sidebar"}
        >
          {collapsed ? <ChevronRight size={14} /> : <ChevronLeft size={14} />}
        </button>
      </div>

      {/* Navigation */}
      <nav className="sidebar-nav" aria-label="Main navigation">
        {NAV_GROUPS.map((group) => (
          <div key={group.label} className="sidebar-nav-group">
            <div className="sidebar-nav-group-label">{group.label}</div>
            {group.items.map(({ to, label, icon: Icon }) => (
              <NavLink
                key={to}
                to={to}
                end={to === "/"}
                className={({ isActive }) =>
                  `nav-link${isActive ? " active" : ""}`
                }
                title={collapsed ? label : undefined}
                aria-label={label}
                onClick={onCloseMobile}
              >
                <span className="nav-link-icon">
                  <Icon size={18} />
                </span>
                <span className="nav-link-text">{label}</span>
              </NavLink>
            ))}
          </div>
        ))}
      </nav>
    </aside>
  );
}
