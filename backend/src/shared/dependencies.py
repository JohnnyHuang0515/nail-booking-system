"""
Shared Dependencies
FastAPI 共享依賴
"""
from sqlalchemy.orm import Session
from shared.database import get_db

# 重新導出 get_db 以便其他模組使用
__all__ = ["get_db"]
