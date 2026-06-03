# PANGAN-AI — Smart Food Price & Supply Chain Intelligence

**PANGAN-AI** adalah platform berbasis Artificial Intelligence untuk monitoring, prediksi, insight, dan rekomendasi peluang distribusi harga pangan strategis di Indonesia.

Aplikasi ini dirancang untuk membantu pemangku kebijakan, analis pangan, dan pemerintah daerah membaca risiko kenaikan harga pangan lebih cepat melalui dashboard interaktif, model prediksi harga, early warning system, AI market insight, dan analisis ketimpangan harga antarwilayah.

🌐 **Live Demo:** https://panganai.vercel.app/
📦 **Backend API:** Azure App Service
☁️ **Cloud Storage:** Azure Blob Storage
🤖 **AI Insight:** Azure OpenAI
📊 **Prediction Engine:** CatBoost

---

## Latar Belakang

Harga pangan strategis seperti beras, cabai, minyak goreng, telur, bawang, dan daging ayam memiliki pengaruh langsung terhadap daya beli masyarakat. Ketika harga pangan naik, dampaknya tidak hanya terlihat pada statistik inflasi, tetapi juga langsung dirasakan oleh rumah tangga dan pelaku ekonomi kecil.

Saat ini, data harga pangan sudah tersedia melalui sumber seperti PIHPS Bank Indonesia. Namun, data tersebut masih perlu diolah agar dapat menjadi alat bantu pengambilan keputusan. Monitoring harga saja belum cukup. Pemangku kebijakan membutuhkan sistem yang mampu:

* membaca tren harga,
* memprediksi potensi kenaikan,
* memberikan peringatan dini,
* menjelaskan risiko dengan bahasa yang mudah dipahami,
* dan menunjukkan peluang distribusi antarwilayah.

PANGAN-AI hadir untuk menjawab kebutuhan tersebut.

---

## Tujuan Project

PANGAN-AI bertujuan untuk membantu proses pengambilan keputusan dalam stabilisasi harga pangan melalui pendekatan berbasis data dan AI.

Tujuan utama sistem ini adalah:

1. Memantau harga pangan strategis secara visual dan terpusat.
2. Memprediksi potensi pergerakan harga berdasarkan data historis.
3. Mengidentifikasi wilayah dengan tekanan harga tinggi.
4. Memberikan insight risiko menggunakan Azure OpenAI.
5. Menampilkan peluang distribusi dari wilayah dengan harga relatif rendah ke wilayah dengan harga lebih tinggi.
6. Membantu pemangku kebijakan bergerak dari respons reaktif menjadi antisipatif.

---

## Fitur Utama

### 1. National Food Command Dashboard

Dashboard utama menampilkan ringkasan kondisi harga pangan strategis secara visual. Pengguna dapat melihat gambaran umum harga nasional, daftar komoditas, indikator tren, dan kondisi wilayah yang perlu diperhatikan.

### 2. AI Price Forecasting

Fitur prediksi harga menggunakan model CatBoost untuk memproyeksikan harga pangan berdasarkan data historis dan fitur yang telah diproses.

Dengan fitur ini, pengguna dapat melihat apakah suatu komoditas cenderung naik, turun, atau stabil dalam periode tertentu.

### 3. Early Warning System

Sistem memberikan peringatan ketika terdapat komoditas atau wilayah yang menunjukkan pola kenaikan harga signifikan. Fitur ini membantu pengguna memprioritaskan komoditas dan provinsi yang perlu dipantau lebih lanjut.

### 4. Regional Price Imbalance Analysis

Fitur ini menganalisis ketimpangan harga antarwilayah untuk membantu pengguna memahami provinsi mana yang mengalami tekanan harga tinggi dan provinsi mana yang memiliki harga relatif lebih rendah.

### 5. Smart Distribution Opportunity

