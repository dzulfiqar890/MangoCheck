"""
run_local.py
Script untuk menjalankan MangoCheck API secara lokal dalam mode development.
Jangan gunakan script ini untuk production deployment.
"""

import os
from dotenv import load_dotenv

# Muat environment variable dari file .env jika tersedia
load_dotenv()

from app import create_app
from app.config import Config

if __name__ == "__main__":
    app = create_app()

    print("=" * 55)
    print("  MangoCheck API — Local Development Server")
    print("=" * 55)
    print(f"  Host   : {Config.FLASK_HOST}")
    print(f"  Port   : {Config.FLASK_PORT}")
    print(f"  Debug  : {Config.FLASK_DEBUG}")
    print(f"  Model  : {Config.MODEL_PATH}")
    print("-" * 55)
    print("  Endpoints:")
    print(f"    GET  http://localhost:{Config.FLASK_PORT}/api/health")
    print(f"    POST http://localhost:{Config.FLASK_PORT}/api/predict")
    print("=" * 55)
    print()

    app.run(
        host=Config.FLASK_HOST,
        port=Config.FLASK_PORT,
        debug=Config.FLASK_DEBUG,
    )
