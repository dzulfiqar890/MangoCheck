"""
app/routes/predict.py
Endpoint POST /api/predict untuk menerima upload gambar mangga dan menjalankan prediksi.
"""

import logging
from flask import Blueprint, request
from app.config import Config
from app.services import image_service, model_service
from app.services.recommendation_service import get_recommendation
from app.schemas.response_schema import build_prediction_response
from app.utils.errors import (
    make_success_response,
    make_error_response,
    MangoCheckError,
    ValidationError,
    ErrorCode,
)

logger = logging.getLogger(__name__)
predict_bp = Blueprint("predict", __name__)


@predict_bp.route("/predict", methods=["POST"])
def predict():
    """
    Menerima gambar mangga via multipart/form-data, memvalidasi,
    menjalankan inference TFLite, dan mengembalikan prediksi beserta rekomendasi.

    Field wajib: image (file)
    Format yang diterima: JPEG, PNG, WEBP
    Batas ukuran: 4 MB
    """
    # --- 1. Periksa keberadaan field 'image' di request ---
    if "image" not in request.files:
        return make_error_response(
            ErrorCode.NO_IMAGE_FIELD,
            "Field 'image' tidak ditemukan dalam request. Kirim file menggunakan multipart/form-data.",
            400,
        )

    file = request.files["image"]

    # --- 2. Periksa apakah file dipilih (nama file tidak kosong) ---
    if file.filename == "" or file.filename is None:
        return make_error_response(
            ErrorCode.EMPTY_FILE,
            "Tidak ada file yang dipilih.",
            400,
        )

    # --- 3. Validasi dan preprocess gambar ---
    # image_service menangani: validasi ukuran, format, integritas, dimensi, dan normalisasi.
    # Jika validasi gagal, MangoCheckError akan dilempar dan ditangkap di sini atau
    # oleh error handler global Flask.
    try:
        img_array = image_service.validate_and_preprocess(file)
    except MangoCheckError as exc:
        return make_error_response(exc.code, exc.message, exc.http_status)

    # --- 4. Jalankan inference model ---
    try:
        class_key, confidence = model_service.predict(img_array)
    except MangoCheckError as exc:
        return make_error_response(exc.code, exc.message, exc.http_status)

    # --- 5. Buat rekomendasi berdasarkan kelas dan confidence ---
    label, rec_status, rec_message, manual_review_note = get_recommendation(
        class_key, confidence
    )

    # --- 6. Tentukan pesan respons ---
    if rec_status == "manual_review_required":
        response_message = "Prediction completed with low confidence"
    else:
        response_message = "Prediction completed successfully"

    # --- 7. Bangun dan kembalikan respons ---
    data = build_prediction_response(
        class_key=class_key,
        label=label,
        confidence=confidence,
        recommendation_status=rec_status,
        recommendation_message=rec_message,
        manual_review_note=manual_review_note,
        model_name=Config.MODEL_NAME,
        model_version=Config.MODEL_VERSION,
    )

    return make_success_response(response_message, data)
