PANGAN AI BACKEND - DOKUMENTASI LENGKAP (RINGKASAN KERJA END-TO-END)
===================================================================

Dokumen ini merangkum semua perubahan yang sudah dikerjakan dari awal sampai akhir refactor backend FastAPI Pangan AI, termasuk fungsi setiap file penting di folder backend.

Tanggal pembaruan dokumentasi: 2026-05-29


1) TUJUAN BESAR REFACTOR
------------------------
Sebelumnya seluruh logic backend menumpuk di satu file, sehingga sulit dirawat dan sulit dikembangkan untuk live inference model.

Tujuan yang dicapai:
- Memecah backend menjadi struktur modular (api, services, repositories, core, utils, schemas).
- Menjaga endpoint lama tetap kompatibel dengan frontend React lama.
- Menambahkan live inference CatBoost (H+7) + recursive forecast prototype untuk horizon 30 hari.
- Menambahkan startup lifecycle (lifespan) yang jelas tanpa global variable.
- Menambahkan health/model observability endpoint.
- Menambahkan validasi startup, error handling, dan logging dasar.


2) RINGKASAN PEKERJAAN PER PHASE
--------------------------------

PHASE 1 - REFACTOR TANPA UBAH BEHAVIOR
- Konfigurasi path dipusatkan ke app/core/config.py (class Settings).
- Helper converter dipindah ke app/utils/converters.py.
- Repository dibuat untuk fokus baca file saja.
- Service dibuat untuk logic bisnis lama (komoditas, historis, prediksi csv, alert, statistik).
- Router dipecah per domain endpoint.
- Endpoint lama tetap berjalan:
  /api/komoditas
  /api/provinsi
  /api/harga-historis
  /api/prediksi
  /api/prediksi-semua
  /api/alert
  /api/statistik-nasional

PHASE 2 - APP STARTUP / LIFESPAN
- Menambahkan app/core/lifespan.py.
- Semua data/model penting dimuat di startup dan disimpan di app.state.
- app/main.py dipertahankan tipis: app init, CORS, include router, lifespan.

PHASE 3 - INTEGRASI CATBOOST LIVE INFERENCE
- Dibuat ModelService:
  load_model, load_feature_columns, predict.
- Dibuat FeatureService:
  get_latest_row, validate_required_features, build_prediction_matrix.
- Dibuat LivePredictionService:
  predict_h7 (native model target H+7),
  predict_recursive_30 (prototype recursive H+7 -> H+14/H+21/H+28).
- Ditambahkan aturan error:
  data tidak ditemukan -> 404,
  feature mismatch -> 500.

PHASE 4 - ENDPOINT BARU
- Menambah endpoint GET /api/prediksi-live.
- Rule horizon:
  <=7 pakai predict_h7,
  >7 dan <=30 pakai predict_recursive_30,
  >30 return 400.
- Menyediakan mode live_catboost di response.

PHASE 5 - UTILITY ENDPOINT
- Menambah/menyempurnakan:
  GET /api/health
  GET /api/model-info
- /api/model-info menampilkan status model, feature_count, range tanggal dataset, dll.

PHASE 6 - VALIDASI DAN ERROR HANDLING
- Startup fail-fast jika file wajib hilang (CSV, JSON, model, feature columns).
- Logging startup ditambahkan:
  path data/model,
  jumlah row dataset,
  min_date/max_date,
  jumlah feature model,
  status model loaded.
- NaN handling inference:
  numeric -> median dataset (fallback 0),
  categorical -> "unknown".

PHASE 7 - ACCEPTANCE CRITERIA
- Semua endpoint lama tervalidasi tetap hidup.
- main.py tetap ringkas dan tanpa bisnis logic.
- Tidak ada global variable data.
- Model loaded sekali saat startup.
- /api/health dan /api/model-info valid.
- /api/prediksi-live horizon 7 dan 30 valid.
- Tidak ada scraping/live fetch saat request.
- Frontend lama tetap tidak perlu diubah.

Tambahan setelah phase:
- /api/prediksi-live kini juga mengembalikan prediksi harian dalam rentang 7 hari
  (interpolasi dari harga terakhir ke titik H+7).
- Untuk horizon 30, disediakan prediksi harian 28 hari (4 blok 7-harian).


3) ARSITEKTUR FINAL BACKEND (SINGKAT)
-------------------------------------
Request masuk -> Router (app/api) -> Service (app/services) -> Repository (app/repositories, jika baca snapshot)

Untuk live model:
Router -> live_prediction_service -> feature_service + model_service -> output response.

Semua dependency berat dimuat di startup lewat lifespan ke app.state.


4) PENJELASAN FILE PER FOLDER
-----------------------------

