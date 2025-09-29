# app/tuya_api.py

import os
from datetime import datetime
import pytz
from tuya_iot import TuyaOpenAPI, AuthType
from app.config import Config

# --- KONFIGURASI API TUYA ---
URL_BASE = f"https://openapi.tuya-cn.com" # Ganti jika region non-sg
ACCESS_ID = Config.TUYA_ACCESS_ID
ACCESS_SECRET = Config.TUYA_SECRET_KEY
DEVICE_ID = Config.TUYA_DEVICE_ID
REGION = Config.TUYA_REGION

# Mapping DPID (Asumsi Smart Socket 5 Gang + USB)
# **INI HARUS DICEK ULANG DI PLATFORM TUYA (Device Debugging)**
DPID_MAPPING = {
    'Switch 1': '1', 
    'Switch 2': '2', 
    'Switch 3': '3', 
    'Switch 4': '4', 
    'Switch 5': '5', 
    'USB_Switch': '7', # DPID yang umum untuk kontrol USB
    'Current_A': '18', # Untuk nilai arus
    'Power_W': '20',  # Untuk nilai daya (Watt)
    'Voltage_V': '19', # Untuk nilai tegangan (Volt)
}
# Perangkat multi-gang Bardi sering menggunakan DPID berurutan 1, 2, 3, 4, 5.
# Jika status 2 dan 4 salah, coba cek apakah DPID-nya ternyata 20 dan 22, lalu ubah di atas.
# Contoh: 'Switch 2': '20',

# --- INISIASI TUYA API ---
openapi = TuyaOpenAPI(URL_BASE, ACCESS_ID, ACCESS_SECRET)
openapi.set_dev_channel("default") # Tambahkan ini jika ada masalah otorisasi

def get_tuya_client():
    """Mendapatkan klien Tuya dan melakukan otorisasi (token)"""
    # Otentikasi dan dapatkan token akses
    try:
        if openapi.is_access_token_expired():
            print("Token Tuya kedaluwarsa, mencoba mendapatkan yang baru...")
            openapi.connect()
        return openapi
    except Exception as e:
        print(f"Gagal koneksi atau otorisasi Tuya: {e}")
        return None

# --- FUNGSI UTILITY WAKTU ---
def convert_utc_to_wib(utc_time_str):
    """Mengkonversi waktu dari string UTC ke WIB."""
    time_format = '%Y-%m-%d %H:%M:%S'
    
    try:
        # Menambahkan 'Z' di akhir untuk menandakan UTC jika Tuya mengembalikan format ISO
        if 'T' in utc_time_str and 'Z' in utc_time_str:
             utc_time_obj = datetime.strptime(utc_time_str.split('.')[0], '%Y-%m-%dT%H:%M:%S')
        else:
             utc_time_obj = datetime.strptime(utc_time_str, time_format)

        utc_time_localized = pytz.utc.localize(utc_time_obj)
        wib_tz = pytz.timezone('Asia/Jakarta')
        wib_time = utc_time_localized.astimezone(wib_tz)
        
        return wib_time.strftime('%Y-%m-%d %H:%M:%S')
        
    except Exception as e:
        # Jika waktu dari DB/Tuya tidak dalam format yang diharapkan, gunakan waktu saat ini
        now_wib = datetime.now(pytz.timezone('Asia/Jakarta'))
        return now_wib.strftime('%Y-%m-%d %H:%M:%S')


# --- FUNGSI UTAMA PENGAMBIL DATA ---
def fetch_device_status(device_id=DEVICE_ID):
    """Mengambil status real-time dari Tuya Cloud."""
    client = get_tuya_client()
    if not client:
        return None, "Koneksi ke Tuya Cloud gagal."

    # Endpoint untuk mendapatkan status device
    endpoint = f'/v1.0/devices/{device_id}/status' 
    response = client.get(endpoint)
    
    if response and response.get('success'):
        # Data berhasil diambil dari Tuya Cloud
        return response.get('result'), "Data berhasil diambil."
    else:
        # Gagal mengambil data
        error_msg = response.get('msg', 'Respon Tuya Cloud tidak sukses.')
        print(f"Error Tuya API: {error_msg}")
        return None, error_msg

def process_tuya_data(tuya_result):
    """Memproses data mentah Tuya (DPID) menjadi format dashboard."""
    if not tuya_result:
        return None

    # Mengambil status dari respons
    raw_status = {item['code']: item['value'] for item in tuya_result}
    
    processed_status = {
        'timestamp_utc': datetime.utcnow().strftime('%Y-%m-%d %H:%M:%S'), # Waktu saat ini (sebagai fallback)
        'switches': {}
    }
    
    # Memetakan dan mengkonversi DPID
    for switch_name, dpid in DPID_MAPPING.items():
        value = raw_status.get(dpid)
        
        if 'Switch' in switch_name or 'USB' in switch_name:
            # Konversi nilai Boolean (True/False) ke ON/OFF
            status = "ON" if value is True else "OFF"
            processed_status['switches'][switch_name] = status
        
        # Konversi nilai daya (asumsi Tuya memberikan nilai daya dalam Watt/Ampere/Volt)
        elif 'Power' in switch_name:
            # Tuya sering memberikan nilai daya dalam mili-unit (mW, mA, mV). 
            # Jika '20' adalah mW, bagi 1000. Cek di dokumentasi/debug Tuya.
            processed_status[switch_name] = round(value / 1000, 2) if isinstance(value, (int, float)) and value > 1000 else value
        else:
             processed_status[switch_name] = value

    return processed_status