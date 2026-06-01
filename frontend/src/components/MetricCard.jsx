import { TrendingUp, TrendingDown, Minus } from "lucide-react";

export default function MetricCard({
  label,
  value,
  icon: Icon,
  color,
  trend,
  trendPct,
  footer,
}) {
  const trendEl =
    trendPct != null ? (
      trendPct > 0 ? (
        <span className="metric-trend" style={{ color: "var(--danger)" }}>
          <TrendingUp size={13} /> +{trendPct.toFixed(1)}%
        </span>
      ) : trendPct < 0 ? (
        <span className="metric-trend" style={{ color: "var(--success)" }}>
          <TrendingDown size={13} /> {trendPct.toFixed(1)}%
        </span>
      ) : (
        <span className="metric-trend" style={{ color: "var(--gray-500)" }}>
          <Minus size={13} /> Stabil
        </span>
      )
    ) : null;

  return (
    <div className="metric-card flex items-stretch gap-4">
      <div className="w-0.75 h-full bg-gray-200 rounded-full"></div>
      <div className="flex-1">
        <div className="flex items-center gap-2">
          <div className="metric-label">{label}</div>
        </div>
        <div className="flex items-center gap-2">
          <div className="metric-value font-bold">{value}</div>
          {trendEl}
        </div>
        {footer && <div className="metric-footer">{footer}</div>}
      </div>
    </div>
  );
}
