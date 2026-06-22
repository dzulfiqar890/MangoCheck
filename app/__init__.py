"""
app/__init__.py
Flask application factory untuk MangoCheck.
Mendaftarkan blueprint, CORS, dan error handler global di satu tempat.
"""

import logging
from flask import Flask, jsonify
from flask_cors import CORS

from app.config import Config
from app.routes.health import health_bp
from app.routes.predict import predict_bp
from app.utils.errors import MangoCheckError, ErrorCode


def create_app() -> Flask:
    """
    Membuat dan mengkonfigurasi instance Flask.
    Menggunakan application factory pattern agar mudah di-test dan di-deploy.
    """
    app = Flask(__name__)

    # --- Konfigurasi batas upload Flask ---
    # Flask akan menolak request lebih besar dari nilai ini sebelum mencapai route.
    app.config["MAX_CONTENT_LENGTH"] = Config.MAX_UPLOAD_SIZE_BYTES

    # --- Setup logging ---
    _configure_logging()

    # --- CORS ---
    # CORS dikonfigurasi dari environment variable ALLOWED_ORIGINS.
    # Tidak menggunakan wildcard '*' agar aman di production.
    _configure_cors(app)

    # --- Daftarkan blueprint di bawah prefix /api ---
    app.register_blueprint(health_bp, url_prefix="/api")
    app.register_blueprint(predict_bp, url_prefix="/api")

    # --- Error handler global ---
    _register_error_handlers(app)

    logging.getLogger(__name__).info("MangoCheck API berhasil diinisialisasi.")
    return app


def _configure_cors(app: Flask) -> None:
    """
    Mengaktifkan CORS dengan daftar origin yang diizinkan dari konfigurasi.
    Origins dibaca dari ALLOWED_ORIGINS dan tidak boleh menggunakan wildcard di production.
    """
    allowed_origins = Config.ALLOWED_ORIGINS
    CORS(
        app,
        origins=allowed_origins,
        methods=["GET", "POST", "OPTIONS"],
        allow_headers=["Content-Type"],
    )
    logging.getLogger(__name__).info(
        "CORS diaktifkan untuk origins: %s", allowed_origins
    )


def _configure_logging() -> None:
    """
    Mengkonfigurasi format logging agar error internal tercatat di server log,
    tetapi tidak pernah dikirim ke client.
    """
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )


def _register_error_handlers(app: Flask) -> None:
    """
    Mendaftarkan error handler global untuk memastikan semua error
    dikembalikan dalam format JSON yang konsisten, bukan HTML default Flask.
    Traceback dan detail internal tidak pernah dikirim ke client.
    """
    logger = logging.getLogger(__name__)

    @app.errorhandler(MangoCheckError)
    def handle_mangocheck_error(exc: MangoCheckError):
        """Menangkap semua MangoCheckError yang lolos dari route handler."""
        return jsonify({"success": False, "error": {"code": exc.code, "message": exc.message}}), exc.http_status

    @app.errorhandler(413)
    def handle_request_entity_too_large(exc):
        """Flask otomatis mengembalikan 413 jika MAX_CONTENT_LENGTH terlampaui."""
        return jsonify({
            "success": False,
            "error": {
                "code": ErrorCode.FILE_TOO_LARGE,
                "message": f"Ukuran file melebihi batas maksimum {Config.MAX_UPLOAD_SIZE_MB} MB.",
            }
        }), 413

    @app.errorhandler(404)
    def handle_not_found(exc):
        return jsonify({
            "success": False,
            "error": {
                "code": "NOT_FOUND",
                "message": "Endpoint tidak ditemukan.",
            }
        }), 404

    @app.errorhandler(405)
    def handle_method_not_allowed(exc):
        return jsonify({
            "success": False,
            "error": {
                "code": "METHOD_NOT_ALLOWED",
                "message": "Method HTTP tidak diizinkan untuk endpoint ini.",
            }
        }), 405

    @app.errorhandler(500)
    def handle_internal_error(exc):
        # Log error lengkap di server, tetapi kirim pesan generik ke client.
        logger.error("Internal server error: %s", exc, exc_info=True)
        return jsonify({
            "success": False,
            "error": {
                "code": ErrorCode.INTERNAL_ERROR,
                "message": "Terjadi kesalahan internal pada server. Coba lagi nanti.",
            }
        }), 500
