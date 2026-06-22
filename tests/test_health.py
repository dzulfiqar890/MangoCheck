"""
tests/test_health.py
Pengujian endpoint GET /api/health.

Memastikan:
- Endpoint selalu mengembalikan HTTP 200.
- Format JSON sesuai kontrak API.
- Endpoint tetap berjalan ketika model belum tersedia (model_loaded: false).
"""

import pytest
from unittest.mock import patch
from app import create_app


@pytest.fixture
def client():
    """Membuat test client Flask tanpa memulai server sungguhan."""
    app = create_app()
    app.config["TESTING"] = True
    with app.test_client() as client:
        yield client


class TestHealthEndpoint:
    """Pengujian endpoint GET /api/health."""

    def test_health_returns_200(self, client):
        """Health check harus selalu mengembalikan HTTP 200."""
        response = client.get("/api/health")
        assert response.status_code == 200

    def test_health_response_structure(self, client):
        """Respons harus mengikuti kontrak API: success, message, data."""
        response = client.get("/api/health")
        data = response.get_json()

        assert data is not None, "Respons harus berupa JSON"
        assert "success" in data
        assert "message" in data
        assert "data" in data

    def test_health_success_is_true(self, client):
        """Field 'success' harus bernilai True meskipun model belum ada."""
        response = client.get("/api/health")
        data = response.get_json()
        assert data["success"] is True

    def test_health_message_content(self, client):
        """Pesan harus menyertakan identitas API."""
        response = client.get("/api/health")
        data = response.get_json()
        assert "MangoCheck" in data["message"]

    def test_health_data_has_service_field(self, client):
        """Field 'data' harus memiliki field 'service'."""
        response = client.get("/api/health")
        data = response.get_json()
        assert "service" in data["data"]
        assert data["data"]["service"] == "mangocheck-api"

    def test_health_data_has_model_loaded_field(self, client):
        """Field 'data' harus memiliki field 'model_loaded' bertipe boolean."""
        response = client.get("/api/health")
        data = response.get_json()
        assert "model_loaded" in data["data"]
        assert isinstance(data["data"]["model_loaded"], bool)

    def test_health_returns_200_when_model_not_available(self, client):
        """
        Jika model belum tersedia, health check tetap harus mengembalikan 200.
        model_loaded harus false, bukan error.
        """
        with patch("app.services.model_service.is_model_loaded", return_value=False):
            response = client.get("/api/health")
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["model_loaded"] is False

    def test_health_returns_200_when_model_available(self, client):
        """
        Jika model tersedia, health check harus mengembalikan 200
        dengan model_loaded bernilai true.
        """
        with patch("app.services.model_service.is_model_loaded", return_value=True):
            response = client.get("/api/health")
            assert response.status_code == 200
            data = response.get_json()
            assert data["success"] is True
            assert data["data"]["model_loaded"] is True

    def test_health_content_type_is_json(self, client):
        """Respons harus memiliki Content-Type application/json."""
        response = client.get("/api/health")
        assert "application/json" in response.content_type
