# MangoCheck 🥭

**Sistem Klasifikasi Tingkat Kematangan Mangga Berbasis Computer Vision**

MangoCheck adalah prototype backend API berbasis Python dan Flask yang menerima foto mangga dan mengklasifikasikannya ke tiga kategori menggunakan model TensorFlow Lite:

| Kelas    | Label   | Keterangan                          |
|----------|---------|-------------------------------------|
| `unripe` | Mentah  | Mangga belum siap dijual/dikonsumsi |
| `ripe`   | Matang  | Mangga siap dijual/dikonsumsi       |
| `rotten` | Busuk   | Mangga perlu dipisahkan dari stok   |

> **Catatan Penting:** MangoCheck adalah alat bantu keputusan awal, bukan penilaian kualitas pangan yang pasti. Hasil prediksi bergantung pada kualitas foto dan kemampuan model yang dilatih.

---

## Daftar Isi

- [Arsitektur Backend](#arsitektur-backend)
- [Struktur Folder](#struktur-folder)
- [Prasyarat](#prasyarat)
- [Instalasi](#instalasi)
- [Konfigurasi Environment Variable](#konfigurasi-environment-variable)
- [Menaruh File Model](#menaruh-file-model)
- [Menjalankan Server Lokal](#menjalankan-server-lokal)
- [Menjalankan Test](#menjalankan-test)
- [Penggunaan API](#penggunaan-api)
- [Format Respons](#format-respons)
- [Keamanan Upload File](#keamanan-upload-file)
- [Confidence Rendah](#confidence-rendah)
- [Deployment Vercel](#deployment-vercel)
- [Integrasi Frontend](#integrasi-frontend)
- [Lisensi Dataset](#lisensi-dataset)

---

## Arsitektur Backend

```
Pengguna
   ↓
Frontend HTML + CSS + JavaScript (Tahap 3)
   ↓ POST /api/predict  multipart/form-data
Backend Python + Flask
   ├── Validasi file (ukuran, format, integritas)
   ├── Preprocessing gambar (resize, RGB, normalisasi)
   ├── TensorFlow Lite inference
   ├── Rekomendasi berdasarkan kelas + confidence
   └── Respons JSON sesuai kontrak API
```

**Komponen utama:**

| Komponen           | Teknologi                    |
|--------------------|------------------------------|
| Bahasa             | Python 3.11                  |
| Framework API      | Flask 3.x                    |
| Inference model    | tflite-runtime               |
| Pengolahan gambar  | Pillow                       |
| Perhitungan array  | NumPy                        |
| Testing            | pytest                       |
| Hosting target     | Vercel                       |
| Hosting cadangan   | Render / Hugging Face Spaces |

---

## Struktur Folder

```
MangoCheck/
│
├── api/
│   └── index.py                  # Entry point Vercel (WSGI)
│
├── app/
│   ├── __init__.py               # Flask app factory, CORS, error handler
│   ├── config.py                 # Konfigurasi terpusat dari env variable
│   │
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py             # GET /api/health
│   │   └── predict.py            # POST /api/predict
│   │
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_service.py      # Validasi & preprocessing gambar
│   │   ├── model_service.py      # Muat & jalankan TFLite inference
│   │   └── recommendation_service.py  # Rekomendasi berdasarkan prediksi
│   │
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── response_schema.py    # Builder JSON respons API
│   │
│   └── utils/
│       ├── __init__.py
│       └── errors.py             # Kode error & exception kustom
│
├── model/
│   └── .gitkeep                  # Taruh mango_classifier.tflite di sini
│
├── tests/
│   ├── __init__.py
│   ├── test_health.py            # Pengujian endpoint health check
│   ├── test_predict_validation.py # Pengujian validasi upload
│   └── test_recommendation.py    # Pengujian service rekomendasi
│
├── PROJECT_SPEC.md               # Source of truth proyek
├── README.md
├── requirements.txt
├── vercel.json
├── .env.example
├── .gitignore
└── run_local.py                  # Script menjalankan server lokal
```

---

## Prasyarat

- **Python 3.11** — [python.org/downloads](https://www.python.org/downloads/)
- **pip** — sudah termasuk dalam instalasi Python
- File model `mango_classifier.tflite` (setelah proses training selesai)

---

## Instalasi

### 1. Clone repository

```bash
git clone https://github.com/username/MangoCheck.git
cd MangoCheck
```

### 2. Buat virtual environment

```bash
# Windows
python -m venv .venv
.venv\Scripts\activate

# Linux / Mac
python3 -m venv .venv
source .venv/bin/activate
```

### 3. Install dependency

**Untuk Windows (development):**

`tflite-runtime` tidak tersedia via pip untuk Windows. Gunakan TensorFlow penuh:

```bash
pip install Flask flask-cors numpy Pillow python-dotenv pytest
pip install tensorflow
```

Model service akan otomatis mendeteksi `tflite-runtime`, dan jika tidak tersedia akan menggunakan `tensorflow.lite` sebagai fallback.

**Untuk Linux / Mac (atau production):**

```bash
pip install -r requirements.txt
```

### 4. Salin file konfigurasi

```bash
# Windows
copy .env.example .env

# Linux / Mac
cp .env.example .env
```

---

## Konfigurasi Environment Variable

Edit file `.env` sesuai kebutuhan:

| Variable               | Default                                     | Keterangan                                      |
|------------------------|---------------------------------------------|-------------------------------------------------|
| `FLASK_DEBUG`          | `true`                                      | Mode debug Flask                                |
| `FLASK_PORT`           | `5000`                                      | Port server lokal                               |
| `MODEL_PATH`           | `model/mango_classifier.tflite`             | Path ke file model TFLite                       |
| `MODEL_INPUT_WIDTH`    | `224`                                       | Lebar input model (piksel)                      |
| `MODEL_INPUT_HEIGHT`   | `224`                                       | Tinggi input model (piksel)                     |
| `CLASS_LABELS`         | `unripe,ripe,rotten`                        | **Urutan kelas harus sama dengan saat training**|
| `CONFIDENCE_THRESHOLD` | `0.70`                                      | Batas confidence rendah (0.0–1.0)               |
| `MAX_UPLOAD_SIZE_MB`   | `4`                                         | Batas ukuran file upload (MB)                   |
| `MODEL_OUTPUT_TYPE`    | `probabilities`                             | `probabilities` atau `logits`                   |
| `NORMALIZATION_MODE`   | `0_1`                                       | `0_1`, `neg1_1`, atau `none`                    |
| `ALLOWED_ORIGINS`      | `http://localhost:3000,...`                 | CORS origins, dipisahkan koma                   |
| `MODEL_VERSION`        | `1.0.0`                                     | Versi model yang ditampilkan di respons          |
| `MAX_IMAGE_PIXELS`     | `50000000`                                  | Batas total piksel gambar                       |

> **Penting:** `CLASS_LABELS` dan `NORMALIZATION_MODE` HARUS disesuaikan dengan pengaturan saat training model. Kesalahan konfigurasi ini akan menghasilkan prediksi yang salah meskipun model berjalan tanpa error.

---

## Menaruh File Model

File model **tidak di-commit ke Git** karena ukurannya bisa sangat besar.

### Untuk development lokal

Setelah proses training dan ekspor model selesai, salin file ke:

```
MangoCheck/model/mango_classifier.tflite
```

### Untuk deployment Vercel

Karena Vercel tidak menyimpan file statis di luar bundle, ada dua pilihan:

1. **Commit model ke repository** menggunakan Git LFS (untuk model < 100 MB)
2. **Unduh model saat startup** dari URL publik (misalnya GitHub Releases atau Google Drive) — perlu kode tambahan di `model_service.py`

Untuk deployment ke **Render** atau **Hugging Face Spaces**, model dapat disimpan langsung di repository atau di persistent disk.

---

## Menjalankan Server Lokal

Pastikan virtual environment sudah aktif dan file `.env` sudah dibuat.

```bash
python run_local.py
```

Server akan berjalan di:

```
http://localhost:5000
```

Output yang diharapkan:

```
=======================================================
  MangoCheck API — Local Development Server
=======================================================
  Host   : 0.0.0.0
  Port   : 5000
  Debug  : True
  Model  : /path/to/MangoCheck/model/mango_classifier.tflite
-------------------------------------------------------
  Endpoints:
    GET  http://localhost:5000/api/health
    POST http://localhost:5000/api/predict
=======================================================
```

Jika file model belum ada, server tetap berjalan. Endpoint `/api/health` akan menampilkan `"model_loaded": false` dan endpoint `/api/predict` akan mengembalikan error `MODEL_NOT_AVAILABLE`.

---

## Menjalankan Test

```bash
pytest tests/ -v
```

Untuk melihat output lebih detail:

```bash
pytest tests/ -v --tb=short
```

Untuk menjalankan satu file test saja:

```bash
pytest tests/test_health.py -v
pytest tests/test_predict_validation.py -v
pytest tests/test_recommendation.py -v
```

Test dirancang untuk berjalan **tanpa file model asli** menggunakan mocking.

---

## Penggunaan API

### GET /api/health

Memeriksa status API dan ketersediaan model.

```bash
curl http://localhost:5000/api/health
```

**Respons (model tersedia):**

```json
{
  "success": true,
  "message": "MangoCheck API is running",
  "data": {
    "service": "mangocheck-api",
    "model_loaded": true
  }
}
```

**Respons (model belum tersedia):**

```json
{
  "success": true,
  "message": "MangoCheck API is running",
  "data": {
    "service": "mangocheck-api",
    "model_loaded": false
  }
}
```

---

### POST /api/predict

Mengirim foto mangga dan mendapatkan hasil prediksi.

```bash
curl -X POST http://localhost:5000/api/predict \
  -F "image=@/path/to/mango.jpg"
```

**Respons sukses (confidence tinggi):**

```json
{
  "success": true,
  "message": "Prediction completed successfully",
  "data": {
    "prediction": {
      "class_key": "ripe",
      "label": "Matang",
      "confidence": 0.9234,
      "confidence_percentage": 92.34
    },
    "recommendation": {
      "status": "prediction_available",
      "message": "Mangga matang. Prioritaskan untuk dijual atau dikonsumsi dalam waktu dekat.",
      "manual_review_note": null
    },
    "model": {
      "name": "MangoCheck Mango Classifier",
      "version": "1.0.0"
    }
  }
}
```

**Respons sukses (confidence rendah):**

```json
{
  "success": true,
  "message": "Prediction completed with low confidence",
  "data": {
    "prediction": {
      "class_key": "unripe",
      "label": "Mentah",
      "confidence": 0.5312,
      "confidence_percentage": 53.12
    },
    "recommendation": {
      "status": "manual_review_required",
      "message": "Mangga terindikasi mentah, tetapi hasil perlu diperiksa kembali.",
      "manual_review_note": "Tingkat keyakinan model rendah. Lakukan pemeriksaan visual secara manual."
    },
    "model": {
      "name": "MangoCheck Mango Classifier",
      "version": "1.0.0"
    }
  }
}
```

---

## Format Respons

### Error Response

Semua error mengikuti format yang sama:

```json
{
  "success": false,
  "error": {
    "code": "KODE_ERROR",
    "message": "Pesan error yang mudah dipahami."
  }
}
```

### Kode Error

| Kode                  | HTTP | Keterangan                                  |
|-----------------------|------|---------------------------------------------|
| `NO_IMAGE_FIELD`      | 400  | Field `image` tidak ada dalam request       |
| `EMPTY_FILE`          | 400  | File kosong atau nama file kosong           |
| `INVALID_IMAGE_FILE`  | 400  | File bukan gambar valid / gambar rusak      |
| `IMAGE_TOO_LARGE`     | 400  | Dimensi gambar melebihi batas piksel        |
| `FILE_TOO_LARGE`      | 413  | Ukuran file melebihi batas MB               |
| `UNSUPPORTED_FORMAT`  | 415  | Format file tidak didukung (selain JPG/PNG/WEBP) |
| `MODEL_NOT_AVAILABLE` | 503  | Model TFLite belum tersedia atau gagal muat |
| `INFERENCE_FAILED`    | 503  | Inference model gagal dijalankan            |
| `INTERNAL_ERROR`      | 500  | Error internal server                       |

---

## Keamanan Upload File

Backend menerapkan validasi berlapis untuk mencegah file berbahaya:

1. **Ukuran file** dibatasi 4 MB sebelum file diproses.
2. **Format file** divalidasi menggunakan Pillow, bukan hanya MIME type dari browser (MIME type dapat dipalsukan).
3. **Integritas gambar** diverifikasi menggunakan `PIL.Image.verify()` untuk mendeteksi file rusak atau corrupt.
4. **Setelah `verify()`**, gambar dibuka ulang karena Pillow menutup stream internal setelah verifikasi.
5. **Dimensi gambar** dibatasi untuk mencegah *decompression bomb* — gambar kecil yang mengembang menjadi sangat besar saat didekode.
6. **File upload tidak disimpan ke disk**. Seluruh proses menggunakan `BytesIO` di memori.
7. **Nama file dari pengguna tidak digunakan** sebagai path server.
8. **Traceback dan detail internal** tidak pernah dikirim ke client.

---

## Confidence Rendah

Model melaporkan confidence (tingkat keyakinan) untuk setiap prediksi. Jika confidence tertinggi di bawah **70%** (dapat dikonfigurasi via `CONFIDENCE_THRESHOLD`):

- Hasil prediksi tetap ditampilkan (kelas dengan confidence tertinggi).
- Status rekomendasi berubah menjadi `manual_review_required`.
- Pesan tambahan muncul: *"Tingkat keyakinan model rendah. Lakukan pemeriksaan visual secara manual."*
- Backend **tidak** menyembunyikan hasil atau menolak request.

Confidence rendah bisa terjadi karena:
- Foto kurang jelas, gelap, atau terpotong.
- Mangga dari varietas yang tidak terwakili dalam dataset training.
- Objek dalam foto bukan mangga.

---

## Deployment Vercel

### Langkah Deployment

1. Push kode ke GitHub (tanpa file `.env` dan `.tflite`).
2. Buat proyek baru di [vercel.com](https://vercel.com).
3. Hubungkan ke repository GitHub.
4. Tambahkan environment variable di Vercel Dashboard sesuai `.env.example`.
5. Deploy.

### Risiko dan Keterbatasan Vercel

| Risiko              | Keterangan                                                                 |
|---------------------|----------------------------------------------------------------------------|
| **Ukuran dependency** | `tflite-runtime` + `Pillow` + `NumPy` bisa mendekati batas 50 MB Vercel  |
| **Kompatibilitas**  | `tflite-runtime` hanya tersedia untuk Linux x86_64. Vercel menggunakan Linux, jadi kompatibel. |
| **Cold start**      | Instance serverless baru membutuhkan waktu untuk memuat Flask dan model TFLite. Request pertama setelah idle bisa 3–10 detik lebih lambat. |
| **Batas upload**    | Vercel membatasi ukuran request body. Pastikan sesuai dengan `MAX_UPLOAD_SIZE_MB`. |
| **File statis**     | File `mango_classifier.tflite` harus di-bundle bersama kode atau diunduh saat startup. |

### Alternatif Deployment

Jika Vercel tidak kompatibel, gunakan:

- **Render** — [render.com](https://render.com) — Mendukung Python, persistent disk, lebih mudah untuk model besar.
- **Hugging Face Spaces** — [huggingface.co/spaces](https://huggingface.co/spaces) — Mendukung Flask/Gradio, cocok untuk demo AI.

---

## Integrasi Frontend

Frontend akan dibuat di Tahap 3. Berikut panduan untuk pengembang frontend:

- Backend menerima `multipart/form-data`
- Field file **harus** bernama `image`
- Endpoint prediksi: `POST /api/predict`
- Backend mengembalikan JSON sesuai kontrak API di atas

**Contoh JavaScript (untuk referensi, belum ada file frontend):**

```javascript
async function predictMango(imageFile) {
  const formData = new FormData();
  formData.append("image", imageFile);  // field name harus "image"

  const response = await fetch("http://localhost:5000/api/predict", {
    method: "POST",
    body: formData,
    // Jangan set Content-Type secara manual — browser akan set boundary secara otomatis
  });

  const result = await response.json();

  if (result.success) {
    console.log("Kelas:", result.data.prediction.class_key);
    console.log("Label:", result.data.prediction.label);
    console.log("Confidence:", result.data.prediction.confidence_percentage + "%");
    console.log("Rekomendasi:", result.data.recommendation.message);

    if (result.data.recommendation.status === "manual_review_required") {
      console.warn("Peringatan:", result.data.recommendation.manual_review_note);
    }
  } else {
    console.error("Error:", result.error.code, result.error.message);
  }
}
```

---

## Lisensi Dataset

Model MangoCheck dilatih menggunakan dataset:

- **Nama dataset:** Unripe, Ripe, Rotten Mango
- **Platform:** Kaggle
- **Sumber:** [`adrinbd/unripe-ripe-rotten-mango`](https://www.kaggle.com/datasets/adrinbd/unripe-ripe-rotten-mango)
- **Lisensi:** CC0 1.0 Universal (Public Domain)

Meskipun CC0 tidak mewajibkan atribusi, sumber dataset tetap dicantumkan dalam dokumentasi ini sebagai bentuk penghargaan kepada kontributor dataset.

---

## Catatan Tambahan

- Model **hanya dirancang untuk gambar mangga**. Hasil untuk objek lain tidak dapat diandalkan.
- Hasil prediksi **bukan kepastian kualitas pangan profesional** dan tidak boleh dijadikan satu-satunya dasar keputusan.
- Backend **tidak menyimpan riwayat prediksi** dan **tidak memerlukan login**.
- Backend **tidak memiliki database** pada versi MVP ini.

---

*MangoCheck — Prototype Computer Vision untuk Klasifikasi Kematangan Mangga*
