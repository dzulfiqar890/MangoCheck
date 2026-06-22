# MangoCheck — Project Specification

## 1. Ringkasan Proyek

**MangoCheck** adalah prototype website berbasis *computer vision* untuk membantu pedagang buah, UMKM, dan pengguna umum mengidentifikasi tingkat kematangan mangga melalui foto.

Sistem menerima gambar mangga dari pengguna, lalu model *machine learning* mengklasifikasikan gambar tersebut ke dalam tiga kategori:

* **Mentah** (`unripe`)
* **Matang** (`ripe`)
* **Busuk** (`rotten`)

MangoCheck tidak dimaksudkan sebagai penilaian kualitas pangan yang pasti. Sistem ini adalah alat bantu keputusan awal untuk membantu pengguna mengatur prioritas penjualan, penyimpanan, konsumsi, dan pengelolaan buah yang sudah tidak layak.

---

## 2. Latar Belakang Masalah

Pedagang buah dan UMKM sering menentukan tingkat kematangan buah secara manual melalui warna, tekstur, aroma, atau pengalaman pribadi. Proses tersebut dapat memerlukan waktu, terutama ketika stok buah cukup banyak.

Kesalahan dalam mengelola stok dapat menyebabkan beberapa masalah:

* Mangga matang tidak segera dijual sehingga berisiko membusuk.
* Mangga mentah dijual terlalu cepat sehingga kualitas konsumsi belum optimal.
* Buah busuk tercampur dengan stok lain.
* Food waste meningkat karena buah terlambat diprioritaskan untuk dijual atau diolah.

MangoCheck dibuat sebagai prototype solusi digital yang membantu pengguna memperoleh indikasi awal tingkat kematangan mangga dari foto.

---

## 3. Tujuan Proyek

Tujuan MangoCheck adalah:

1. Mengklasifikasikan foto mangga ke kategori mentah, matang, atau busuk.
2. Memberikan rekomendasi tindakan berdasarkan hasil klasifikasi.
3. Membantu pengguna menentukan prioritas pengelolaan stok mangga.
4. Mendukung upaya pengurangan food waste pada skala pedagang kecil, UMKM, dan pengguna rumah tangga.
5. Menjadi prototype inovasi digital berbasis AI untuk portofolio jalur inovasi.

---

## 4. Target Pengguna

Target pengguna MangoCheck:

* Pedagang buah skala kecil.
* UMKM yang mengolah atau menjual buah.
* Pasar tradisional.
* Pengguna rumah tangga.
* Komunitas atau pihak yang menjalankan program pengurangan food waste.

---

## 5. Ruang Lingkup MVP

Versi awal atau Minimum Viable Product (MVP) hanya mencakup:

* Upload satu foto mangga.
* Validasi file gambar.
* Prediksi tingkat kematangan mangga.
* Tampilan hasil prediksi.
* Tampilan confidence atau tingkat keyakinan model.
* Rekomendasi tindakan berdasarkan hasil prediksi.
* Peringatan jika confidence model rendah.
* Endpoint API health check.
* Tidak menggunakan database.
* Tidak menyimpan riwayat prediksi.
* Tidak memiliki login atau register pengguna.

Fitur di luar ruang lingkup MVP tidak boleh dibuat sebelum alur utama upload gambar sampai hasil prediksi telah berjalan dengan baik.

---

## 6. Klasifikasi dan Rekomendasi

### 6.1 Kelas Model

| Class Key | Label Bahasa Indonesia | Arti                                                          |
| --------- | ---------------------- | ------------------------------------------------------------- |
| `unripe`  | Mentah                 | Mangga belum siap diprioritaskan untuk dijual atau dikonsumsi |
| `ripe`    | Matang                 | Mangga siap diprioritaskan untuk dijual atau dikonsumsi       |
| `rotten`  | Busuk                  | Mangga perlu dipisahkan dari stok lain                        |

### 6.2 Rekomendasi Sistem

