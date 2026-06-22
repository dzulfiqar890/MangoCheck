"""
app/services/image_service.py
Validasi dan preprocessing gambar upload untuk inference TFLite.

Alasan validasi berlapis:
- Browser MIME type dapat dipalsukan, jadi validasi tidak boleh hanya mengandalkan Content-Type.
- PIL.Image.verify() mendeteksi korupsi tanpa mendekode seluruh gambar.
- Setelah verify(), file pointer harus direset atau gambar dibuka ulang karena
  verify() menutup stream internal. Ini adalah perilaku Pillow yang terdokumentasi.
- Pembatasan dimensi mencegah decompression bomb (gambar kecil yang mengembang
  menjadi sangat besar saat didekode, menguras RAM).
"""

import io
import logging
import numpy as np
from PIL import Image, UnidentifiedImageError

from app.config import Config
from app.utils.errors import (
    ErrorCode,
    ValidationError,
    FileTooLargeError,
    UnsupportedFormatError,
)

logger = logging.getLogger(__name__)


def validate_and_preprocess(file_storage) -> np.ndarray:
    """
    Menerima FileStorage dari Flask, memvalidasi, dan mengembalikan
    array NumPy siap pakai untuk inference TFLite.

    Args:
        file_storage: werkzeug.datastructures.FileStorage dari request.files

    Returns:
        np.ndarray dengan shape (1, H, W, 3) dan dtype float32

    Raises:
        ValidationError, FileTooLargeError, UnsupportedFormatError
    """
    # --- 1. Baca seluruh isi file ke memori ---
    # Menggunakan BytesIO agar file tidak pernah disimpan ke disk.
    raw_bytes = file_storage.read()

    # --- 2. Tolak file kosong ---
    if not raw_bytes:
        raise ValidationError(
            ErrorCode.EMPTY_FILE,
            "File yang diunggah kosong."
        )

    # --- 3. Periksa ukuran file ---
    file_size = len(raw_bytes)
    if file_size > Config.MAX_UPLOAD_SIZE_BYTES:
        raise FileTooLargeError(
            f"Ukuran file ({file_size // (1024*1024)} MB) melebihi batas "
            f"{Config.MAX_UPLOAD_SIZE_MB} MB."
        )

    # --- 4. Verifikasi bahwa file adalah gambar valid menggunakan Pillow ---
    # PIL.Image.verify() membaca header gambar dan mendeteksi korupsi.
    # PENTING: verify() menutup stream internal. Gambar HARUS dibuka ulang setelahnya.
    try:
        verify_buf = io.BytesIO(raw_bytes)
        with Image.open(verify_buf) as probe:
            # Periksa format sebelum verify agar error format lebih informatif
            pil_format = probe.format  # misalnya "JPEG", "PNG", "WEBP"
            probe.verify()
    except UnidentifiedImageError:
        raise ValidationError(
            ErrorCode.INVALID_IMAGE_FILE,
            "File yang diunggah bukan gambar yang valid."
        )
    except Exception as exc:
        # Tangani file rusak atau corrupt
        logger.warning("Gambar gagal diverifikasi: %s", exc)
        raise ValidationError(
            ErrorCode.INVALID_IMAGE_FILE,
            "File gambar rusak atau tidak dapat dibaca."
        )

    # --- 5. Periksa format gambar ---
    # Validasi menggunakan format yang dideteksi Pillow, bukan MIME type dari browser.
    if pil_format not in Config.ALLOWED_PIL_FORMATS:
        raise UnsupportedFormatError(
            f"Format '{pil_format}' tidak didukung. Gunakan JPEG, PNG, atau WEBP."
        )

    # --- 6. Buka ulang gambar untuk preprocessing ---
    # Wajib dibuka ulang karena verify() telah menutup stream internal.
    try:
        image_buf = io.BytesIO(raw_bytes)
        img = Image.open(image_buf)

        # --- 7. Periksa dimensi gambar (cegah decompression bomb) ---
        width, height = img.size
        if width * height > Config.MAX_IMAGE_PIXELS:
            raise ValidationError(
                ErrorCode.IMAGE_TOO_LARGE,
                f"Dimensi gambar terlalu besar ({width}x{height} piksel). "
                f"Batas maksimum adalah {Config.MAX_IMAGE_PIXELS:,} piksel total."
            )

        # --- 8. Konversi ke RGB ---
        # Wajib dilakukan sebelum resize agar channel konsisten (3 channel).
        # Gambar PNG bisa memiliki mode RGBA atau P, WEBP bisa RGBA — model hanya menerima RGB.
        img = img.convert("RGB")

        # --- 9. Resize sesuai dimensi input model ---
        target_size = (Config.MODEL_INPUT_WIDTH, Config.MODEL_INPUT_HEIGHT)
        img = img.resize(target_size, Image.BILINEAR)

    except ValidationError:
        raise
    except Exception as exc:
        logger.warning("Preprocessing gambar gagal: %s", exc)
        raise ValidationError(
            ErrorCode.INVALID_IMAGE_FILE,
            "Gambar tidak dapat diproses. Pastikan file tidak rusak."
        )

    # --- 10. Ubah ke NumPy array dan normalisasi ---
    img_array = np.array(img, dtype=np.float32)  # shape: (H, W, 3)
    img_array = _normalize(img_array)

    # --- 11. Tambahkan batch dimension ---
    # TFLite mengharapkan input shape (1, H, W, 3)
    img_array = np.expand_dims(img_array, axis=0)

    return img_array


def _normalize(img_array: np.ndarray) -> np.ndarray:
    """
    Menormalisasi pixel gambar sesuai NORMALIZATION_MODE.
    Normalisasi HARUS sama dengan yang digunakan saat training model.

    Mode yang didukung:
    - "0_1"     : pixel / 255.0              (rentang 0.0 hingga 1.0)
    - "neg1_1"  : (pixel / 127.5) - 1.0     (rentang -1.0 hingga 1.0, MobileNetV2 default)
    - "none"    : tidak ada normalisasi
    """
    mode = Config.NORMALIZATION_MODE.strip().lower()

    if mode == "0_1":
        return img_array / 255.0
    elif mode == "neg1_1":
        return (img_array / 127.5) - 1.0
    elif mode == "none":
        return img_array
    else:
        # Mode tidak dikenali — log peringatan dan gunakan 0_1 sebagai fallback aman
        logger.warning(
            "NORMALIZATION_MODE '%s' tidak dikenali. Menggunakan '0_1' sebagai fallback.", mode
        )
        return img_array / 255.0
