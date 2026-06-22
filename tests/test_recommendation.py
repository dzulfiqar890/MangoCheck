"""
tests/test_recommendation.py
Pengujian service rekomendasi MangoCheck.

Memastikan:
- Setiap kelas menghasilkan label Bahasa Indonesia yang benar.
- Setiap kelas menghasilkan pesan rekomendasi yang sesuai.
- Confidence rendah menghasilkan status manual_review_required.
- Confidence cukup menghasilkan status prediction_available.
"""

import pytest
from app.services.recommendation_service import get_recommendation, get_label_for_class


class TestRecommendationMapping:
    """Pengujian mapping kelas ke label dan pesan rekomendasi."""

    def test_unripe_label_is_mentah(self):
        """Kelas 'unripe' harus menghasilkan label 'Mentah'."""
        label = get_label_for_class("unripe")
        assert label == "Mentah"

    def test_ripe_label_is_matang(self):
        """Kelas 'ripe' harus menghasilkan label 'Matang'."""
        label = get_label_for_class("ripe")
        assert label == "Matang"

    def test_rotten_label_is_busuk(self):
        """Kelas 'rotten' harus menghasilkan label 'Busuk'."""
        label = get_label_for_class("rotten")
        assert label == "Busuk"

    def test_unripe_recommendation_message(self):
        """Rekomendasi 'unripe' harus menyebutkan menyimpan mangga."""
        _, _, message, _ = get_recommendation("unripe", confidence=0.90)
        assert "Simpan" in message or "mentah" in message.lower()

    def test_ripe_recommendation_message(self):
        """Rekomendasi 'ripe' harus menyebutkan prioritas jual atau konsumsi."""
        _, _, message, _ = get_recommendation("ripe", confidence=0.90)
        assert "dijual" in message or "dikonsumsi" in message

    def test_rotten_recommendation_message(self):
        """Rekomendasi 'rotten' harus menyebutkan memisahkan dari stok."""
        _, _, message, _ = get_recommendation("rotten", confidence=0.90)
        assert "Pisahkan" in message or "busuk" in message.lower()


class TestConfidenceThreshold:
    """Pengujian status rekomendasi berdasarkan nilai confidence."""

    def test_high_confidence_gives_prediction_available(self):
        """Confidence di atas threshold harus menghasilkan 'prediction_available'."""
        _, status, _, manual_note = get_recommendation("ripe", confidence=0.90, threshold=0.70)
        assert status == "prediction_available"
        assert manual_note is None

    def test_low_confidence_gives_manual_review_required(self):
        """Confidence di bawah threshold harus menghasilkan 'manual_review_required'."""
        _, status, _, manual_note = get_recommendation("unripe", confidence=0.50, threshold=0.70)
        assert status == "manual_review_required"
        assert manual_note is not None

    def test_exactly_at_threshold_is_not_low_confidence(self):
        """Confidence tepat sama dengan threshold TIDAK dianggap rendah (gunakan >=)."""
        _, status, _, _ = get_recommendation("ripe", confidence=0.70, threshold=0.70)
        # 0.70 >= 0.70, jadi bukan low confidence
        assert status == "prediction_available"

    def test_just_below_threshold_is_low_confidence(self):
        """Confidence sedikit di bawah threshold dianggap rendah."""
        _, status, _, _ = get_recommendation("ripe", confidence=0.6999, threshold=0.70)
        assert status == "manual_review_required"

    def test_low_confidence_manual_review_note_not_empty(self):
        """Manual review note tidak boleh None atau kosong saat confidence rendah."""
        _, _, _, note = get_recommendation("rotten", confidence=0.40, threshold=0.70)
        assert note is not None
        assert len(note) > 0

    def test_high_confidence_manual_review_note_is_none(self):
        """Manual review note harus None saat confidence cukup tinggi."""
        _, _, _, note = get_recommendation("ripe", confidence=0.95, threshold=0.70)
        assert note is None

    def test_low_confidence_message_contains_caution_language(self):
        """Pesan low confidence harus menggunakan bahasa yang hati-hati (terindikasi)."""
        _, _, message, _ = get_recommendation("unripe", confidence=0.50, threshold=0.70)
        # Pesan harus mengindikasikan ketidakpastian, bukan pernyataan pasti
        assert "terindikasi" in message or "perlu diperiksa" in message

    def test_unripe_low_confidence_returns_correct_label(self):
        """Label tetap harus 'Mentah' meskipun confidence rendah."""
        label, _, _, _ = get_recommendation("unripe", confidence=0.40)
        assert label == "Mentah"

    def test_ripe_low_confidence_returns_correct_label(self):
        """Label tetap harus 'Matang' meskipun confidence rendah."""
        label, _, _, _ = get_recommendation("ripe", confidence=0.40)
        assert label == "Matang"

    def test_rotten_low_confidence_returns_correct_label(self):
        """Label tetap harus 'Busuk' meskipun confidence rendah."""
        label, _, _, _ = get_recommendation("rotten", confidence=0.40)
        assert label == "Busuk"


class TestRecommendationReturnType:
    """Pengujian tipe data nilai yang dikembalikan get_recommendation."""

    def test_returns_four_values(self):
        """Fungsi harus mengembalikan tepat 4 nilai."""
        result = get_recommendation("ripe", confidence=0.90)
        assert len(result) == 4

    def test_label_is_string(self):
        label, _, _, _ = get_recommendation("ripe", confidence=0.90)
        assert isinstance(label, str)

    def test_status_is_string(self):
        _, status, _, _ = get_recommendation("ripe", confidence=0.90)
        assert isinstance(status, str)

    def test_message_is_string(self):
        _, _, message, _ = get_recommendation("ripe", confidence=0.90)
        assert isinstance(message, str)

    def test_status_is_valid_value(self):
        """Status hanya boleh berupa dua nilai yang valid."""
        valid_statuses = {"prediction_available", "manual_review_required"}

        for class_key in ["unripe", "ripe", "rotten"]:
            for confidence in [0.40, 0.75, 0.95]:
                _, status, _, _ = get_recommendation(class_key, confidence)
                assert status in valid_statuses, (
                    f"Status '{status}' tidak valid untuk class '{class_key}' "
                    f"dengan confidence {confidence}"
                )