| Hasil Prediksi | Rekomendasi                                                                                           |
| -------------- | ----------------------------------------------------------------------------------------------------- |
| Mentah         | Mangga masih mentah. Simpan dan pantau kembali sebelum dijual atau dikonsumsi.                        |
| Matang         | Mangga matang. Prioritaskan untuk dijual atau dikonsumsi dalam waktu dekat.                           |
| Busuk          | Mangga terindikasi busuk. Pisahkan dari stok dan pertimbangkan pengolahan limbah organik atau kompos. |

### 6.3 Confidence Rendah

Jika confidence prediksi tertinggi berada di bawah **70%**, sistem tetap dapat menampilkan hasil prediksi tertinggi, tetapi harus memberi status:

```text
manual_review_required
```

Pesan tambahan yang harus ditampilkan:

> Tingkat keyakinan model rendah. Lakukan pemeriksaan visual secara manual.

Sistem tidak boleh mengklaim hasil prediksi sebagai kepastian mutlak.

---

## 7. Dataset dan Model

### 7.1 Dataset Awal

Model MangoCheck akan dilatih menggunakan dataset:

* Nama dataset: **Unripe, Ripe, Rotten Mango**
* Platform: Kaggle
* Sumber: `adrinbd/unripe-ripe-rotten-mango`
* Kelas data: unripe, ripe, rotten
* Lisensi yang tercantum: **CC0 1.0 Universal**

Dataset digunakan sebagai data pelatihan awal. Dokumentasi proyek dan portofolio harus tetap mencantumkan sumber dataset serta lisensinya, meskipun CC0 tidak mewajibkan atribusi.

### 7.2 Model

* Training dilakukan terpisah menggunakan Google Colab atau komputer lokal.
* Backend tidak melakukan training.
* Backend hanya menjalankan inference atau prediksi.
* Model hasil training diekspor ke format TensorFlow Lite:

```text
mango_classifier.tflite
```

### 7.3 Batasan Model

* Model hanya dirancang untuk memproses gambar mangga.
* Hasil untuk objek selain mangga tidak dapat diandalkan.
* Akurasi model bergantung pada kualitas dataset, variasi gambar, proses training, dan kondisi foto pengguna.
* Model tidak boleh diklaim sebagai alat penilaian kualitas pangan profesional atau kepastian keamanan konsumsi.

---

## 8. Arsitektur Sistem

```text
Pengguna
   ↓
Frontend HTML + CSS + JavaScript
   ↓ upload foto menggunakan multipart/form-data
Backend Python + Flask
   ↓ validasi file dan preprocessing gambar
TensorFlow Lite Model (.tflite)
   ↓ hasil prediksi JSON
Frontend menampilkan hasil dan rekomendasi
```

### 8.1 Teknologi Backend

| Komponen          | Teknologi                       |
| ----------------- | ------------------------------- |
| Bahasa backend    | Python                          |
| Framework API     | Flask                           |
| Inference model   | TensorFlow Lite                 |
| Runtime model     | tflite-runtime                  |
| Pengolahan gambar | Pillow                          |
| Perhitungan array | NumPy                           |
| Testing           | pytest                          |
| Database          | Tidak digunakan pada MVP        |
| Hosting target    | Vercel                          |
| Hosting cadangan  | Render atau Hugging Face Spaces |

### 8.2 Teknologi Frontend

Frontend akan dibuat setelah backend selesai dan telah diuji.

| Komponen                  | Teknologi          |
| ------------------------- | ------------------ |
| Struktur halaman          | HTML               |
| Styling                   | CSS                |
| Interaksi dan API request | JavaScript vanilla |

---

## 9. Kontrak API

### 9.1 Health Check

**Endpoint**

```text
GET /api/health
```

**Respons sukses**

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

Jika model belum tersedia, endpoint health check tetap harus merespons sukses, tetapi nilai `model_loaded` harus bernilai `false`.

---

### 9.2 Prediksi Gambar

