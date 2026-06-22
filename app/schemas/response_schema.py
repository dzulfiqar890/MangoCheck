"""
app/schemas/response_schema.py
Fungsi builder untuk membangun payload respons sesuai kontrak API MangoCheck.
Memastikan struktur JSON selalu konsisten di seluruh route.
"""

from typing import Optional


def build_prediction_response(
    class_key: str,
    label: str,
    confidence: float,
    recommendation_status: str,
    recommendation_message: str,
    manual_review_note: Optional[str],
    model_name: str,
    model_version: str,
) -> dict:
    """
    Membangun dictionary payload untuk respons prediksi sukses.
    Semua nilai numerik dibulatkan secara eksplisit agar konsisten.
    """
    confidence_rounded = round(confidence, 4)
    confidence_percentage = round(confidence * 100, 2)

    return {
        "prediction": {
            "class_key": class_key,
            "label": label,
            "confidence": confidence_rounded,
            "confidence_percentage": confidence_percentage,
        },
        "recommendation": {
            "status": recommendation_status,
            "message": recommendation_message,
            "manual_review_note": manual_review_note,
        },
        "model": {
            "name": model_name,
            "version": model_version,
        },
    }


def build_health_response(model_loaded: bool) -> dict:
    """
    Membangun dictionary payload untuk respons health check.
    Health check tidak pernah gagal — model_loaded hanya menunjukkan status model.
    """
    return {
        "service": "mangocheck-api",
        "model_loaded": model_loaded,
    }
