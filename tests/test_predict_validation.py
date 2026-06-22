"""
tests/test_predict_validation.py
Pengujian validasi upload endpoint POST /api/predict.

Semua kasus error diuji tanpa membutuhkan model asli.
Model di-mock sehingga test berjalan di environment apapun.
"""

import io
import pytest
from unittest.mock import patch
from PIL import Image
from app import create_app


@pytest.fixture
def client():
    """Membuat test client Flask untuk pengujian."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


def _make_valid_jpeg_bytes(width: int = 100, height: int = 100) -> bytes:
    """Membuat bytes JPEG valid untuk pengujian menggunakan Pillow."""
    img = Image.new("RGB", (width, height), color=(100, 150, 200))
    buf = io.BytesIO()
    img.save(buf, format="JPEG")
    buf.seek(0)
    return buf.read()


def _make_valid_png_bytes() -> bytes:
    """Membuat bytes PNG valid untuk pengujian."""
    img = Image.new("RGB", (50, 50), color=(200, 100, 50))
    buf = io.BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf.read()


class TestPredictValidation:
    """Pengujian validasi input endpoint POST /api/predict."""

    def test_no_image_field_returns_400(self, client):
        """POST tanpa field 'image' harus mengembalikan 400."""
        response = client.post("/api/predict", data={})
        assert response.status_code == 400
        data = response.get_json()
        assert data["success"] is False
        assert data["error"]["code"] == "NO_IMAGE_FIELD"

    def test_empty_filename_returns_400(self, client):
        """Upload file dengan nama kosong harus mengembalikan 400."""
        data = {"image": (io.BytesIO(b""), "")}
        response = client.post(
            "/api/predict",
            data=data,
            content_type="multipart/form-data",
        )
        assert response.status_code == 400
        data_json = response.get_json()
        assert data_json["success"] is False

    def test_text_file_returns_error(self, client):
        """Upload file teks (bukan gambar) harus menghasilkan error validasi."""
        text_bytes = b"Ini bukan gambar, hanya teks biasa."
        data = {"image": (io.BytesIO(text_bytes), "test.txt", "text/plain")}
        response = client.post(
            "/api/predict",
            data=data,
            content_type="multipart/form-data",
        )
        # Harus error (400 atau 415), bukan 200
        assert response.status_code in (400, 415)
        resp_json = response.get_json()
        assert resp_json["success"] is False

    def test_corrupt_image_returns_400(self, client):
        """Upload gambar rusak (header JPEG palsu) harus mengembalikan 400."""
        # Bytes yang dimulai dengan magic bytes JPEG tapi sisanya rusak
        fake_jpeg = b"\xff\xd8\xff\xe0" + b"\x00" * 50 + b"corrupt_data_here"
        data = {"image": (io.BytesIO(fake_jpeg), "corrupt.jpg", "image/jpeg")}
        response = client.post(
            "/api/predict",
            data=data,
            content_type="multipart/form-data",
        )
        assert response.status_code == 400
        resp_json = response.get_json()
        assert resp_json["success"] is False

    def test_file_too_large_returns_413(self, client):
        """Upload file lebih dari batas ukuran harus mengembalikan 413."""
        # Buat data lebih besar dari 4 MB (batas default)
        large_data = b"X" * (5 * 1024 * 1024)  # 5 MB
        data = {"image": (io.BytesIO(large_data), "large.jpg", "image/jpeg")}
        response = client.post(
            "/api/predict",
            data=data,
            content_type="multipart/form-data",
        )
        assert response.status_code == 413
        resp_json = response.get_json()
        assert resp_json["success"] is False
        assert resp_json["error"]["code"] == "FILE_TOO_LARGE"

    def test_unsupported_format_gif_returns_415(self, client):
        """Upload gambar GIF (format tidak didukung) harus mengembalikan 415."""
        # Buat GIF valid menggunakan Pillow
        img = Image.new("RGB", (10, 10), color=(0, 255, 0))
        buf = io.BytesIO()
        img.save(buf, format="GIF")
        buf.seek(0)

        data = {"image": (buf, "image.gif", "image/gif")}
        response = client.post(
            "/api/predict",
            data=data,
            content_type="multipart/form-data",
        )
        assert response.status_code == 415
        resp_json = response.get_json()
        assert resp_json["success"] is False
        assert resp_json["error"]["code"] == "UNSUPPORTED_FORMAT"

    def test_model_not_available_returns_503(self, client):
        """
        Ketika model belum tersedia, endpoint prediksi harus mengembalikan 503.
        Upload gambar valid tetap dilakukan, tetapi model di-mock sebagai tidak tersedia.
        """
        from app.utils.errors import ModelNotAvailableError

        valid_jpeg = _make_valid_jpeg_bytes()
        data = {"image": (io.BytesIO(valid_jpeg), "mango.jpg", "image/jpeg")}

        with patch(
            "app.services.model_service.predict",
            side_effect=ModelNotAvailableError(),
        ):
            response = client.post(
                "/api/predict",
                data=data,
                content_type="multipart/form-data",
            )

        assert response.status_code == 503
        resp_json = response.get_json()
        assert resp_json["success"] is False
        assert resp_json["error"]["code"] == "MODEL_NOT_AVAILABLE"

    def test_valid_jpeg_reaches_model(self, client):
        """
        Upload JPEG valid harus berhasil melewati validasi dan mencapai model.
        Model di-mock untuk mengembalikan hasil prediksi.
        """
        valid_jpeg = _make_valid_jpeg_bytes()
        data = {"image": (io.BytesIO(valid_jpeg), "mango.jpg", "image/jpeg")}

        with patch(
            "app.services.model_service.predict",
            return_value=("ripe", 0.9234),
        ):
            response = client.post(
                "/api/predict",
                data=data,
                content_type="multipart/form-data",
            )

        assert response.status_code == 200
        resp_json = response.get_json()
        assert resp_json["success"] is True

    def test_valid_png_reaches_model(self, client):
        """Upload PNG valid harus berhasil melewati validasi."""
        valid_png = _make_valid_png_bytes()
        data = {"image": (io.BytesIO(valid_png), "mango.png", "image/png")}

        with patch(
            "app.services.model_service.predict",
            return_value=("unripe", 0.8100),
        ):
            response = client.post(
                "/api/predict",
                data=data,
                content_type="multipart/form-data",
            )

        assert response.status_code == 200
        resp_json = response.get_json()
        assert resp_json["success"] is True

    def test_error_response_structure(self, client):
        """Format error harus selalu memiliki success=false dan error.code."""
        response = client.post("/api/predict", data={})
        resp_json = response.get_json()

        assert "success" in resp_json
        assert resp_json["success"] is False
        assert "error" in resp_json
        assert "code" in resp_json["error"]
        assert "message" in resp_json["error"]

    def test_no_traceback_in_error_response(self, client):
        """Traceback Python tidak boleh bocor ke respons client."""
        response = client.post("/api/predict", data={})
        resp_text = response.get_data(as_text=True)

        assert "Traceback" not in resp_text
        assert "File \"" not in resp_text
        assert "line " not in resp_text.lower() or "Traceback" not in resp_text