**Endpoint**

```text
POST /api/predict
```

**Content-Type**

```text
multipart/form-data
```

**Field wajib**

```text
image
```

**Format file yang diizinkan**

* JPEG
* PNG
* WEBP

**Batas ukuran file**

```text
4 MB
```

**Respons prediksi sukses**

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

**Respons confidence rendah**

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

## 10. Standar Validasi dan Keamanan Backend

Backend wajib menerapkan aturan berikut:

1. Field `image` harus tersedia.
2. File upload tidak boleh kosong.
3. File hanya boleh berformat JPEG, PNG, atau WEBP.
4. Validasi tidak boleh hanya mengandalkan MIME type dari browser.
5. File harus diverifikasi sebagai gambar valid menggunakan Pillow.
6. Gambar harus dibuka ulang setelah proses verifikasi.
7. File lebih dari 4 MB harus ditolak.
8. Dimensi gambar harus dibatasi untuk mencegah gambar sangat besar atau decompression bomb.
9. File upload diproses di memory menggunakan `BytesIO` jika memungkinkan.
10. File upload tidak boleh disimpan secara permanen.
11. Nama file dari pengguna tidak boleh dieksekusi atau digunakan sebagai path server.
12. Backend tidak boleh menggunakan `eval`, `pickle`, atau shell command.
13. Error internal, traceback, path server, dan environment variable tidak boleh dikirim ke client.
14. Error internal harus dicatat secara aman pada server log.
15. CORS harus dapat dikonfigurasi menggunakan environment variable.
16. CORS tidak boleh memakai wildcard `*` sebagai default production.
17. Jika model belum tersedia, API harus mengembalikan error jelas dan tidak boleh menghasilkan prediksi dummy.
18. Jika inference gagal, API harus mengembalikan error yang konsisten.

### Format Error API

```json
{
  "success": false,
  "error": {
    "code": "INVALID_IMAGE_FILE",
    "message": "File yang diunggah bukan gambar yang valid."
  }
}
```

### HTTP Status Code

| Kondisi                                | Status |
| -------------------------------------- | ------ |
| Prediksi berhasil                      | 200    |
| Request atau file tidak valid          | 400    |
| Ukuran file terlalu besar              | 413    |
| Format file tidak didukung             | 415    |
| Model belum tersedia atau gagal dimuat | 503    |
| Error internal                         | 500    |

---

## 11. Konfigurasi Backend

Konfigurasi penting harus berada di file konfigurasi atau environment variable.

| Variable               | Fungsi                                       |
| ---------------------- | -------------------------------------------- |
| `MODEL_PATH`           | Lokasi file `.tflite`                        |
| `MODEL_INPUT_WIDTH`    | Lebar input model                            |
| `MODEL_INPUT_HEIGHT`   | Tinggi input model                           |
| `CLASS_LABELS`         | Urutan kelas model                           |
| `CONFIDENCE_THRESHOLD` | Batas confidence rendah                      |
| `MAX_UPLOAD_SIZE_MB`   | Batas ukuran upload                          |
| `ALLOWED_ORIGINS`      | Domain frontend yang diizinkan mengakses API |
| `MODEL_VERSION`        | Versi model                                  |
| `MODEL_OUTPUT_TYPE`    | `probabilities` atau `logits`                |
| `NORMALIZATION_MODE`   | Contoh: `0_1` atau `none`                    |

Normalisasi dan urutan kelas harus disesuaikan dengan proses training model. Tidak boleh membuat asumsi tersembunyi.

---

## 12. Struktur Folder Target

