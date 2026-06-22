"""
app/services/recommendation_service.py
Menghasilkan rekomendasi tindakan berdasarkan hasil prediksi kelas dan confidence.
Rekomendasi tidak mengklaim kepastian kualitas pangan — hanya indikasi awal.
"""

from typing import Optional, Tuple
from app.config import Config


# Mapping kelas ke label bahasa Indonesia dan pesan rekomendasi.
# Urutan kelas tidak bergantung pada urutan dict ini — bergantung pada CLASS_LABELS di config.
_CLASS_RECOMMENDATIONS: dict[str, dict[str, str]] = {
    "unripe": {
        "label": "Mentah",
        "message": "Mangga masih mentah. Simpan dan pantau kembali sebelum dijual atau dikonsumsi.",
        "low_confidence_message": "Mangga terindikasi mentah, tetapi hasil perlu diperiksa kembali.",
    },
    "ripe": {
        "label": "Matang",
        "message": "Mangga matang. Prioritaskan untuk dijual atau dikonsumsi dalam waktu dekat.",
        "low_confidence_message": "Mangga terindikasi matang, tetapi hasil perlu diperiksa kembali.",
    },
    "rotten": {
        "label": "Busuk",
        "message": "Mangga terindikasi busuk. Pisahkan dari stok dan pertimbangkan pengolahan limbah organik atau kompos.",
        "low_confidence_message": "Mangga terindikasi busuk, tetapi hasil perlu diperiksa kembali.",
    },
}

_LOW_CONFIDENCE_NOTE = (
    "Tingkat keyakinan model rendah. Lakukan pemeriksaan visual secara manual."
)


def get_recommendation(
    class_key: str,
    confidence: float,
    threshold: float = Config.CONFIDENCE_THRESHOLD,
) -> Tuple[str, str, str, Optional[str]]:
    """
    Menghasilkan label, status rekomendasi, pesan rekomendasi, dan catatan review manual.

    Returns:
        Tuple berisi (label, status, message, manual_review_note)
        - label             : label Bahasa Indonesia kelas
        - status            : "prediction_available" atau "manual_review_required"
        - message           : pesan rekomendasi untuk pengguna
        - manual_review_note: catatan tambahan jika confidence rendah, atau None
    """
    # Gunakan kelas "unknown" sebagai fallback jika class_key tidak dikenali.
    # Ini tidak seharusnya terjadi jika CLASS_LABELS dikonfigurasi dengan benar.
    rec = _CLASS_RECOMMENDATIONS.get(class_key)
    if rec is None:
        return (
            class_key,
            "manual_review_required",
            f"Kelas '{class_key}' tidak dikenali. Periksa konfigurasi CLASS_LABELS.",
            _LOW_CONFIDENCE_NOTE,
        )

    label = rec["label"]
    is_low_confidence = confidence < threshold

    if is_low_confidence:
        # Confidence rendah: gunakan pesan yang lebih hati-hati dan tandai untuk review manual.
        return (
            label,
            "manual_review_required",
            rec["low_confidence_message"],
            _LOW_CONFIDENCE_NOTE,
        )
    else:
        return (
            label,
            "prediction_available",
            rec["message"],
            None,
        )


def get_label_for_class(class_key: str) -> str:
    """
    Mengembalikan label Bahasa Indonesia untuk kelas tertentu.
    Digunakan oleh test untuk memverifikasi mapping label.
    """
    rec = _CLASS_RECOMMENDATIONS.get(class_key)
    return rec["label"] if rec else class_key