A. ROOT BACKEND

1. backend/main.py
- Compatibility entrypoint.
- Menjaga pola import lama/deployment lama tetap hidup.
- Menyediakan object app dari app.main.

2. backend/app.py
- Entrypoint alternatif yang isinya sama tujuan dengan backend/main.py.
- Menjembatani import path ke app.main.

3. backend/requirements.txt
- Daftar dependency runtime backend (FastAPI, pandas, catboost, dll).

4. backend/vercel.json
- Routing deployment Vercel untuk mengarahkan request ke backend.

5. backend/postman_panganai_collection.json
- Koleksi Postman siap import untuk smoke test endpoint utama, live endpoint,
  dan negative case.

6. backend/README.txt
- Dokumen ini.

7. backend/__pycache__/*
- File cache bytecode Python otomatis.
- Bukan logic aplikasi.


B. APP LAYER (backend/app)

1. backend/app/main.py
- App bootstrap utama:
  - init FastAPI
  - pasang lifespan
  - pasang CORS
  - include semua router
- Tidak berisi bisnis logic.

2. backend/app/__init__.py
- Penanda package Python.

3. backend/app/__pycache__/*
- Cache bytecode Python.


C. CORE (backend/app/core)

1. backend/app/core/config.py
- Menyediakan class Settings.
- Pusat semua path penting:
  ROOT_DIR, DATA_DIR, PREDICTIONS_CSV_DIR, PREDICTIONS_JSON_DIR,
  DATASET_DIR, MODEL_DIR, CATBOOST_MODEL_PATH, FEATURE_COLUMNS_PATH.

2. backend/app/core/lifespan.py
- Lifecycle startup app.
- Tugas:
  - validasi file wajib ada (fail-fast)
  - load df_hasil, df_harian, df_semua, alerts
  - load model CatBoost + feature columns
  - load dataset fitur untuk inference
  - hitung median numeric feature untuk imputasi NaN
  - simpan semua ke app.state
  - tulis logging startup

3. backend/app/core/__init__.py
- Penanda package.


D. API ROUTERS (backend/app/api)

1. backend/app/api/health.py
- GET /
  status welcome message.
- GET /api/health
  status runtime backend + status data/model loaded.
- GET /api/model-info
  metadata model/dataset (feature_count, rows, min/max date, dst).

2. backend/app/api/commodity.py
- GET /api/komoditas
- GET /api/provinsi
- Mengambil list dari dataset bersih melalui service.

3. backend/app/api/historical.py
- GET /api/harga-historis
- Mengembalikan data historis harga per komoditas/provinsi.

4. backend/app/api/prediction.py
- GET /api/prediksi
  endpoint lama berbasis snapshot CSV.
- GET /api/prediksi-semua
  endpoint lama agregasi semua provinsi per komoditas.
- GET /api/prediksi-live
  endpoint baru live model CatBoost (horizon rule 7/30/>30).

5. backend/app/api/alert.py
- GET /api/alert
- Return alert yang diurutkan berdasarkan kenaikan_pct.

6. backend/app/api/statistics.py
- GET /api/statistik-nasional
- Statistik nasional dari snapshot + sinyal trend.

7. backend/app/api/__init__.py
- Penanda package.

8. backend/app/api/__pycache__/*
- Cache bytecode Python.


E. REPOSITORIES (backend/app/repositories)

1. backend/app/repositories/dataset_repository.py
- load_main_dataset()
- Hanya baca file dataset bersih utama.

2. backend/app/repositories/prediction_repository.py
- load_prediction_summary()
- load_daily_prediction()
- Hanya baca file snapshot prediksi CSV.

3. backend/app/repositories/alert_repository.py
- load_alerts()
- Hanya baca file alert JSON.

4. backend/app/repositories/__init__.py
- Penanda package.

5. backend/app/repositories/__pycache__/*
- Cache bytecode Python.


F. SERVICES (backend/app/services)

1. backend/app/services/dataset_service.py
- Logic domain dataset:
  - get_komoditas
  - get_provinsi
  - get_harga_historis

2. backend/app/services/prediction_csv_service.py
- Logic endpoint lama berbasis snapshot:
  - get_prediction_summary
  - get_daily_forecast
  - get_all_province_predictions

3. backend/app/services/alert_service.py
- get_sorted_alerts

4. backend/app/services/statistics_service.py
- get_national_statistics

5. backend/app/services/model_service.py
- Class ModelService:
  - load_model(path)
  - load_feature_columns(path)
  - predict(model, X, numeric_fill_values)
- Menangani imputasi NaN numeric/categorical sebelum predict.

6. backend/app/services/feature_service.py
- load_feature_dataset
- get_latest_row (dengan optional jenis_harga/level_harga)
- validate_required_features
- build_prediction_matrix
- Validasi feature mismatch dan not found.

7. backend/app/services/live_prediction_service.py
- predict_h7:
  prediksi titik H+7 + prediksi_harian 7 hari.
- predict_recursive_30:
  recursive prototype 4 step (H+7/14/21/28) + prediksi_harian 28 hari.
- Catatan penting: ini bukan native H+30 model, melainkan prototype recursive.

8. backend/app/services/prediction_service.py
- File helper lama yang pernah dipakai saat transisi refactor.
- Saat ini arsitektur aktif utama memakai prediction_csv_service dan live_prediction_service.

9. backend/app/services/__init__.py
- Penanda package.

10. backend/app/services/__pycache__/*
- Cache bytecode Python.


G. UTILS (backend/app/utils)

1. backend/app/utils/converters.py
- Helper konversi:
  - safe_float
  - safe_int
  - format_date

2. backend/app/utils/__init__.py
- Penanda package.

3. backend/app/utils/__pycache__/*
- Cache bytecode Python.


H. SCHEMAS (backend/app/schemas)

1. backend/app/schemas/health.py
2. backend/app/schemas/commodity.py
3. backend/app/schemas/historical.py
4. backend/app/schemas/prediction.py
5. backend/app/schemas/__init__.py

Status:
- File schema disiapkan sebagai struktur typing/response model.
- Beberapa endpoint saat ini masih return dict/list langsung (tanpa response_model ketat).


I. MODEL ARTIFACTS (backend/models)

1. backend/models/trained_catboost_model.cbm
- Model CatBoost terlatih untuk target harga_target_h7.

2. backend/models/feature_columns.pkl
- Daftar urutan kolom feature model (47 feature).
- Urutan ini wajib konsisten saat membangun matrix prediksi.


J. DATASET & SNAPSHOT (backend/data)

1. backend/data/dataset/final_training_dataset_feature_engineered.csv
- Dataset feature engineering untuk training/inference support.

2. backend/data/dataset/clean_dataset/semua_komoditas.csv
- Dataset historis bersih untuk endpoint lama.

3. backend/data/predictions/csv/hasil_prediksi.csv
- Snapshot ringkasan prediksi lama.

4. backend/data/predictions/csv/prediksi_harian.csv
- Snapshot prediksi harian lama.

5. backend/data/predictions/json/alert_prediksi.json
- Snapshot alert prediksi.

6. backend/data/dataset/*.xlsx
- Sumber data mentah komoditas tertentu.

7. backend/data/dataset/clean_dataset/*_clean.csv dan *_ringkasan.json
- Artefak pembersihan per komoditas.

8. backend/data/predictions/chart/*.png
- Gambar/chart prediksi historis/simulasi.


5) DAFTAR ENDPOINT AKTIF
------------------------

A. Endpoint kompatibilitas lama
- GET /api/komoditas
- GET /api/provinsi
- GET /api/harga-historis
- GET /api/prediksi
- GET /api/prediksi-semua
- GET /api/alert
- GET /api/statistik-nasional

B. Endpoint utilitas
- GET /
- GET /api/health
- GET /api/model-info

C. Endpoint live model
- GET /api/prediksi-live
  Query:
  - provinsi (required)
  - komoditas (required)
  - horizon (default 7)
  - jenis_harga (optional)
  - level_harga (optional)

Rule horizon:
- horizon <= 7 -> prediksi H+7
- 7 < horizon <= 30 -> recursive prototype
- horizon > 30 -> HTTP 400


6) CATATAN IMPLEMENTASI PENTING
-------------------------------
- Model asli adalah model target H+7.
- Horizon 30 bukan native model 30 hari.
- Horizon 30 menggunakan recursive forecast prototype.
- Prediksi harian dalam rentang mingguan disediakan dengan interpolasi (bukan model harian native).
- Tidak ada live scraping / external API fetch saat request.
- Seluruh state runtime disimpan di app.state (tanpa global variable).


7) CARA TEST CEPAT
------------------
- Jalankan backend lokal, lalu import file:
  backend/postman_panganai_collection.json
- Uji request utama:
  /api/health
  /api/model-info
  /api/prediksi-live?horizon=7
  /api/prediksi-live?horizon=30
- Uji negative case:
  /api/prediksi-live?horizon=31 (harus 400)
  provinsi/komoditas invalid (harus 404)


8) STATUS AKHIR
---------------
Refactor backend selesai sesuai target:
- Modular, maintainable, dan siap dikembangkan lanjut.
- Backward compatible untuk frontend lama.
- Live CatBoost inference aktif dengan guardrail validasi yang jelas.
