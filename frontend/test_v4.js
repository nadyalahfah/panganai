const getSmartReasoning = (commodity, province, forecastPct, riskLevel, currentPrice) => {
    const c = (commodity || '').toLowerCase();
    const p = province || '';
    const pLow = p.toLowerCase();
    const pct = forecastPct ? forecastPct.toFixed(1) : 0;
    
    // Base Price String
    let priceStr = "";
    if (currentPrice) {
      priceStr = `Harga saat ini Rp${currentPrice.toLocaleString('id-ID')}/kg dengan proyeksi kenaikan ${pct}%.`;
    } else {
      priceStr = `Proyeksi kenaikan mencapai ${pct}%.`;
    }

    // Commodity-Specific Intervention Logic
    let actionStr = "";
    if (riskLevel === 'High Risk Alert' || riskLevel === 'Intervensi Segera') {
      if (c.includes('cabai')) {
        actionStr = `Prioritas tindakan:\n• Verifikasi stok distributor utama\n• Monitoring sentra produksi terdekat\n• Perkuat jalur pasok antar wilayah`;
      } else if (c.includes('bawang')) {
        actionStr = `Prioritas tindakan:\n• Pengecekan stok gudang penyimpanan\n• Percepatan distribusi dari sentra panen\n• Operasi pasar spesifik komoditas`;
      } else if (c.includes('beras')) {
        actionStr = `Prioritas tindakan:\n• Evaluasi cadangan stok Bulog\n• Operasi pasar & SPHP\n• Persiapan intervensi cadangan strategis`;
      } else if (c.includes('telur') || c.includes('ayam')) {
        actionStr = `Prioritas tindakan:\n• Monitoring pasokan peternak\n• Evaluasi biaya pakan ternak\n• Penguatan koordinasi rantai distribusi`;
      } else if (c.includes('minyak')) {
        actionStr = `Prioritas tindakan:\n• Pemantauan ketat kepatuhan HET\n• Audit stok tingkat distributor\n• Inspeksi pasar berkelanjutan`;
      } else {
        actionStr = `Intervensi segera direkomendasikan untuk menstabilkan gejolak harga.`;
      }
    } else if (riskLevel === 'Medium Risk Alert' || riskLevel === 'Monitoring Prioritas') {
      if (c.includes('cabai') || c.includes('bawang')) {
        actionStr = `Sinyal tekanan harga Hortikultura mulai muncul.\nDisarankan pemantauan distribusi dan evaluasi pasokan.`;
      } else if (c.includes('beras')) {
        actionStr = `Terindikasi peningkatan tekanan harga.\nEvaluasi ketersediaan stok dan distribusi direkomendasikan.`;
      } else if (c.includes('telur') || c.includes('ayam')) {
        actionStr = `Tekanan harga protein mulai terdeteksi.\nPemantauan rantai pasok direkomendasikan.`;
      } else {
        actionStr = `Sinyal tekanan harga mulai terdeteksi.\nPemantauan distribusi dan evaluasi stok direkomendasikan.`;
      }
    } else {
      actionStr = `Kondisi pasar relatif stabil.\nPemantauan berkala direkomendasikan.`;
    }
    
    // Region-Specific Intelligence
    let geoMod = "";
    if (pLow.includes('papua')) {
      geoMod = "Mengingat tantangan inter-island logistics, siapkan shipping readiness untuk koridor timur.";
    } else if (pLow.includes('aceh')) {
      geoMod = "Optimalkan inter-district distribution sepanjang koridor pasokan Sumatera Utara.";
    } else if (pLow.includes('jambi')) {
      geoMod = "Evaluasi plantation logistics dan amankan jalur distribusi Sumatera bagian tengah.";
    } else if (pLow.includes('sulawesi selatan')) {
      geoMod = "Sebagai regional hub, perkuat koordinasi untuk mendukung distribusi Indonesia Timur.";
    } else if (pLow.includes('jawa barat') || pLow.includes('jakarta') || pLow.includes('banten')) {
      geoMod = "Tekanan consumer demand tinggi. Lakukan monitoring strategis pada pasar urban utama.";
    } else if (pLow.includes('sumatera')) {
      geoMod = "Fokus pada pemantauan distribusi antar-kabupaten dan rute lintas Sumatera.";
    } else if (pLow.includes('jawa')) {
      geoMod = "Wilayah padat populasi. Pastikan kelancaran jalur distribusi darat strategis.";
    } else if (pLow.includes('kalimantan')) {
      geoMod = "Monitoring ketersediaan angkutan antar-provinsi dan kesiapan stok logistik regional.";
    } else if (pLow.includes('maluku') || pLow.includes('ntt') || pLow.includes('ntb')) {
      geoMod = "Wilayah kepulauan membutuhkan pemantauan jadwal tol laut dan distribusi antar-pulau.";
    } else {
      geoMod = "Pastikan koordinasi rantai pasok dengan wilayah surplus terdekat.";
    }
    
    return `${priceStr}\n\n${actionStr}\n\nKonteks Wilayah (${p}):\n${geoMod}`;
  };

console.log("=== BUKTI PERBEDAAN ACEH, JAMBI, PAPUA BARAT ===");

console.log("\\n[1] ACEH (Minyak Goreng, High Risk):");
console.log(getSmartReasoning("Minyak Goreng Curah", "Aceh", 12.5, "High Risk Alert", 18000));

console.log("\\n[2] JAMBI (Minyak Goreng, High Risk):");
console.log(getSmartReasoning("Minyak Goreng Curah", "Jambi", 12.5, "High Risk Alert", 18000));

console.log("\\n[3] PAPUA BARAT (Minyak Goreng, High Risk):");
console.log(getSmartReasoning("Minyak Goreng Curah", "Papua Barat", 12.5, "High Risk Alert", 18000));
