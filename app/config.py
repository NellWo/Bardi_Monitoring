# app/config.py

import os
from dotenv import load_dotenv

# Memuat variabel lingkungan dari file .env
load_dotenv()

class Config:
    # Tuya Cloud Credentials (WAJIB DIAMBIL DARI .env)
    TUYA_ACCESS_ID = os.getenv('h5m35truajwuhpfgwqq3')
    TUYA_SECRET_KEY = os.getenv('2a50b6e87837441ca5b21ace9fa43c55')
    TUYA_REGION = os.getenv('sg')
    TUYA_DEVICE_ID = os.getenv('72838210e09806dd2286')

    # Konfigurasi Database (SQLite)
    DATABASE_FILE = 'bardi.db'
    SQLALCHEMY_DATABASE_URI = f'sqlite:///{DATABASE_FILE}'
    SQLALCHEMY_TRACK_MODIFICATIONS = False