Sistem membandingkan harga antarprovinsi untuk menampilkan peluang distribusi pangan. Wilayah dengan harga relatif rendah dapat dipertimbangkan sebagai kandidat sumber pasokan untuk wilayah dengan harga lebih tinggi.

### 6. AI Market Insight

PANGAN-AI menggunakan Azure OpenAI untuk menghasilkan insight berbasis bahasa alami dalam Bahasa Indonesia.

Insight yang dihasilkan mencakup:

* ringkasan kondisi harga,
* analisis risiko,
* dan rekomendasi tindakan awal.

Fitur ini membantu pengguna non-teknis memahami hasil prediksi tanpa harus menafsirkan angka dan grafik secara manual.

### 7. Commodity Drilldown

Pengguna dapat memilih komoditas dan provinsi tertentu untuk melihat harga historis, prediksi, tren, dan kondisi wilayah secara lebih detail.

---

## Komoditas yang Dipantau

Beberapa komoditas pangan strategis yang dipantau antara lain:

* Beras
* Minyak goreng
* Cabai merah
* Cabai rawit
* Bawang merah
* Bawang putih
* Telur ayam
* Daging ayam
* Daging sapi
* Komoditas pangan lain yang tersedia pada dataset

---

## Arsitektur Sistem

Secara umum, PANGAN-AI terdiri dari tiga lapisan utama:

```text
Frontend Web Dashboard
        │
        ▼
Backend API - FastAPI
        │
        ├── Data Processing
        ├── CatBoost Prediction Engine
        ├── Early Warning System
        ├── Azure OpenAI Insight Service
        └── Azure Blob Storage Integration
```

Frontend digunakan untuk menampilkan dashboard dan visualisasi data. Backend digunakan untuk mengelola API, prediksi, alert, insight, dan integrasi cloud. Azure digunakan untuk deployment backend, penyimpanan artefak model/dataset, dan AI insight.

---

## Tech Stack

### Frontend

* React
* Vite
* Tailwind CSS
* Recharts
* JavaScript

### Backend

* FastAPI
* Python
* Pandas
* Uvicorn
* CatBoost
* PyArrow
* Python Dotenv

### Cloud & AI

* Azure App Service
* Azure Blob Storage
* Azure OpenAI
* Vercel

### Data & Model

* PIHPS-based food price dataset
* Parquet dataset
* CatBoost model artifact
* Local cache fallback for development

---

## Integrasi Microsoft Azure

PANGAN-AI telah menggunakan beberapa layanan Microsoft Azure untuk mendukung deployment, penyimpanan artefak AI, dan insight berbasis AI.

### Azure App Service

Backend PANGAN-AI dideploy menggunakan Azure App Service. Backend ini menjalankan FastAPI dan menyediakan endpoint untuk harga historis, prediksi, alert, statistik, insight AI, dan health check.

### Azure Blob Storage

Azure Blob Storage digunakan untuk menyimpan dan mengambil artefak penting seperti:

* model CatBoost,
* dataset input inference,
* data harga historis dalam format Parquet.

Dengan Azure Blob Storage, backend dapat mengambil model dan dataset dari cloud ketika aplikasi berjalan di environment deployment.

### Azure OpenAI

Azure OpenAI digunakan untuk menghasilkan AI Market Insight. Sistem dapat memberikan ringkasan, analisis risiko, dan rekomendasi tindakan berdasarkan hasil prediksi harga pangan.

### Runtime Health Check

Backend menyediakan endpoint health check untuk memastikan sistem siap digunakan. Health check memeriksa kesiapan storage, dataset, model, fitur, dan prediction engine.

---

## Environment Variables

### Backend Local Development

Untuk development lokal, gunakan konfigurasi `.env` pada folder `backend`.

Contoh konfigurasi:

```env
USE_AZURE_BLOB=false
LOCAL_MODEL_PATH=.cache/catboost_h01_h30_full_factor.cbm
LOCAL_INFERENCE_INPUT_PATH=.cache/model_input_2026-05-20_h01_h30.parquet
LOCAL_HISTORICAL_PRICE_PARQUET_PATH=.cache/harga_historis_2026-01-01_2026-05-20.parquet
LOCAL_HISTORICAL_CSV_FALLBACK_PATH=data/harga_historis_2026-01-01_2026-05-20.csv
CACHE_TTL_SECONDS=300
ALERT_MIN_CHANGE_PCT=5
CORS_ALLOWED_ORIGINS=http://localhost:5173
```

### Backend Azure Deployment

Pada Azure App Service, gunakan Application Settings seperti berikut:

```env
USE_AZURE_BLOB=true
AZURE_STORAGE_CONNECTION_STRING=
AZURE_BLOB_CONTAINER=paganai-artifacts
AZURE_MODEL_BLOB=models/catboost_h01_h30_full_factor.cbm
AZURE_INFERENCE_INPUT_BLOB=datasets/model_input_2026-05-20_h01_h30.parquet
AZURE_HISTORICAL_PRICE_PARQUET_BLOB=datasets/harga_historis_2026-01-01_2026-05-20.parquet
CORS_ALLOWED_ORIGINS=https://panganai.vercel.app
AZURE_OPENAI_ENDPOINT=
AZURE_OPENAI_API_KEY=
AZURE_OPENAI_MODEL=gpt-4.1-mini
```

> Catatan: jangan commit secret asli seperti API key, connection string, atau credential Azure ke repository.

### Frontend

Untuk frontend, gunakan file `.env` pada folder `frontend`.

Local development:

```env
VITE_API_URL=http://localhost:8000
```

Production:

```env
VITE_API_URL=https://<azure-app-service-url>
```

---

## Cara Menjalankan Project Secara Lokal

### 1. Clone repository

```bash
git clone https://github.com/elrenoel/panganai.git
cd panganai
```

### 2. Jalankan backend

```bash
cd backend
python -m pip install -r requirements.txt
python -m uvicorn main:app --reload --port 8000
```

Backend akan berjalan di:

```text
http://localhost:8000
```

### 3. Jalankan frontend

Buka terminal baru:

```bash
cd frontend
npm install
npm run dev
```

Frontend akan berjalan di:

```text
http://localhost:5173
```

---

## Cara Menggunakan Aplikasi

### 1. Buka aplikasi

Akses aplikasi melalui:

```text
https://panganai.vercel.app/
```

Untuk kebutuhan demo, autentikasi belum diaktifkan sehingga pengguna dapat langsung mengakses dashboard.

### 2. Lihat dashboard utama

Dashboard menampilkan ringkasan kondisi harga pangan, indikator utama, grafik, dan informasi komoditas yang dipantau.

### 3. Pilih komoditas dan provinsi

Pengguna dapat memilih komoditas dan provinsi untuk melihat kondisi harga yang lebih spesifik.

### 4. Lihat prediksi harga

Sistem menampilkan proyeksi harga untuk membantu pengguna memahami apakah harga suatu komoditas berpotensi naik, turun, atau stabil.

### 5. Baca AI Market Insight

Sistem menampilkan ringkasan, risiko, dan rekomendasi berbasis Azure OpenAI agar hasil prediksi lebih mudah dipahami.

### 6. Periksa alert

Jika terdapat pola kenaikan harga yang berisiko, sistem akan menampilkan alert agar pengguna dapat memprioritaskan wilayah atau komoditas tersebut.

### 7. Lihat peluang distribusi

Sistem membandingkan harga antarwilayah dan menampilkan peluang distribusi dari daerah dengan harga relatif rendah ke daerah dengan harga lebih tinggi.

---

## API Endpoints