```text
mangocheck/
│
├── api/
│   └── index.py
│
├── app/
│   ├── __init__.py
│   ├── config.py
│   ├── routes/
│   │   ├── __init__.py
│   │   ├── health.py
│   │   └── predict.py
│   ├── services/
│   │   ├── __init__.py
│   │   ├── image_service.py
│   │   ├── model_service.py
│   │   └── recommendation_service.py
│   ├── schemas/
│   │   ├── __init__.py
│   │   └── response_schema.py
│   └── utils/
│       ├── __init__.py
│       └── errors.py
│
├── model/
│   └── mango_classifier.tflite
│
├── tests/
│   ├── __init__.py
│   ├── test_health.py
│   ├── test_predict_validation.py
│   └── test_recommendation.py
│
├── PROJECT_SPEC.md
├── README.md
├── requirements.txt
├── vercel.json
├── .env.example
├── .gitignore
└── run_local.py
```

Struktur boleh disempurnakan jika ada alasan teknis yang jelas, tetapi backend harus tetap modular, mudah dibaca, dan tidak membuat satu file besar.

---

## 13. Tahapan Pengerjaan

### Tahap 1 — Backend API

Prioritas pertama:

1. Menyiapkan struktur backend Python dan Flask.
2. Membuat endpoint `/api/health`.
3. Membuat endpoint `/api/predict`.
4. Membuat validasi upload gambar.
5. Membuat service preprocessing gambar.
6. Membuat service TensorFlow Lite inference.
7. Membuat service rekomendasi.
8. Membuat error handler konsisten.
9. Membuat test dasar.
10. Menjalankan backend secara lokal.

### Tahap 2 — Model Machine Learning

1. Menyiapkan dataset.
2. Melatih model klasifikasi.
3. Mengevaluasi model.
4. Mengekspor model menjadi `.tflite`.
5. Menyesuaikan konfigurasi input, normalisasi, output model, dan urutan kelas.
6. Menguji endpoint prediksi dengan model asli.

### Tahap 3 — Frontend

Frontend hanya dibuat setelah backend dapat diuji.

Frontend akan memiliki:

* Landing page.
* Halaman upload foto mangga.
* Preview gambar.
* Tombol analisis.
* Loading state.
* Tampilan hasil prediksi.
* Tampilan confidence.
* Tampilan rekomendasi.
* Pesan error yang mudah dipahami.
* Desain responsif untuk desktop dan mobile.

Frontend mengirim file menggunakan `FormData` dengan field bernama `image` ke endpoint:

```text
POST /api/predict
```

### Tahap 4 — Deployment

1. Deploy backend ke Vercel.
2. Uji endpoint production.
3. Jika Vercel tidak kompatibel dengan dependency TFLite, pindahkan backend ke Render atau Hugging Face Spaces.
4. Deploy frontend setelah backend stabil.
5. Rekam video demo untuk portofolio OPES.

---

## 14. Standar Kualitas Kode

Kode harus:

* Modular.
* Mudah dipahami.
* Menggunakan nama variabel dan fungsi yang jelas.
* Menggunakan type hints jika relevan.
* Memiliki docstring singkat pada fungsi atau class penting.
* Memiliki komentar informatif pada bagian penting, terutama validasi file, preprocessing, pemuatan model, dan alasan keamanan.
* Tidak menggunakan komentar berlebihan atau komentar generik.
* Tidak menggunakan hasil prediksi dummy.
* Tidak menyembunyikan kegagalan model.
* Tidak membuat klaim akurasi tanpa hasil evaluasi model.

---

## 15. Kriteria Selesai MVP

MVP MangoCheck dianggap selesai jika:

* Backend dapat dijalankan secara lokal.
* Endpoint `/api/health` berjalan.
* Endpoint `/api/predict` dapat menerima foto mangga.
* File invalid ditolak dengan error yang jelas.
* Model `.tflite` dapat dimuat.
* Model menghasilkan prediksi mentah, matang, atau busuk.
* Confidence dan rekomendasi dikembalikan dalam JSON.
* Confidence rendah memunculkan peringatan pemeriksaan manual.
* Test dasar dapat dijalankan.
* Tidak ada database dan tidak ada penyimpanan upload permanen.
* Dokumentasi README tersedia.
* Backend siap dihubungkan dengan frontend HTML, CSS, dan JavaScript.
