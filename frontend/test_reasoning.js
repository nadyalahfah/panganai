const getSmartReasoning = (commodity, province, forecastPct, riskLevel) => {
    const c = (commodity || '').toLowerCase();
    const p = province || '';
    const pct = forecastPct ? forecastPct.toFixed(1) : 0;
    
    if (riskLevel === 'High Risk Alert' || riskLevel === 'Intervensi Segera') {
      if (c.includes('cabai') || c.includes('merah') || c.includes('rawit')) {
        return `Prediksi kenaikan harga ${commodity} di ${p}\nmencapai ${pct}%.\n\nPrioritas tindakan:\n\n• Verifikasi stok distributor utama\n• Koordinasi pasokan antar wilayah\n• Monitoring sentra produksi terdekat`;
      } else if (c.includes('beras')) {
        return `Potensi tekanan harga ${commodity}\ndi ${p} mencapai ${pct}%.\n\nPrioritas tindakan:\n\n• Evaluasi stok Bulog\n• Pertimbangkan operasi pasar\n• Monitoring distribusi antar wilayah`;
      } else if (c.includes('telur') || c.includes('ayam')) {
        return `Potensi kenaikan harga ${commodity}\ndi ${p} mencapai ${pct}%.\n\nPrioritas tindakan:\n\n• Monitoring pasokan peternak\n• Evaluasi distribusi regional\n• Penguatan koordinasi rantai pasok`;
      } else {
        return `Prediksi kenaikan harga mencapai ${pct}%.\nIntervensi segera direkomendasikan.`;
      }
    }
};

console.log("--- CABAI ---");
console.log(getSmartReasoning("Cabai Merah", "Jawa Barat", 12.5, "High Risk Alert"));

console.log("\n--- BERAS ---");
console.log(getSmartReasoning("Beras Premium", "Aceh", 15.2, "High Risk Alert"));

console.log("\n--- TELUR ---");
console.log(getSmartReasoning("Telur Ayam", "DKI Jakarta", 8.4, "High Risk Alert"));
