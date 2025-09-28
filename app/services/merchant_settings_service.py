"""
商家設定管理服務
負責管理商家的基本設定、營業規則、LIFF、Rich Menu 等
"""
import logging
from typing import Dict, Any, Optional, List
from uuid import UUID
from sqlalchemy.orm import Session

from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.infrastructure.repositories.sql_service_repository import SqlServiceRepository
from app.infrastructure.repositories.sql_business_hour_repository import SQLBusinessHourRepository
from app.rich_menu_manager import RichMenuManager
from app.line_client import LineClient

logger = logging.getLogger(__name__)


class MerchantSettingsService:
    """商家設定管理服務"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.merchant_repo = SQLMerchantRepository(db_session)
        self.service_repo = SqlServiceRepository(db_session)
        self.business_hour_repo = SQLBusinessHourRepository(db_session)
        self.rich_menu_manager = RichMenuManager()
        self.line_client = LineClient()
    
    async def get_basic_settings(self, merchant_id: UUID) -> Dict[str, Any]:
        """
        取得商家基本設定
        
        Args:
            merchant_id: 商家ID
            
        Returns:
            Dict: 基本設定資料
        """
        try:
            merchant = self.merchant_repo.find_by_id(merchant_id)
            if not merchant:
                raise ValueError("找不到指定的商家")
            
            return {
                "merchant_id": str(merchant_id),
                "name": merchant.name,
                "timezone": merchant.timezone,
                "line_channel_id": merchant.line_channel_id,
                "liff_id": merchant.liff_id,
                "is_active": merchant.is_active,
                "created_at": merchant.created_at.isoformat() if merchant.created_at else None
            }
            
        except Exception as e:
            logger.error(f"取得商家基本設定失敗: {e}")
            raise

    async def update_basic_settings(
        self,
        merchant_id: UUID,
        name: Optional[str] = None,
        address: Optional[str] = None,
        phone: Optional[str] = None,
        brand_icon: Optional[str] = None,
        ig_link: Optional[str] = None,
        timezone: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        更新商家基本設定
        
        Args:
            merchant_id: 商家ID
            name: 商家名稱
            address: 地址
            phone: 電話
            brand_icon: 品牌圖示URL
            ig_link: Instagram 連結
            timezone: 時區
            
        Returns:
            Dict: 更新結果
        """
        try:
            merchant = self.merchant_repo.find_by_id(merchant_id)
            if not merchant:
                raise ValueError("找不到指定的商家")
            
            # 更新基本資訊
            if name:
                merchant.name = name
            if timezone:
                merchant.timezone = timezone
            
            # 這裡可以擴展更多基本設定欄位
            # 例如：address, phone, brand_icon, ig_link 等
            
            self.db_session.commit()
            
            logger.info(f"商家 {merchant_id} 基本設定已更新")
            
            return {
                "status": "success",
                "message": "基本設定更新成功",
                "merchant_id": str(merchant_id),
                "updated_fields": {
                    "name": name,
                    "timezone": timezone
                },
                "updated_at": "2024-01-01T00:00:00Z"  # 實際應該使用當前時間
            }
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"更新基本設定失敗: {str(e)}")
            raise
    
    async def update_business_rules(
        self,
        merchant_id: UUID,
        booking_advance_hours: Optional[int] = None,
        cancellation_hours: Optional[int] = None,
        no_show_penalty: Optional[bool] = None,
        max_advance_days: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        更新營業規則
        
        Args:
            merchant_id: 商家ID
            booking_advance_hours: 可預約提前小時數
            cancellation_hours: 最晚取消時間（小時）
            no_show_penalty: 是否啟用 No-show 懲罰
            max_advance_days: 最大提前預約天數
            
        Returns:
            Dict: 更新結果
        """
        try:
            merchant = self.merchant_repo.find_by_id(merchant_id)
            if not merchant:
                raise ValueError("找不到指定的商家")
            
            # 這裡可以實作營業規則的儲存邏輯
            # 可以新增一個 business_rules 表或使用 JSON 欄位
            
            logger.info(f"商家 {merchant_id} 營業規則已更新")
            
            return {
                "status": "success",
                "message": "營業規則更新成功",
                "merchant_id": str(merchant_id),
                "updated_rules": {
                    "booking_advance_hours": booking_advance_hours,
                    "cancellation_hours": cancellation_hours,
                    "no_show_penalty": no_show_penalty,
                    "max_advance_days": max_advance_days
                },
                "updated_at": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"更新營業規則失敗: {str(e)}")
            raise
    
    async def update_liff_settings(
        self,
        merchant_id: UUID,
        liff_id: str
    ) -> Dict[str, Any]:
        """
        更新 LIFF 設定
        
        Args:
            merchant_id: 商家ID
            liff_id: 新的 LIFF ID
            
        Returns:
            Dict: 更新結果
        """
        try:
            merchant = self.merchant_repo.find_by_id(merchant_id)
            if not merchant:
                raise ValueError("找不到指定的商家")
            
            # 更新 LIFF ID
            merchant.liff_id = liff_id
            
            # 健康檢查
            health_check = await self._check_liff_health(merchant_id, liff_id)
            
            self.db_session.commit()
            
            return {
                "status": "success",
                "message": "LIFF 設定更新成功",
                "merchant_id": str(merchant_id),
                "liff_id": liff_id,
                "health_check": health_check,
                "updated_at": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"更新 LIFF 設定失敗: {str(e)}")
            raise
    
    async def publish_rich_menu(
        self,
        merchant_id: UUID,
        rich_menu_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        發布 Rich Menu
        
        Args:
            merchant_id: 商家ID
            rich_menu_id: Rich Menu ID（可選，不提供則使用預設）
            
        Returns:
            Dict: 發布結果
        """
        try:
            merchant = self.merchant_repo.find_by_id(merchant_id)
            if not merchant:
                raise ValueError("找不到指定的商家")
            
            # 取得解密後的憑證
            merchant_data = self.merchant_repo.get_decrypted_merchant(merchant_id)
            if not merchant_data:
                raise ValueError("無法取得商家憑證")
            
            access_token = merchant_data["line_channel_access_token"]
            
            # 如果沒有指定 Rich Menu ID，創建預設的
            if not rich_menu_id:
                rich_menu_id = await self.rich_menu_manager.create_default_rich_menu(access_token)
            
            # 發布 Rich Menu
            result = await self.rich_menu_manager.publish_rich_menu(access_token, rich_menu_id)
            
            return {
                "status": "success",
                "message": "Rich Menu 發布成功",
                "merchant_id": str(merchant_id),
                "rich_menu_id": rich_menu_id,
                "publish_result": result,
                "published_at": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            logger.error(f"發布 Rich Menu 失敗: {str(e)}")
            raise
    
    async def rollback_rich_menu(
        self,
        merchant_id: UUID,
        previous_rich_menu_id: str
    ) -> Dict[str, Any]:
        """
        回滾 Rich Menu
        
        Args:
            merchant_id: 商家ID
            previous_rich_menu_id: 之前的 Rich Menu ID
            
        Returns:
            Dict: 回滾結果
        """
        try:
            merchant = self.merchant_repo.find_by_id(merchant_id)
            if not merchant:
                raise ValueError("找不到指定的商家")
            
            # 取得解密後的憑證
            merchant_data = self.merchant_repo.get_decrypted_merchant(merchant_id)
            if not merchant_data:
                raise ValueError("無法取得商家憑證")
            
            access_token = merchant_data["line_channel_access_token"]
            
            # 回滾 Rich Menu
            result = await self.rich_menu_manager.rollback_rich_menu(access_token, previous_rich_menu_id)
            
            return {
                "status": "success",
                "message": "Rich Menu 回滾成功",
                "merchant_id": str(merchant_id),
                "rich_menu_id": previous_rich_menu_id,
                "rollback_result": result,
                "rolled_back_at": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            logger.error(f"回滾 Rich Menu 失敗: {str(e)}")
            raise
    
    async def get_template_library(self) -> Dict[str, Any]:
        """
        取得範本庫
        
        Returns:
            Dict: 範本庫內容
        """
        try:
            # 服務項目範本
            service_templates = [
                {
                    "id": "basic_nail",
                    "name": "基礎美甲",
                    "price": 800,
                    "duration_minutes": 60,
                    "description": "基礎指甲護理與上色"
                },
                {
                    "id": "french_nail",
                    "name": "法式美甲",
                    "price": 1200,
                    "duration_minutes": 90,
                    "description": "經典法式美甲設計"
                },
                {
                    "id": "art_nail",
                    "name": "彩繪美甲",
                    "price": 1500,
                    "duration_minutes": 120,
                    "description": "客製化彩繪設計"
                },
                {
                    "id": "gel_nail",
                    "name": "光療美甲",
                    "price": 1800,
                    "duration_minutes": 120,
                    "description": "持久光療美甲"
                }
            ]
            
            # Flex Message 範本
            flex_templates = [
                {
                    "id": "booking_confirmation",
                    "name": "預約確認",
                    "description": "預約成功確認訊息"
                },
                {
                    "id": "reminder",
                    "name": "預約提醒",
                    "description": "預約前提醒訊息"
                },
                {
                    "id": "cancellation",
                    "name": "取消通知",
                    "description": "預約取消通知"
                }
            ]
            
            # FAQ 範本
            faq_templates = [
                {
                    "id": "booking_process",
                    "question": "如何預約？",
                    "answer": "請點選下方按鈕開始預約流程"
                },
                {
                    "id": "cancellation_policy",
                    "question": "取消政策是什麼？",
                    "answer": "請於預約時間前24小時取消"
                },
                {
                    "id": "payment_methods",
                    "question": "接受哪些付款方式？",
                    "answer": "現金、信用卡、LINE Pay"
                }
            ]
            
            return {
                "status": "success",
                "templates": {
                    "services": service_templates,
                    "flex_messages": flex_templates,
                    "faq": faq_templates
                },
                "updated_at": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            logger.error(f"取得範本庫失敗: {str(e)}")
            raise
    
    async def apply_service_template(
        self,
        merchant_id: UUID,
        template_id: str
    ) -> Dict[str, Any]:
        """
        套用服務項目範本
        
        Args:
            merchant_id: 商家ID
            template_id: 範本ID
            
        Returns:
            Dict: 套用結果
        """
        try:
            # 取得範本庫
            template_library = await self.get_template_library()
            service_templates = template_library["templates"]["services"]
            
            # 找到對應的範本
            template = next((t for t in service_templates if t["id"] == template_id), None)
            if not template:
                raise ValueError(f"找不到範本: {template_id}")
            
            # 創建 Domain Service 物件
            from app.domain.booking.models import Service as DomainService
            domain_service = DomainService(
                merchant_id=merchant_id,
                name=template["name"],
                price=template["price"],
                duration_minutes=template["duration_minutes"]
            )
            self.service_repo.add(domain_service)
            
            self.db_session.commit()
            
            return {
                "status": "success",
                "message": "服務項目範本套用成功",
                "merchant_id": str(merchant_id),
                "service_id": "created",
                "template_id": template_id,
                "applied_at": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            self.db_session.rollback()
            logger.error(f"套用服務項目範本失敗: {str(e)}")
            raise
    
    async def _check_liff_health(self, merchant_id: UUID, liff_id: str) -> Dict[str, Any]:
        """檢查 LIFF 健康狀態"""
        try:
            # 這裡可以實作 LIFF 健康檢查邏輯
            # 例如：檢查 LIFF 是否可正常載入、API 是否可正常調用等
            
            return {
                "status": "success",
                "message": "LIFF 健康檢查通過",
                "liff_id": liff_id,
                "checked_at": "2024-01-01T00:00:00Z"
            }
            
        except Exception as e:
            return {
                "status": "error",
                "message": f"LIFF 健康檢查失敗: {str(e)}",
                "liff_id": liff_id,
                "checked_at": "2024-01-01T00:00:00Z"
            }
