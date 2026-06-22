"""
app/utils/errors.py
Kelas error kustom dan helper untuk membuat respons error JSON yang konsisten.
Semua error yang dikembalikan ke client mengikuti format kontrak API.
"""

from flask import jsonify
from typing import Tuple


# --- Kode Error Standar ---
# Daftar kode ini menjadi kontrak antara backend dan frontend.

class ErrorCode:
    # Upload / validasi file
    NO_IMAGE_FIELD      = "NO_IMAGE_FIELD"
    EMPTY_FILE          = "EMPTY_FILE"
    FILE_TOO_LARGE      = "FILE_TOO_LARGE"
    UNSUPPORTED_FORMAT  = "UNSUPPORTED_FORMAT"
    INVALID_IMAGE_FILE  = "INVALID_IMAGE_FILE"
    IMAGE_TOO_LARGE     = "IMAGE_TOO_LARGE"

    # Model
    MODEL_NOT_AVAILABLE = "MODEL_NOT_AVAILABLE"
    INFERENCE_FAILED    = "INFERENCE_FAILED"

    # Server
    INTERNAL_ERROR      = "INTERNAL_ERROR"


# --- Exception Kustom ---

class MangoCheckError(Exception):
    """Base exception untuk semua error terkontrol MangoCheck."""

    def __init__(self, code: str, message: str, http_status: int):
        self.code = code
        self.message = message
        self.http_status = http_status
        super().__init__(message)


class ValidationError(MangoCheckError):
    """Error validasi input dari client (400)."""

    def __init__(self, code: str, message: str):
        super().__init__(code, message, 400)


class FileTooLargeError(MangoCheckError):
    """File melebihi batas ukuran yang diizinkan (413)."""

    def __init__(self, message: str = "Ukuran file melebihi batas maksimum yang diizinkan."):
        super().__init__(ErrorCode.FILE_TOO_LARGE, message, 413)


class UnsupportedFormatError(MangoCheckError):
    """Format file tidak didukung (415)."""

    def __init__(self, message: str = "Format file tidak didukung. Gunakan JPEG, PNG, atau WEBP."):
        super().__init__(ErrorCode.UNSUPPORTED_FORMAT, message, 415)


class ModelNotAvailableError(MangoCheckError):
    """Model belum tersedia atau gagal dimuat (503)."""

    def __init__(self, message: str = "Model klasifikasi belum tersedia. Tempatkan file mango_classifier.tflite di folder model/."):
        super().__init__(ErrorCode.MODEL_NOT_AVAILABLE, message, 503)


class InferenceError(MangoCheckError):
    """Inference model gagal dijalankan (503)."""

    def __init__(self, message: str = "Inference model gagal. Coba lagi atau periksa konfigurasi model."):
        super().__init__(ErrorCode.INFERENCE_FAILED, message, 503)


# --- Helper Respons ---

def make_error_response(code: str, message: str, http_status: int) -> Tuple:
    """
    Membuat respons error JSON standar sesuai kontrak API.
    Tidak menyertakan traceback atau detail internal ke client.
    """
    body = {
        "success": False,
        "error": {
            "code": code,
            "message": message,
        }
    }
    return jsonify(body), http_status


def make_success_response(message: str, data: dict) -> Tuple:
    """Membuat respons sukses JSON standar sesuai kontrak API."""
    body = {
        "success": True,
        "message": message,
        "data": data,
    }
    return jsonify(body), 200
