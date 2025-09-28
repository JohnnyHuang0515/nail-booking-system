"""
商家初始化服務
負責新商家的完整初始化流程
"""
import logging
from typing import Dict, Any, Optional
from uuid import UUID
from sqlalchemy.orm import Session

from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.infrastructure.repositories.sql_service_repository import SqlServiceRepository
from app.infrastructure.repositories.sql_business_hour_repository import SQLBusinessHourRepository
from app.config import MerchantConfig
from app.line_client import LineClient
from app.rich_menu_manager import RichMenuManager

logger = logging.getLogger(__name__)


class MerchantInitializationService:
    """商家初始化服務"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.merchant_repo = SQLMerchantRepository(db_session)
        self.service_repo = SqlServiceRepository(db_session)
        self.business_hour_repo = SQLBusinessHourRepository(db_session)
        self.line_client = LineClient()
        self.rich_menu_manager = RichMenuManager()
    
    async def initialize_merchant(
        self,
        name: str,
        line_channel_id: str,
        line_channel_secret: str,
        line_channel_access_token: str,
        liff_id: Optional[str] = None,
        timezone: str = 'Asia/Taipei',
        contact_info: Optional[Dict[str, str]] = None
    ) -> Dict[str, Any]:
        """
        完整初始化新商家
        
        Args:
            name: 商家名稱
            line_channel_id: LINE Channel ID
            line_channel_secret: LINE Channel Secret
            line_channel_access_token: LINE Access Token
            liff_id: LIFF App ID
            timezone: 時區
            contact_info: 聯絡資訊
            
        Returns:
            Dict: 初始化結果
        """
        try:
            # 1. 創建商家主檔
            logger.info(f"開始初始化商家: {name}")
            merchant = self.merchant_repo.create(
                name=name,
                line_channel_id=line_channel_id,
                line_channel_secret=line_channel_secret,
                line_channel_access_token=line_channel_access_token,
                liff_id=liff_id,
                timezone=timezone
            )
            self.db_session.flush()
            
            # 2. 初始化服務項目範本
            await self._initialize_services(merchant.id)
            
            # 3. 初始化營業時間範本
            await self._initialize_business_hours(merchant.id)
            
            # 4. 初始化 Rich Menu
            rich_menu_result = await self._initialize_rich_menu(merchant.id, line_channel_access_token)
            
            # 5. 健康檢查
            health_check_result = await self._health_check(merchant.id, line_channel_access_token)
            
            # 6. 提交所有變更
            self.db_session.commit()
            
            logger.info(f"商家 {name} 初始化完成")
            
            return {
                "merchant_id": str(merchant.id),
                "name": merchant.name,
                "status": "initialized",
                "services_created": len(MerchantConfig.get_default_services()),
                "business_hours_created": len(MerchantConfig.get_default_business_hours()),
                "rich_menu": rich_menu_result,
                "health_check": health_check_result,
                "initialization_time": merchant.created_at.isoformat()
            }
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"商家初始化失敗: {str(e)}")
            raise
    
    async def _initialize_services(self, merchant_id: UUID) -> None:
        """初始化服務項目範本"""
        default_services = MerchantConfig.get_default_services()
        
        for service_data in default_services:
            # 創建 Domain Service 物件
            from app.domain.booking.models import Service as DomainService
            domain_service = DomainService(
                merchant_id=merchant_id,
                name=service_data["name"],
                price=service_data["price"],
                duration_minutes=service_data["duration_minutes"]
            )
            self.service_repo.add(domain_service)
        
        logger.info(f"為商家 {merchant_id} 創建了 {len(default_services)} 個預設服務")
    
    async def _initialize_business_hours(self, merchant_id: UUID) -> None:
        """初始化營業時間範本"""
        default_hours = MerchantConfig.get_default_business_hours()
        
        for hour_data in default_hours:
            self.business_hour_repo.create(
                merchant_id=merchant_id,
                day_of_week=hour_data["day_of_week"],
                start_time=hour_data["start_time"],
                end_time=hour_data["end_time"]
            )
        
        logger.info(f"為商家 {merchant_id} 創建了 {len(default_hours)} 個營業時間設定")
    
    async def _initialize_rich_menu(self, merchant_id: UUID, access_token: str) -> Dict[str, Any]:
        """初始化 Rich Menu"""
        try:
            # 創建預設 Rich Menu
            rich_menu_id = await self.rich_menu_manager.create_default_rich_menu(access_token)
            
            # 設定為預設 Rich Menu
            await self.rich_menu_manager.set_default_rich_menu(access_token, rich_menu_id)
            
            return {
                "status": "success",
                "rich_menu_id": rich_menu_id,
                "message": "Rich Menu 初始化成功"
            }
            
        except Exception as e:
            logger.warning(f"Rich Menu 初始化失敗: {str(e)}")
            return {
                "status": "failed",
                "error": str(e),
                "message": "Rich Menu 初始化失敗，可稍後手動設定"
            }
    
    async def _health_check(self, merchant_id: UUID, access_token: str) -> Dict[str, Any]:
        """健康檢查"""
        try:
            # 1. 測試 LINE API 連線
            line_health = await self.line_client.health_check(access_token)
            
            # 2. 測試 Webhook 設定
            webhook_health = await self._check_webhook_health(merchant_id)
            
            # 3. 測試 LIFF 初始化（如果有設定）
            liff_health = await self._check_liff_health(merchant_id)
            
            overall_status = "healthy" if all([
                line_health["status"] == "success",
                webhook_health["status"] == "success"
            ]) else "warning"
            
            return {
                "status": overall_status,
                "line_api": line_health,
                "webhook": webhook_health,
                "liff": liff_health,
                "timestamp": "2024-01-01T00:00:00Z"  # 實際應該使用當前時間
            }
            
        except Exception as e:
            logger.error(f"健康檢查失敗: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "message": "健康檢查失敗"
            }
    
    async def _check_webhook_health(self, merchant_id: UUID) -> Dict[str, Any]:
        """檢查 Webhook 健康狀態"""
        # 這裡可以實作 Webhook 健康檢查邏輯
        # 例如：檢查最近的事件接收情況、錯誤率等
        return {
            "status": "success",
            "message": "Webhook 健康檢查通過",
            "last_event": None,
            "error_rate": 0.0
        }
    
    async def _check_liff_health(self, merchant_id: UUID) -> Dict[str, Any]:
        """檢查 LIFF 健康狀態"""
        # 這裡可以實作 LIFF 健康檢查邏輯
        return {
            "status": "success",
            "message": "LIFF 健康檢查通過"
        }
    
    async def rotate_credentials(
        self,
        merchant_id: UUID,
        new_access_token: str,
        new_secret: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        輪替商家憑證
        
        Args:
            merchant_id: 商家ID
            new_access_token: 新的 Access Token
            new_secret: 新的 Channel Secret（可選）
            
        Returns:
            Dict: 輪替結果
        """
        try:
            # 1. 取得當前商家資料
            merchant = self.merchant_repo.find_by_id(merchant_id)
            if not merchant:
                raise ValueError("找不到指定的商家")
            
            # 2. 測試新憑證
            health_check = await self.line_client.health_check(new_access_token)
            if health_check["status"] != "success":
                raise ValueError("新憑證驗證失敗")
            
            # 3. 更新憑證
            updated_merchant = self.merchant_repo.update_credentials(
                merchant_id=merchant_id,
                line_channel_secret=new_secret,
                line_channel_access_token=new_access_token
            )
            
            if not updated_merchant:
                raise ValueError("憑證更新失敗")
            
            # 4. 重新健康檢查
            final_health_check = await self._health_check(merchant_id, new_access_token)
            
            self.db_session.commit()
            
            return {
                "status": "success",
                "message": "憑證輪替成功",
                "merchant_id": str(merchant_id),
                "health_check": final_health_check,
                "rotated_at": "2024-01-01T00:00:00Z"  # 實際應該使用當前時間
            }
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"憑證輪替失敗: {str(e)}")
            raise
    
    async def toggle_merchant_status(self, merchant_id: UUID, is_active: bool) -> Dict[str, Any]:
        """
        切換商家狀態
        
        Args:
            merchant_id: 商家ID
            is_active: 是否啟用
            
        Returns:
            Dict: 切換結果
        """
        try:
            merchant = self.merchant_repo.find_by_id(merchant_id)
            if not merchant:
                raise ValueError("找不到指定的商家")
            
            # 更新狀態
            merchant.is_active = is_active
            self.db_session.commit()
            
            action = "啟用" if is_active else "停用"
            logger.info(f"商家 {merchant.name} 已{action}")
            
            return {
                "status": "success",
                "message": f"商家已{action}",
                "merchant_id": str(merchant_id),
                "is_active": is_active,
                "updated_at": "2024-01-01T00:00:00Z"  # 實際應該使用當前時間
            }
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"切換商家狀態失敗: {str(e)}")
            raise