| Endpoint                                             | Deskripsi                                                                 |
| ---------------------------------------------------- | ------------------------------------------------------------------------- |
| `GET /`                                              | Root API status                                                           |
| `GET /api/health`                                    | Mengecek kesiapan storage, dataset, model, feature, dan prediction engine |
| `GET /api/model-info`                                | Informasi model, jumlah fitur, dataset, provinsi, dan komoditas           |
| `GET /api/komoditas`                                 | Menampilkan daftar komoditas tersedia                                     |
| `GET /api/provinsi`                                  | Menampilkan daftar provinsi tersedia                                      |
| `GET /api/harga-historis?komoditas=...&provinsi=...` | Menampilkan data harga historis                                           |
| `GET /api/prediksi?komoditas=...&provinsi=...`       | Menampilkan ringkasan prediksi harga                                      |
| `GET /api/prediksi-semua?komoditas=...`              | Menampilkan prediksi untuk semua provinsi                                 |
| `GET /api/alert`                                     | Menampilkan alert kenaikan harga                                          |
| `GET /api/statistik-nasional`                        | Menampilkan statistik harga nasional                                      |

---

## Health Check

Setelah backend dideploy, health check dapat dilakukan melalui:

```bash
curl https://<azure-app-service-url>/api/health
```

Contoh response ketika sistem siap:

```json
{
  "status": "ok",
  "ready": true,
  "storage_ready": true,
  "storage_error": null,
  "dataset_loaded": true,
  "model_loaded": true,
  "feature_loaded": true,
  "prediction_engine": "catboost"
}
```

Jika status menunjukkan `degraded`, periksa konfigurasi storage, dataset, model artifact, atau environment variables pada backend.

---

## Struktur Folder

```text
panganai/
├── backend/
│   ├── app/
│   │   ├── api/
│   │   ├── core/
│   │   ├── services/
│   │   └── utils/
│   ├── data/
│   ├── .cache/
│   ├── main.py
│   ├── requirements.txt
│   ├── .env.example
│   └── .env.azure.example
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   ├── pages/
│   │   ├── api/
│   │   └── App.jsx
│   ├── package.json
│   └── vite.config.js
│
├── pangan_pipeline/
│   └── data/
│
├── DEPLOYMENT.md
└── README.md
```

---

## Deployment

Detail deployment dapat dilihat pada file:

```text
DEPLOYMENT.md
```

Ringkasan deployment:

1. Backend dideploy ke Azure App Service.
2. Artifact model dan dataset disimpan di Azure Blob Storage.
3. Frontend dideploy ke Vercel.
4. Frontend diarahkan ke backend Azure melalui `VITE_API_URL`.
5. Health check digunakan untuk memastikan backend, storage, dataset, dan model siap digunakan.

---

## Dampak yang Diharapkan

PANGAN-AI diharapkan dapat membantu:

* mempercepat deteksi risiko kenaikan harga pangan,
* mendukung pengambilan keputusan berbasis data,
* mempermudah analisis ketimpangan harga antarwilayah,
* memberikan rekomendasi awal peluang distribusi pangan,
* membantu stabilisasi harga pangan strategis,
* dan meningkatkan keterjangkauan pangan bagi masyarakat.

---

## Roadmap Pengembangan

Beberapa pengembangan berikutnya yang dapat dilakukan:

* Integrasi data cuaca dan bencana untuk memperkuat prediksi.
* Integrasi data stok dan produksi pangan daerah.
* Azure SQL Database untuk penyimpanan data historis dan hasil prediksi.
* Azure Functions untuk pipeline data terjadwal.
* Azure Machine Learning untuk eksperimen dan deployment model.
* Azure Key Vault untuk pengelolaan secret.
* Microsoft Entra ID untuk autentikasi dan role-based access control.
* Mobile reporting untuk petugas lapangan.
* Kalkulator biaya logistik dan estimasi rute distribusi.

---

## Link Penting

* Live App: https://panganai.vercel.app/
* Repository: https://github.com/elrenoel/panganai
* Deployment Guide: `DEPLOYMENT.md`
* Video Demo: https://youtu.be/NqsgjIOlnHU

---

## License

Project ini dikembangkan untuk kebutuhan hackathon Microsoft Elevate Training Center.
