# app/models.py
from pydantic import BaseModel
from typing import Optional, List
from datetime import datetime

class SwitchStatus(BaseModel):
    name: str
    status: bool
    code: str

class DeviceInfo(BaseModel):
    device_id: str
    product_name: str
    ip_address: str
    online_status: str
    last_updated: datetime

class LogEntry(BaseModel):
    switch_name: str
    status: bool
    created_at: datetime

class APIResponse(BaseModel):
    success: bool
    message: Optional[str] = None
    error: Optional[str] = None
    data: Optional[dict] = None