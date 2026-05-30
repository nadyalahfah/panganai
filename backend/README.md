# Pangan AI Backend API Guide

Dokumen ini adalah checklist endpoint API yang perlu dites beserta query params/body dan expected response minimal.

## Dataset yang Dipakai

Backend saat ini menggunakan **satu dataset utama**:

- `backend/data/dataset/final_training_dataset_feature_engineered.csv`

Fungsi dataset ini:
- sumber data historis API (`df_semua`)
- sumber data fitur untuk inferensi CatBoost (`feature_df`)

Catatan:
- File model disimpan di:
  - `backend/models/trained_catboost_model.cbm`
  - `backend/models/feature_columns.pkl`

## 1) Health & Info ?

1. `GET /`
- Query: tidak ada
- Body: tidak ada
- Expect:

```json
{
  "status": "success",
  "message": "API Pangan AI siap melayani permintaan data harga pangan Indonesia."
}
```

2. `GET /api/health`
- Query: tidak ada
- Body: tidak ada
- Expect (minimal):

```json
{
  "status": "ok",
  "data_loaded": true,
  "model_loaded": true,
  "data_source": "csv_snapshot"
}
```

3. `GET /api/model-info`
- Query: tidak ada
- Body: tidak ada
- Expect (minimal):

```json
{
  "model_loaded": true,
  "feature_count": 47,
  "prediction_engine": "catboost",
  "dataset_rows": 0,
  "min_date": "YYYY-MM-DD",
  "max_date": "YYYY-MM-DD",
  "available_provinsi_count": 0,
  "available_komoditas_count": 0
}
```

## 2) Master Data ?

1. `GET /api/komoditas`
- Query: tidak ada
- Body: tidak ada
- Expect:
- Array object komoditas (`id`, `nama`, `slug`), contoh:

```json
[
  {
    "id": 1,
    "nama": "Beras Kualitas Medium I",
    "slug": "beras-kualitas-medium-i"
  },
  {
    "id": 2,
    "nama": "Cabai Merah Keriting",
    "slug": "cabai-merah-keriting"
  }
]
```

2. `GET /api/provinsi`
- Query: tidak ada
- Body: tidak ada
- Expect:
- Array object provinsi (`id`, `nama`, `slug`), contoh:

```json
[
  {
    "id": 1,
    "nama": "Aceh",
    "slug": "aceh"
  },
  {
    "id": 2,
    "nama": "Bali",
    "slug": "bali"
  }
]
```

## 3) Historis ?

1. `GET /api/harga-historis`
- Query (required):
  - `komoditas` string (slug dari `/api/komoditas`)
  - `provinsi` string (slug dari `/api/provinsi`)
- Body: tidak ada
- Contoh:
  - `/api/harga-historis?komoditas=beras-kualitas-medium-i&provinsi=aceh`
- Expect:
- Array object:

```json
[
  {
    "tanggal": "YYYY-MM-DD",
    "harga": 0,
    "harga_nasional": 0,
    "status_pasokan": "NORMAL"
  }
]
```

## 4) Prediksi Utama (dipakai UI) ?

1. `GET /api/prediksi`
- Query (required):
  - `komoditas` string (slug)
  - `provinsi` string (slug)
- Body: tidak ada
- Contoh:
  - `/api/prediksi?komoditas=beras-kualitas-medium-i&provinsi=aceh`
- Expect:

```json
{
  "ringkasan": {
    "harga_sekarang": 0,
    "prediksi_7h": 0,
    "prediksi_30h": 0,
    "tren_7h": "NAIK|TURUN|STABIL",
    "tren_30h": "NAIK|TURUN|STABIL",
    "mape_pct": 0,
    "bawah_7h": 0,
    "atas_7h": 0,
    "bawah_30h": 0,
    "atas_30h": 0,
    "mae": 0,
    "engine": "catboost",
    "prototype_recursive_forecast": true
  },
  "harian": [
    {
      "tanggal": "YYYY-MM-DD",
      "prediksi": 0,
      "batas_bawah": 0,
      "batas_atas": 0
    }
  ]
}
```

Catatan:
- `harian` mode CatBoost sekarang 30 titik (day 1..30).

2. `GET /api/prediksi-semua`
- Query (required):
  - `komoditas` string (slug)
- Body: tidak ada
- Contoh:
  - `/api/prediksi-semua?komoditas=beras-kualitas-medium-i`
- Expect:

```json
[
  {
    "provinsi": "Aceh",
    "harga_sekarang": 0,
    "prediksi_7h": 0,
    "prediksi_30h": 0,
    "tren_7h": "NAIK|TURUN|STABIL",
    "tren_30h": "NAIK|TURUN|STABIL",
    "ubah_7_pct": 0,
    "ubah_30_pct": 0,
    "engine": "catboost"
  }
]
```

## 5) Alert & Statistik ?

1. `GET /api/alert`
- Query: tidak ada
- Body: tidak ada
- Expect:
- Array object, sorted desc by `kenaikan_pct`:

```json
[
  {
    "provinsi": "Aceh",
    "komoditas": "Beras Kualitas Medium I",
    "harga_sekarang": 0,
    "prediksi_7h": 0,
    "kenaikan_pct": 0,
    "risk_level": "HIGH|MEDIUM|LOW|UNKNOWN",
    "ai_reasoning": "string",
    "engine": "catboost"
  }
]
```

2. `GET /api/statistik-nasional`
- Query: tidak ada
- Body: tidak ada
- Expect:

```json
[
  {
    "komoditas": "Beras Kualitas Medium I",
    "harga_rata_nasional": 0,
    "tren_30h_mayoritas": "NAIK|TURUN|STABIL",
    "engine": "catboost"
  }
]
```

## 6) Endpoint Debug Live Model ?

1. `GET /api/prediksi-live`
- Query (required):
  - `provinsi` string (slug)
  - `komoditas` string (slug)
- Query (optional):
  - `horizon` int (default `7`, valid `<=30`)
  - `jenis_harga` string
  - `level_harga` string
- Body: tidak ada

### 6a) Horizon 7

- Contoh:
  - `/api/prediksi-live?provinsi=aceh&komoditas=beras-kualitas-medium-i&horizon=7`
- Expect:

```json
{
  "mode": "live_catboost",
  "provinsi": "Aceh",
  "komoditas": "Beras Kualitas Medium I",
  "last_data_date": "YYYY-MM-DD",
  "target_date": "YYYY-MM-DD",
  "horizon": 7,
  "prediksi_harga": 0,
  "prediksi_harian": [
    {
      "tanggal": "YYYY-MM-DD",
      "horizon": 1,
      "prediksi_harga": 0
    }
  ]
}
```

### 6b) Horizon 30

- Contoh:
  - `/api/prediksi-live?provinsi=aceh&komoditas=beras-kualitas-medium-i&horizon=30`
- Expect:

```json
{
  "mode": "live_catboost",
  "prototype_recursive_forecast": true,
  "provinsi": "Aceh",
  "komoditas": "Beras Kualitas Medium I",
  "last_data_date": "YYYY-MM-DD",
  "predictions": [
    {"tanggal":"YYYY-MM-DD","horizon":7,"prediksi_harga":0},
    {"tanggal":"YYYY-MM-DD","horizon":14,"prediksi_harga":0},
    {"tanggal":"YYYY-MM-DD","horizon":21,"prediksi_harga":0},
    {"tanggal":"YYYY-MM-DD","horizon":28,"prediksi_harga":0}
  ],
  "prediksi_harian": [
    {"tanggal":"YYYY-MM-DD","horizon":1,"prediksi_harga":0}
  ]
}
```

## 7) Negative Tests (Wajib) ?

1. `GET /api/prediksi-live?horizon=31...`
- Expect:
  - HTTP `400`
  - detail error max horizon.

2. `GET /api/prediksi-live` dengan `provinsi/komoditas` tidak valid
- Expect:
  - HTTP `404`

3. Jika engine runtime bukan `catboost`, panggil `/api/prediksi-live`
- Expect:
  - HTTP `400`
  - pesan endpoint hanya tersedia saat engine catboost aktif.

## 8) Endpoint Optimasi Fetch (Baru)

1. `GET /api/dashboard/initial`
- Query: tidak ada
- Body: tidak ada
- Fungsi:
  - Bootstrap data dashboard initial load dalam 1 request
  - Menggantikan call terpisah ke `/api/komoditas`, `/api/provinsi`, `/api/alert`, `/api/statistik-nasional`
- Expect:

```json
{
  "komoditas": [{"id": 1, "nama": "Beras Kualitas Medium I", "slug": "beras-kualitas-medium-i"}],
  "provinsi": [{"id": 1, "nama": "Aceh", "slug": "aceh"}],
  "alert": [],
  "statistik_nasional": [],
  "default_selection": {
    "provinsi": "aceh",
    "komoditas": "beras-kualitas-medium-i"
  },
  "metadata": {
    "data_source": "catboost",
    "last_updated": "YYYY-MM-DDTHH:mm:ssZ",
    "dataset_max_date": "YYYY-MM-DD"
  }
}
```

2. `GET /api/dashboard/detail`
- Query (required):
  - `komoditas` string (slug)
  - `provinsi` string (slug)
- Body: tidak ada
- Fungsi:
  - Detail dashboard per selection dalam 1 request
  - Menggabungkan data:
    - prediksi (`/api/prediksi` contract)
    - historis (`/api/harga-historis` contract)
    - prediksi semua provinsi (`/api/prediksi-semua` contract)
- Response:

```json
{
  "selection": {
    "komoditas": "beras-kualitas-medium-i",
    "provinsi": "aceh"
  },
  "historis": [],
  "prediksi": {
    "ringkasan": {},
    "harian": []
  },
  "prediksi_semua": [],
  "recommendation": null
}
```

3. `POST /api/harga-historis/batch`
- Query: tidak ada
- Body (required):

```json
{
  "items": [
    {"komoditas": "bawang-merah-ukuran-sedang", "provinsi": "aceh"},
    {"komoditas": "cabai-merah-keriting", "provinsi": "bali"}
  ],
  "limit_days": 90
}
```

- Fungsi:
  - Ambil historis banyak pasangan komoditas-provinsi dalam 1 request.
- Response:

```json
{
  "results": {
    "aceh::bawang-merah-ukuran-sedang": [],
    "bali::cabai-merah-keriting": []
  }
}
```

4. `POST /api/prediksi-batch`
- Query: tidak ada
- Body (required):

```json
[
  {"komoditas": "beras-kualitas-medium-i", "provinsi": "aceh"},
  {"komoditas": "cabai-merah-keriting", "provinsi": "bali"}
]
```

- Fungsi:
  - Ambil prediksi banyak pasangan komoditas-provinsi dalam 1 request.
