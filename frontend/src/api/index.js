const BASE = import.meta.env.VITE_API_URL || "/api";
const responseCache = new Map();

function getCached(key, ttlMs) {
  const item = responseCache.get(key);
  if (!item) return null;
  if (Date.now() - item.ts > ttlMs) {
    responseCache.delete(key);
    return null;
  }
  return item.value;
}

function setCached(key, value) {
  responseCache.set(key, { ts: Date.now(), value });
  return value;
}

function normalizeParam(value) {
  if (value == null) return "";
  if (typeof value === "string") return value;
  if (typeof value === "object") {
    return value.slug || value.nama || "";
  }
  return String(value);
}

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
  const params = new URLSearchParams({
    komoditas: normalizeParam(komoditas),
    provinsi: normalizeParam(provinsi),
  });
  const res = await fetch(`${BASE}/harga-historis?${params}`);
  if (!res.ok) throw new Error("Gagal memuat data harga historis");
  return res.json();
}

export async function fetchPrediksi(komoditas, provinsi) {
  const params = new URLSearchParams({
    komoditas: normalizeParam(komoditas),
    provinsi: normalizeParam(provinsi),
  });
  const res = await fetch(`${BASE}/prediksi?${params}`);
  if (!res.ok) throw new Error("Gagal memuat data prediksi");
  return res.json();
}

export async function fetchPrediksiSemua(komoditas) {
  const params = new URLSearchParams({ komoditas: normalizeParam(komoditas) });
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

export async function fetchDashboardInitial(signal) {
  const cacheKey = "dashboard-initial";
  const cached = getCached(cacheKey, 5 * 60 * 1000);
  if (cached) return cached;

  const res = await fetch(`${BASE}/dashboard/initial`, { signal });
  if (!res.ok) throw new Error("Gagal memuat data initial dashboard");
  const data = await res.json();
  return setCached(cacheKey, data);
}

export async function fetchDashboardDetail(komoditas, provinsi, signal) {
  const k = normalizeParam(komoditas);
  const p = normalizeParam(provinsi);
  const cacheKey = `dashboard-detail::${k}::${p}`;
  const cached = getCached(cacheKey, 2 * 60 * 1000);
  if (cached) return cached;

  const params = new URLSearchParams({
    komoditas: k,
    provinsi: p,
  });
  const res = await fetch(`${BASE}/dashboard/detail?${params}`, { signal });
  if (!res.ok) throw new Error("Gagal memuat detail dashboard");
  const data = await res.json();
  return setCached(cacheKey, data);
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
