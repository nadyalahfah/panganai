import os
import re

file_path = 'frontend/src/components/EarlyWarningSystem.jsx'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove DIST_SOURCES dict
content = re.sub(
    r'const DIST_SOURCES = \{.*?\};\n\n',
    '',
    content,
    flags=re.DOTALL
)

# 2. Update processedAlerts useMemo
replacement = """
  const processedAlerts = useMemo(() => {
    if (!alerts) return [];
    
    return alerts.map(a => {
      let level = 'Low';
      let colorClass = 'info'; 
      let bg = '#F1F5F9';
      let color = '#64748B';
      let Icon = Info;
      let action = 'Monitor';
      let cause = a.ai_reasoning || 'Fluktuasi dalam batas wajar';
      let distRec = '';
      
      // Derive action from level if not explicitly provided
      const risk = (a.risk_level || '').toUpperCase();
      const pct = a.kenaikan_pct || 0;
      
      if (risk === 'CRITICAL' || pct > 15) {
        level = 'Critical';
        colorClass = 'danger';
        bg = '#FEF2F2';
        color = '#EF4444';
        Icon = AlertTriangle;
        action = 'Intervensi Pasokan';
        if (!cause || cause.length < 10) cause = 'Indikasi defisit pasokan serius.';
      } else if (risk === 'HIGH' || pct >= 10) {
        level = 'High';
        colorClass = 'warning';
        bg = '#FFF7ED';
        color = '#F97316';
        Icon = AlertCircle;
        action = 'Inspeksi Lapangan';
        if (!cause || cause.length < 10) cause = 'Tren kenaikan harga signifikan.';
      } else if (risk === 'WATCH' || pct >= 5) {
        level = 'Medium';
        colorClass = 'info';
        bg = '#FEF9C3';
        color = '#CA8A04';
        Icon = Info;
        action = 'Monitor Lanjut';
        if (!cause || cause.length < 10) cause = 'Gejolak harga minor terdeteksi.';
      }

      return {
        ...a, level, colorClass, bg, color, Icon, action, cause, distRec, days: 7
      };
    }).sort((a, b) => (b.kenaikan_pct || 0) - (a.kenaikan_pct || 0));
  }, [alerts]);
"""

content = re.sub(
    r'  const processedAlerts = useMemo\(\(\) => \{[\s\S]*?\}, \[alerts\]\);',
    replacement.strip(),
    content
)

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)

print("EarlyWarningSystem.jsx updated successfully.")
