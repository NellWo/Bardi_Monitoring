# app/db.py
import sqlite3
from contextlib import contextmanager
from datetime import datetime
from typing import List, Optional, Dict, Any
from app.models import DeviceInfo, LogEntry
from datetime import datetime, timedelta

DB_NAME = "bardi.db"

@contextmanager
def get_db():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row  # Return dictionary-like rows
    try:
        yield conn
    finally:
        conn.close()

def init_db():
    """Initialize database dengan tabel yang diperlukan"""
    with get_db() as conn:
        cursor = conn.cursor()
        
        # Create tables
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_logs (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT NOT NULL,
                switch_name TEXT NOT NULL,
                status TEXT NOT NULL,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS device_info (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                device_id TEXT UNIQUE NOT NULL,
                product_name TEXT,
                ip_address TEXT,
                online_status TEXT,
                last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)
        
        # Create indexes
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_device_logs_created_at 
            ON device_logs(created_at DESC)
        """)
        
        cursor.execute("""
            CREATE INDEX IF NOT EXISTS idx_device_logs_switch 
            ON device_logs(switch_name, created_at DESC)
        """)
        
        conn.commit()
    print("Database initialized successfully")

def save_device_info(device_id: str, product_name: str, ip_address: str, online_status: str):
    """Simpan informasi device"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT OR REPLACE INTO device_info 
            (device_id, product_name, ip_address, online_status, last_updated)
            VALUES (?, ?, ?, ?, datetime('now'))
        """, (device_id, product_name, ip_address, online_status))
        conn.commit()

def save_switch_log(device_id: str, switch_name: str, status: bool):
    """Simpan log status switch"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO device_logs (device_id, switch_name, status)
            VALUES (?, ?, ?)
        """, (device_id, switch_name, str(status).lower()))
        conn.commit()

def get_device_info() -> Optional[DeviceInfo]:
    """Ambil informasi device terbaru"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT device_id, product_name, ip_address, online_status, last_updated 
            FROM device_info 
            ORDER BY last_updated DESC 
            LIMIT 1
        """)
        row = cursor.fetchone()
        
        if row:
            return DeviceInfo(
                device_id=row["device_id"],
                product_name=row["product_name"],
                ip_address=row["ip_address"],
                online_status=row["online_status"],
                last_updated=row["last_updated"]
            )
        return None

def get_switch_logs(limit: int = 20) -> List[LogEntry]:
    """Ambil riwayat log switch"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT switch_name, status, created_at 
            FROM device_logs 
            ORDER BY created_at DESC 
            LIMIT ?
        """, (limit,))
        rows = cursor.fetchall()
        
        return [
            LogEntry(
                switch_name=row["switch_name"],
                status=row["status"] == 'true',
                created_at=row["created_at"]
            ) for row in rows
        ]

def get_current_switches() -> List[LogEntry]:
    """Ambil status terbaru setiap switch"""
    with get_db() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            SELECT dl.switch_name, dl.status, MAX(dl.created_at) as created_at
            FROM device_logs dl
            INNER JOIN (
                SELECT switch_name, MAX(created_at) as max_date
                FROM device_logs
                GROUP BY switch_name
            ) latest ON dl.switch_name = latest.switch_name AND dl.created_at = latest.max_date
            GROUP BY dl.switch_name
            ORDER BY dl.switch_name
        """)
        rows = cursor.fetchall()
        
        return [
            LogEntry(
                switch_name=row["switch_name"],
                status=row["status"] == 'true',
                created_at=row["created_at"]
            ) for row in rows
        ]


def sync_switch_logs(device_id: str, logs: List[Dict[str, Any]]):
    """Sync Tuya device logs to local DB, inserting only new events"""
    with get_db() as conn:
        cursor = conn.cursor()
        inserted_count = 0
        for log in logs:
            switch_name = log["switch_name"]
            status = str(log["status"]).lower()
            created_at = log["created_at"]
            created_at_str = created_at.strftime('%Y-%m-%d %H:%M:%S')
            
            # Check if this log already exists (within 1 second tolerance)
            cursor.execute("""
                SELECT COUNT(*) FROM device_logs 
                WHERE switch_name = ? AND status = ? AND 
                created_at >= datetime(?, '-1 second') AND created_at <= datetime(?, '+1 second')
            """, (switch_name, status, created_at_str, created_at_str))
            
            if cursor.fetchone()[0] == 0:
                # Insert new log
                cursor.execute("""
                    INSERT INTO device_logs (device_id, switch_name, status, created_at)
                    VALUES (?, ?, ?, ?)
                """, (device_id, switch_name, status, created_at_str))
                inserted_count += 1
        
        conn.commit()
        print(f"[DB] Synced {inserted_count} new log entries")
