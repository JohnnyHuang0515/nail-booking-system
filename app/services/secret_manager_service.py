"""
秘密管理服務
"""
import logging
import os
from typing import Dict, Optional, Any
from uuid import UUID
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
import base64
from sqlalchemy.orm import Session

logger = logging.getLogger(__name__)


class SecretManagerService:
    """秘密管理服務"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.master_key = self._get_or_create_master_key()
        self.cipher_suite = Fernet(self.master_key)
    
    def _get_or_create_master_key(self) -> bytes:
        """取得或創建主密鑰"""
        # 從環境變數讀取主密鑰
        master_key_env = os.getenv("MASTER_ENCRYPTION_KEY")
        
        if master_key_env:
            try:
                return base64.b64decode(master_key_env)
            except Exception:
                logger.warning("環境變數中的主密鑰格式錯誤，使用預設密鑰")
        
        # 使用預設密鑰（在生產環境中應該從安全的密鑰管理系統讀取）
        default_key = b"your-32-byte-secret-key-here!!"  # 32 bytes
        return base64.b64encode(default_key)
    
    def _derive_key_from_password(self, password: str, salt: bytes) -> bytes:
        """從密碼衍生密鑰"""
        kdf = PBKDF2HMAC(
            algorithm=hashes.SHA256(),
            length=32,
            salt=salt,
            iterations=100000,
        )
        key = base64.urlsafe_b64encode(kdf.derive(password.encode()))
        return key
    
    def encrypt_secret(self, secret: str) -> str:
        """加密秘密"""
        try:
            encrypted_bytes = self.cipher_suite.encrypt(secret.encode())
            return base64.b64encode(encrypted_bytes).decode()
        except Exception as e:
            logger.error(f"加密失敗: {e}")
            raise
    
    def decrypt_secret(self, encrypted_secret: str) -> str:
        """解密秘密"""
        try:
            encrypted_bytes = base64.b64decode(encrypted_secret.encode())
            decrypted_bytes = self.cipher_suite.decrypt(encrypted_bytes)
            return decrypted_bytes.decode()
        except Exception as e:
            logger.error(f"解密失敗: {e}")
            raise
    
    def store_merchant_credentials(
        self,
        merchant_id: UUID,
        line_channel_id: str,
        line_channel_secret: str,
        line_channel_access_token: str
    ) -> Dict[str, str]:
        """儲存商家憑證"""
        try:
            encrypted_secret = self.encrypt_secret(line_channel_secret)
            encrypted_token = self.encrypt_secret(line_channel_access_token)
            
            # 在實際環境中，這裡會將加密後的憑證保存到資料庫
            credentials = {
                "merchant_id": str(merchant_id),
                "line_channel_id": line_channel_id,  # Channel ID 不需要加密
                "line_channel_secret": encrypted_secret,
                "line_channel_access_token": encrypted_token,
                "encrypted_at": "2024-01-01T00:00:00Z"
            }
            
            logger.info(f"商家 {merchant_id} 憑證已加密儲存")
            return credentials
            
        except Exception as e:
            logger.error(f"儲存商家憑證失敗: {e}")
            raise
    
    def retrieve_merchant_credentials(self, merchant_id: UUID) -> Dict[str, str]:
        """取得商家憑證"""
        try:
            # 模擬從資料庫讀取加密憑證
            encrypted_credentials = {
                "line_channel_id": "taipei_fashion_channel_1234567890abcdef",
                "line_channel_secret": "encrypted_secret_here",
                "line_channel_access_token": "encrypted_token_here"
            }
            
            # 解密憑證
            decrypted_secret = self.decrypt_secret(encrypted_credentials["line_channel_secret"])
            decrypted_token = self.decrypt_secret(encrypted_credentials["line_channel_access_token"])
            
            return {
                "line_channel_id": encrypted_credentials["line_channel_id"],
                "line_channel_secret": decrypted_secret,
                "line_channel_access_token": decrypted_token
            }
            
        except Exception as e:
            logger.error(f"取得商家憑證失敗: {e}")
            raise
    
    def rotate_merchant_credentials(
        self,
        merchant_id: UUID,
        new_secret: Optional[str] = None,
        new_token: Optional[str] = None
    ) -> Dict[str, str]:
        """輪替商家憑證"""
        try:
            # 取得現有憑證
            current_credentials = self.retrieve_merchant_credentials(merchant_id)
            
            # 使用新憑證或保持現有憑證
            new_secret = new_secret or current_credentials["line_channel_secret"]
            new_token = new_token or current_credentials["line_channel_access_token"]
            
            # 儲存新憑證
            updated_credentials = self.store_merchant_credentials(
                merchant_id=merchant_id,
                line_channel_id=current_credentials["line_channel_id"],
                line_channel_secret=new_secret,
                line_channel_access_token=new_token
            )
            
            logger.info(f"商家 {merchant_id} 憑證已輪替")
            return updated_credentials
            
        except Exception as e:
            logger.error(f"輪替商家憑證失敗: {e}")
            raise
    
    def store_system_secret(self, key: str, value: str) -> str:
        """儲存系統秘密"""
        try:
            encrypted_value = self.encrypt_secret(value)
            logger.info(f"系統秘密 {key} 已加密儲存")
            return encrypted_value
        except Exception as e:
            logger.error(f"儲存系統秘密失敗: {e}")
            raise
    
    def retrieve_system_secret(self, key: str) -> str:
        """取得系統秘密"""
        try:
            # 模擬從資料庫讀取加密秘密
            encrypted_value = "encrypted_system_secret_here"
            decrypted_value = self.decrypt_secret(encrypted_value)
            return decrypted_value
        except Exception as e:
            logger.error(f"取得系統秘密失敗: {e}")
            raise
    
    def delete_merchant_credentials(self, merchant_id: UUID) -> bool:
        """刪除商家憑證"""
        try:
            # 在實際環境中，這裡會從資料庫刪除憑證
            logger.info(f"商家 {merchant_id} 憑證已刪除")
            return True
        except Exception as e:
            logger.error(f"刪除商家憑證失敗: {e}")
            return False
    
    def list_encrypted_secrets(self) -> Dict[str, Any]:
        """列出所有加密秘密"""
        # 模擬列出所有加密秘密
        return {
            "merchant_credentials": [
                {
                    "merchant_id": "1",
                    "line_channel_id": "taipei_fashion_channel_1234567890abcdef",
                    "encrypted_at": "2024-01-01T00:00:00Z"
                },
                {
                    "merchant_id": "2",
                    "line_channel_id": "kaohsiung_art_channel_1234567890abcdef",
                    "encrypted_at": "2024-01-01T00:00:00Z"
                }
            ],
            "system_secrets": [
                {
                    "key": "database_password",
                    "encrypted_at": "2024-01-01T00:00:00Z"
                },
                {
                    "key": "jwt_secret",
                    "encrypted_at": "2024-01-01T00:00:00Z"
                }
            ]
        }
    
    def health_check(self) -> Dict[str, Any]:
        """健康檢查"""
        try:
            # 測試加密解密功能
            test_secret = "test_secret_123"
            encrypted = self.encrypt_secret(test_secret)
            decrypted = self.decrypt_secret(encrypted)
            
            return {
                "status": "healthy",
                "encryption_working": decrypted == test_secret,
                "master_key_available": bool(self.master_key),
                "timestamp": "2024-01-01T00:00:00Z"
            }
        except Exception as e:
            return {
                "status": "unhealthy",
                "error": str(e),
                "timestamp": "2024-01-01T00:00:00Z"
            }
