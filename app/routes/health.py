"""
app/routes/health.py
Endpoint GET /api/health untuk memeriksa status API dan ketersediaan model.
Health check tidak boleh gagal hanya karena model belum tersedia.
"""

import logging
from flask import Blueprint
from app.services import model_service
from app.schemas.response_schema import build_health_response
from app.utils.errors import make_success_response

logger = logging.getLogger(__name__)
health_bp = Blueprint("health", __name__)


@health_bp.route("/health", methods=["GET"])
def health_check():
    """
    Memeriksa apakah API berjalan dan apakah model sudah dimuat.
    Selalu mengembalikan HTTP 200 — model_loaded hanya menunjukkan status model.
    """
    model_loaded = model_service.is_model_loaded()

    if not model_loaded:
        logger.info(
            "Health check: API berjalan, tetapi model belum tersedia. "
            "Tempatkan mango_classifier.tflite di folder model/."
        )

    data = build_health_response(model_loaded=model_loaded)
    return make_success_response("MangoCheck API is running", data)
