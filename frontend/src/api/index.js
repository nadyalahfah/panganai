const BASE = import.meta.env.VITE_API_URL || "/api";

export async function fetchKomoditas() {
  const res = await fetch(`${BASE}/komoditas`);
  if (!res.ok) throw new Error("Gagal memuat daftar komoditas");
  return res.json();
}

export async function fetchProvinsi() {
  const res = await fetch(`${BASE}/provinsi`);
  if (!res.ok) throw new Error("Gagal memuat daftar provinsi");
  return res.json();
}

export async function fetchHargaHistoris(komoditas, provinsi) {
  const params = new URLSearchParams({ komoditas, provinsi });
  const res = await fetch(`${BASE}/harga-historis?${params}`);
  if (!res.ok) throw new Error("Gagal memuat data harga historis");
  return res.json();
}

export async function fetchPrediksi(komoditas, provinsi) {
  const params = new URLSearchParams({ komoditas, provinsi });
  const res = await fetch(`${BASE}/prediksi?${params}`);
  if (!res.ok) throw new Error("Gagal memuat data prediksi");
  return res.json();
}

export async function fetchPrediksiSemua(komoditas) {
  const params = new URLSearchParams({ komoditas });
  const res = await fetch(`${BASE}/prediksi-semua?${params}`);
  if (!res.ok) throw new Error("Gagal memuat prediksi semua provinsi");
  return res.json();
}

export async function fetchAlert() {
  const res = await fetch(`${BASE}/alert`);
  if (!res.ok) throw new Error("Gagal memuat data alert");
  return res.json();
}

export async function fetchStatistikNasional() {
  const res = await fetch(`${BASE}/statistik-nasional`);
  if (!res.ok) throw new Error("Gagal memuat statistik nasional");
  return res.json();
}

// ── Helpers ──────────────────────────────────────────────────
export function formatRupiah(num) {
  if (num == null) return "-";
  return "Rp " + Math.round(num).toLocaleString("id-ID");
}

export function formatRupiahShort(num) {
  if (num == null) return "-";
  if (num >= 1000) {
    return "Rp" + Math.round(num / 1000) + "rb";
  }
  return "Rp" + Math.round(num);
}

export function formatPct(val) {
  if (val == null) return "-";
  const sign = val > 0 ? "+" : "";
  return `${sign}${val.toFixed(1)}%`;
}

export function getKomoditasColor(komoditas) {
  if (!komoditas) return "#6c757d";
  const lower = komoditas.toLowerCase();
  if (lower.includes("beras")) return "#378ADD";
  if (lower.includes("minyak")) return "#E29A27";
  if (lower.includes("cabai")) return "#E24B4A";
  return "#6c757d";
}

export function getKomoditasClass(komoditas) {
  if (!komoditas) return "";
  const lower = komoditas.toLowerCase();
  if (lower.includes("beras")) return "beras";
  if (lower.includes("minyak")) return "minyak";
  if (lower.includes("cabai")) return "cabai";
  return "";
}

export function getTrenClass(tren) {
  if (!tren) return "stabil";
  return tren.toLowerCase();
}

export function formatTanggalShort(dateStr) {
  const d = new Date(dateStr);
  const months = [
    "Jan",
    "Feb",
    "Mar",
    "Apr",
    "Mei",
    "Jun",
    "Jul",
    "Agt",
    "Sep",
    "Okt",
    "Nov",
    "Des",
  ];
  return `${d.getDate()} ${months[d.getMonth()]}`;
}
