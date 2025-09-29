# app/main.py

from flask import Flask, render_template, jsonify, request
from app.config import Config
from app.tuya_api import fetch_device_status, process_tuya_data, convert_utc_to_wib
from app.db import db # Asumsi kamu sudah setup SQLAlchemy/sqlite

# Setup Flask
app = Flask(__name__)
app.config.from_object(Config)

# --- INI HARUS ADA DI FOLDER APP/db.py ATAU DI SINI ---
# db.init_app(app) 
# with app.app_context():
#     db.create_all()
# ---

# Fungsi untuk menyimpan riwayat (ASUMSI MODEL KAMU)
def log_status(data):
    # Logika untuk menyimpan data ke bardi.db (SQLite)
    # Gunakan data['timestamp_utc'] dan data['switches']
    print(f"Logging data ke DB: {data}")
    # ... (Di sini kamu tambahkan kode untuk INSERT ke tabel riwayat)
    pass 

def get_last_logs():
    # Logika untuk mengambil 10 log terakhir dari DB
    # ...
    # Contoh data dummy (ganti dengan query DB yang sebenarnya)
    return [
        {'time': '2025-09-29 12:40:00', 'switch': 'Switch 1', 'status': 'ON'},
        {'time': '2025-09-29 12:40:00', 'switch': 'Switch 2', 'status': 'OFF'},
    ]

# --- ROUTE UTAMA ---
@app.route('/')
def dashboard():
    # 1. Ambil status terbaru dari Tuya Cloud
    raw_result, msg = fetch_device_status()
    current_data = process_tuya_data(raw_result)

    # 2. Ambil riwayat dari DB (WIB)
    history_logs = get_last_logs() 
    
    # 3. Konversi waktu update (jika ada) ke WIB
    update_time_wib = convert_utc_to_wib(current_data.get('timestamp_utc', ''))
    
    return render_template(
        'dashboard.html',
        device_id=Config.TUYA_DEVICE_ID,
        device_name="Bardi Power Strip",
        status_online="Online" if raw_result else "Offline",
        last_update=update_time_wib,
        switches=current_data.get('switches', {}),
        history=history_logs
    )

# --- ROUTE UPDATE (API yang dipanggil tombol "Update Data Sekarang") ---
@app.route('/update', methods=['POST'])
def update_data():
    # 1. Ambil status terbaru dari Tuya Cloud
    raw_result, msg = fetch_device_status()
    
    if raw_result is None:
        return jsonify({
            "success": False,
            "message": f"Update gagal: {msg}",
            "error": msg,
            "data": None
        })

    # 2. Proses data, konversi DPID, konversi waktu (WIB)
    current_data = process_tuya_data(raw_result)
    
    # 3. Log ke database (simpan riwayat)
    log_status(current_data)

    # 4. Ambil waktu update WIB (untuk notifikasi di frontend)
    update_time_wib = convert_utc_to_wib(current_data.get('timestamp_utc', ''))

    # 5. KEMBALIKAN DATA SWITCHES DAN WAKTU YANG SUDAH DIPROSES
    return jsonify({
        "success": True,
        "message": "Data berhasil diperbarui!",
        "error": None,
        "data": {
            "switches": current_data.get('switches'),
            "update_time": update_time_wib,
            # Tambahkan data daya jika kamu ingin update di frontend
            "power": current_data.get('Power_W', 'N/A')
        }
    })