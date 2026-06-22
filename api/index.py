"""
api/index.py
Entry point untuk deployment Vercel (Serverless Function).
Vercel mencari file ini berdasarkan konfigurasi vercel.json.

Catatan cold start:
Pada deployment serverless, instance baru dibuat saat tidak ada request aktif.
Request pertama setelah idle akan lebih lambat karena Flask app dan model TFLite
perlu dimuat dari awal. Ini adalah perilaku normal serverless, bukan bug.
"""

import sys
import os

# Tambahkan root project ke sys.path agar import package app/ berfungsi
# ketika Vercel menjalankan file ini dari direktori api/.
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from app import create_app

# Buat aplikasi Flask — variabel ini digunakan Vercel sebagai WSGI callable.
app = create_app()

# Untuk kompatibilitas Vercel Python runtime yang mengharapkan nama 'app'
# atau 'handler'. Tidak perlu mengubah nama jika vercel.json sudah dikonfigurasi.
