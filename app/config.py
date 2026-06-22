"""
app/config.py
Konfigurasi terpusat MangoCheck. Semua nilai dapat di-override melalui environment variable.
Urutan kelas dan normalisasi HARUS disesuaikan dengan proses training model.
"""

import os
from pathlib import Path

# Root project dideteksi secara absolut dari lokasi file ini,
# agar tidak bergantung pada current working directory saat server dijalankan.
PROJECT_ROOT = Path(__file__).resolve().parent.parent


class Config:
    """Konfigurasi utama aplikasi MangoCheck."""

    # --- Path Model ---
    # Gunakan path absolut agar model dapat dimuat dari mana saja server dijalankan.
    MODEL_PATH: str = os.environ.get(
        "MODEL_PATH",
        str(PROJECT_ROOT / "model" / "mango_classifier.tflite"),
    )

    # --- Dimensi Input Model ---
    # Harus sama dengan ukuran input saat training. Default: 224x224 (MobileNet standar).
    MODEL_INPUT_WIDTH: int = int(os.environ.get("MODEL_INPUT_WIDTH", 224))
    MODEL_INPUT_HEIGHT: int = int(os.environ.get("MODEL_INPUT_HEIGHT", 224))

    # --- Urutan Kelas ---
    # PENTING: Urutan ini harus sama persis dengan urutan kelas saat training model.
    # Jika urutan berbeda, prediksi akan salah meskipun model berjalan normal.
    CLASS_LABELS: list[str] = os.environ.get(
        "CLASS_LABELS", "unripe,ripe,rotten"
    ).split(",")

    # --- Threshold Confidence ---
    # Prediksi dengan confidence di bawah threshold ini akan ditandai manual_review_required.
    CONFIDENCE_THRESHOLD: float = float(
        os.environ.get("CONFIDENCE_THRESHOLD", 0.70)
    )

    # --- Batas Ukuran Upload ---
    MAX_UPLOAD_SIZE_MB: int = int(os.environ.get("MAX_UPLOAD_SIZE_MB", 4))
    MAX_UPLOAD_SIZE_BYTES: int = MAX_UPLOAD_SIZE_MB * 1024 * 1024

    # --- CORS ---
    # Jangan gunakan wildcard '*' di production.
    # Daftar origin dipisahkan koma. Contoh: http://localhost:3000,http://localhost:5500
    ALLOWED_ORIGINS: list[str] = os.environ.get(
        "ALLOWED_ORIGINS",
        "http://localhost:3000,http://127.0.0.1:3000,http://localhost:5500,http://127.0.0.1:5500",
    ).split(",")

    # --- Versi dan Nama Model ---
    MODEL_NAME: str = "MangoCheck Mango Classifier"
    MODEL_VERSION: str = os.environ.get("MODEL_VERSION", "1.0.0")

    # --- Tipe Output Model ---
    # "probabilities": output model sudah berupa probabilitas (sudah softmax). Jangan softmax lagi.
    # "logits"       : output model adalah logit mentah. Backend akan menerapkan softmax numerik stabil.
    MODEL_OUTPUT_TYPE: str = os.environ.get("MODEL_OUTPUT_TYPE", "probabilities")

    # --- Mode Normalisasi ---
    # "0_1"  : pixel / 255.0  -> nilai float antara 0.0 dan 1.0
    # "neg1_1": (pixel / 127.5) - 1.0 -> nilai float antara -1.0 dan 1.0 (MobileNet standar)
    # "none" : tidak ada normalisasi (jarang digunakan)
    # Harus cocok dengan preprocessing yang digunakan saat training.
    NORMALIZATION_MODE: str = os.environ.get("NORMALIZATION_MODE", "0_1")

    # --- Batas Dimensi Gambar ---
    # Mencegah decompression bomb atau gambar berukuran ekstrem yang bisa menguras memori.
    MAX_IMAGE_PIXELS: int = int(os.environ.get("MAX_IMAGE_PIXELS", 50_000_000))

    # --- Format Gambar yang Diizinkan ---
    ALLOWED_MIME_TYPES: set[str] = {"image/jpeg", "image/png", "image/webp"}
    ALLOWED_PIL_FORMATS: set[str] = {"JPEG", "PNG", "WEBP"}

    # --- Flask Debug ---
    FLASK_DEBUG: bool = os.environ.get("FLASK_DEBUG", "false").lower() == "true"
    FLASK_PORT: int = int(os.environ.get("FLASK_PORT", 5000))
    FLASK_HOST: str = os.environ.get("FLASK_HOST", "0.0.0.0")
