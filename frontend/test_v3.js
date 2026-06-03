const getSmartReasoning = (commodity, province, forecastPct, riskLevel, currentPrice) => {
    const c = (commodity || '').toLowerCase();
    const p = province || '';
    const pct = forecastPct ? forecastPct.toFixed(1) : 0;
    
    const WESTERN = ['aceh', 'sumatera utara', 'sumatera barat', 'riau', 'jambi', 'sumatera selatan', 'bengkulu', 'lampung'];
    const JAVA = ['dki jakarta', 'jawa barat', 'jawa tengah', 'di yogyakarta', 'jawa timur', 'banten'];
    const EASTERN = ['ntt', 'nusa tenggara timur', 'maluku', 'maluku utara', 'papua', 'papua barat', 'papua tengah', 'papua selatan', 'papua pegunungan'];
    const KALIMANTAN = ['kalimantan barat', 'kalimantan tengah', 'kalimantan selatan', 'kalimantan timur', 'kalimantan utara'];
    const SULAWESI = ['sulawesi utara', 'gorontalo', 'sulawesi tengah', 'sulawesi barat', 'sulawesi selatan', 'sulawesi tenggara'];
    
    const pLow = p.toLowerCase();
    let geoMod = "";
    if (WESTERN.includes(pLow)) {
      geoMod = "Fokus pada pemantauan distribusi antar-kabupaten dan stabilitas pasokan pasar utama.";
    } else if (JAVA.includes(pLow) || pLow === 'jakarta') {
      geoMod = "Wilayah merupakan pusat konsumsi nasional. Monitoring distribusi dan kesiapan stok pasar strategis direkomendasikan.";
    } else if (EASTERN.includes(pLow)) {
      geoMod = "Wilayah memiliki tantangan logistik yang lebih tinggi. Evaluasi distribusi antar-pulau dan kesiapan pasokan regional direkomendasikan.";
    } else if (KALIMANTAN.some(k => pLow.includes(k) || pLow === 'kalimantan')) {
      geoMod = "Monitoring rantai distribusi lintas wilayah dan ketersediaan stok regional direkomendasikan.";
    } else if (SULAWESI.some(s => pLow.includes(s) || pLow === 'sulawesi' || pLow === 'gorontalo')) {
      geoMod = "Perlu pemantauan distribusi regional dan koordinasi pasokan antar-provinsi.";
    }
    
    let priceStr = "";
    if (currentPrice) {
      priceStr = `Harga saat ini Rp${currentPrice.toLocaleString('id-ID')}/kg dengan proyeksi kenaikan ${pct}%.`;
    } else {
      priceStr = `Proyeksi kenaikan mencapai ${pct}%.`;
    }

    let actionStr = "";
    if (riskLevel === 'High Risk Alert' || riskLevel === 'Intervensi Segera') {
      if (c.includes('cabai')) {
        actionStr = `Prioritas tindakan:\n• Verifikasi stok distributor utama\n• Koordinasi pasokan antar wilayah\n• Monitoring sentra produksi terdekat`;
      } else if (c.includes('bawang')) {
        actionStr = `Prioritas tindakan:\n• Pengecekan stok gudang penyimpanan\n• Operasi pasar komoditas bawang\n• Percepatan distribusi dari sentra panen`;
      } else if (c.includes('beras')) {
        actionStr = `Prioritas tindakan:\n• Evaluasi stok Bulog\n• Pertimbangkan operasi pasar\n• Monitoring distribusi antar wilayah`;
      } else if (c.includes('telur') || c.includes('ayam')) {
        actionStr = `Prioritas tindakan:\n• Monitoring pasokan peternak\n• Evaluasi distribusi regional\n• Penguatan koordinasi rantai pasok`;
      } else if (c.includes('minyak')) {
        actionStr = `Prioritas tindakan:\n• Pengawasan stok distributor D1/D2\n• Pemantauan kepatuhan HET\n• Inspeksi pasar berkelanjutan`;
      } else {
        actionStr = `Intervensi segera direkomendasikan untuk menstabilkan gejolak harga.`;
      }
    }
    return `${priceStr}\n\n${actionStr}\n\n${geoMod}`;
  };

console.log("--- CABAI ---");
console.log(getSmartReasoning("Cabai Merah Keriting", "Jawa Timur", 12.5, "High Risk Alert", 52000));

console.log("\n--- BAWANG ---");
console.log(getSmartReasoning("Bawang Merah", "Aceh", 11.2, "High Risk Alert", 38000));

console.log("\n--- BERAS ---");
console.log(getSmartReasoning("Beras Premium", "Sulawesi Selatan", 8.4, "High Risk Alert", 16000));

console.log("\n--- TELUR ---");
console.log(getSmartReasoning("Telur Ayam Ras", "Kalimantan Barat", 10.1, "High Risk Alert", 32000));

console.log("\n--- MINYAK ---");
console.log(getSmartReasoning("Minyak Goreng Curah", "Papua Barat", 15.6, "High Risk Alert", 18500));

console.log("\n=====================");
console.log("PROVINCE EXAMPLES");
console.log("=====================\n");

console.log("--- PAPUA BARAT ---");
console.log(getSmartReasoning("Beras Premium", "Papua Barat", 15.6, "High Risk Alert", 16000));

console.log("\n--- SULAWESI SELATAN ---");
console.log(getSmartReasoning("Beras Premium", "Sulawesi Selatan", 15.6, "High Risk Alert", 16000));

console.log("\n--- JAWA BARAT ---");
console.log(getSmartReasoning("Beras Premium", "Jawa Barat", 15.6, "High Risk Alert", 16000));
