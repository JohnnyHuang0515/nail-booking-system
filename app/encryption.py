"""
敏感資料加密存儲管理
"""
import os
import base64
from cryptography.fernet import Fernet
from cryptography.hazmat.primitives import hashes
from cryptography.hazmat.primitives.kdf.pbkdf2 import PBKDF2HMAC
from typing import Optional
import logging

logger = logging.getLogger(__name__)


class EncryptionManager:
    """加密管理器"""
    
    def __init__(self, password: Optional[str] = None):
        """
        初始化加密管理器
        
        Args:
            password: 加密密碼，如果不提供則從環境變數取得
        """
        self.password = password or os.getenv("ENCRYPTION_KEY", "default-encryption-key")
        self._fernet = None
        self._initialize_fernet()
    
    def _initialize_fernet(self):
        """初始化 Fernet 加密器"""
        try:
            # 從密碼生成金鑰
            salt = b'nail_booking_salt_2024'  # 固定鹽值，生產環境應使用隨機鹽值
            kdf = PBKDF2HMAC(
                algorithm=hashes.SHA256(),
                length=32,
                salt=salt,
                iterations=100000,
            )
            key = base64.urlsafe_b64encode(kdf.derive(self.password.encode()))
            self._fernet = Fernet(key)
            
        except Exception as e:
            logger.error(f"初始化加密器失敗: {str(e)}")
            raise
    
    def encrypt(self, data: str) -> str:
        """
        加密字串資料
        
        Args:
            data: 要加密的字串
            
        Returns:
            str: 加密後的字串（Base64 編碼）
        """
        try:
            if not data:
                return ""
            
            encrypted_data = self._fernet.encrypt(data.encode())
            return base64.urlsafe_b64encode(encrypted_data).decode()
            
        except Exception as e:
            logger.error(f"加密資料失敗: {str(e)}")
            raise
    
    def decrypt(self, encrypted_data: str) -> str:
        """
        解密字串資料
        
        Args:
            encrypted_data: 加密的字串（Base64 編碼）
            
        Returns:
            str: 解密後的字串
        """
        try:
            if not encrypted_data:
                return ""
            
            # 解碼 Base64
            encrypted_bytes = base64.urlsafe_b64decode(encrypted_data.encode())
            
            # 解密
            decrypted_data = self._fernet.decrypt(encrypted_bytes)
            return decrypted_data.decode()
            
        except Exception as e:
            logger.error(f"解密資料失敗: {str(e)}")
            raise
    
    def encrypt_dict(self, data_dict: dict, fields_to_encrypt: list) -> dict:
        """
        加密字典中的指定欄位
        
        Args:
            data_dict: 要處理的字典
            fields_to_encrypt: 需要加密的欄位列表
            
        Returns:
            dict: 處理後的字典
        """
        result = data_dict.copy()
        
        for field in fields_to_encrypt:
            if field in result and result[field]:
                result[field] = self.encrypt(str(result[field]))
        
        return result
    
    def decrypt_dict(self, data_dict: dict, fields_to_decrypt: list) -> dict:
        """
        解密字典中的指定欄位
        
        Args:
            data_dict: 要處理的字典
            fields_to_decrypt: 需要解密的欄位列表
            
        Returns:
            dict: 處理後的字典
        """
        result = data_dict.copy()
        
        for field in fields_to_decrypt:
            if field in result and result[field]:
                try:
                    result[field] = self.decrypt(str(result[field]))
                except Exception as e:
                    logger.warning(f"解密欄位 {field} 失敗: {str(e)}")
                    # 如果解密失敗，保留原值（可能是未加密的資料）
                    pass
        
        return result


class TokenEncryptionManager:
    """Token 加密管理器 - 專門處理 LINE Access Token 加密"""
    
    def __init__(self):
        self.encryption_manager = EncryptionManager()
        self.encrypted_fields = [
            'line_channel_access_token',
            'line_channel_secret'
        ]
    
    def encrypt_merchant_tokens(self, merchant_data: dict) -> dict:
        """
        加密商家 Token 資料
        
        Args:
            merchant_data: 商家資料字典
            
        Returns:
            dict: 加密後的商家資料
        """
        return self.encryption_manager.encrypt_dict(
            merchant_data, 
            self.encrypted_fields
        )
    
    def decrypt_merchant_tokens(self, merchant_data: dict) -> dict:
        """
        解密商家 Token 資料
        
        Args:
            merchant_data: 商家資料字典
            
        Returns:
            dict: 解密後的商家資料
        """
        return self.encryption_manager.decrypt_dict(
            merchant_data, 
            self.encrypted_fields
        )
    
    def encrypt_access_token(self, access_token: str) -> str:
        """加密 Access Token"""
        return self.encryption_manager.encrypt(access_token)
    
    def decrypt_access_token(self, encrypted_token: str) -> str:
        """解密 Access Token"""
        return self.encryption_manager.decrypt(encrypted_token)


# 全域實例
encryption_manager = EncryptionManager()
token_encryption_manager = TokenEncryptionManager()


# 使用範例和測試
def test_encryption():
    """測試加密功能"""
    test_data = "test_line_access_token_1234567890"
    
    # 測試加密
    encrypted = encryption_manager.encrypt(test_data)
    print(f"原始資料: {test_data}")
    print(f"加密後: {encrypted}")
    
    # 測試解密
    decrypted = encryption_manager.decrypt(encrypted)
    print(f"解密後: {decrypted}")
    
    # 驗證結果
    assert test_data == decrypted, "加密解密測試失敗"
    print("✅ 加密解密測試通過")
    
    # 測試字典加密
    test_dict = {
        "name": "測試商家",
        "line_channel_access_token": "test_token_123",
        "line_channel_secret": "test_secret_456"
    }
    
    encrypted_dict = token_encryption_manager.encrypt_merchant_tokens(test_dict)
    print(f"加密前: {test_dict}")
    print(f"加密後: {encrypted_dict}")
    
    decrypted_dict = token_encryption_manager.decrypt_merchant_tokens(encrypted_dict)
    print(f"解密後: {decrypted_dict}")
    
    assert test_dict == decrypted_dict, "字典加密解密測試失敗"
    print("✅ 字典加密解密測試通過")


if __name__ == "__main__":
    test_encryption()
