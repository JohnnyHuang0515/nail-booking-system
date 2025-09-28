"""
多商家排程與提醒系統
"""
import asyncio
from datetime import datetime, date, time, timedelta
from typing import List, Dict, Any
import pytz
from uuid import UUID

from app.infrastructure.database.session import get_db_session
from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.infrastructure.repositories.sql_appointment_repository import SQLAppointmentRepository
from app.infrastructure.repositories.sql_user_repository import SQLUserRepository
from app.line_client import LineClient
from app.flex_templates import FlexTemplates


class AppointmentScheduler:
    """預約排程與提醒管理器"""
    
    def __init__(self):
        self.running = False
    
    async def start(self):
        """啟動排程器"""
        self.running = True
        print("預約排程器已啟動")
        
        # 啟動多個並發任務
        tasks = [
            asyncio.create_task(self._reminder_task()),
            asyncio.create_task(self._status_update_task()),
            asyncio.create_task(self._cleanup_task())
        ]
        
        await asyncio.gather(*tasks)
    
    async def stop(self):
        """停止排程器"""
        self.running = False
        print("預約排程器已停止")
    
    async def _reminder_task(self):
        """預約提醒任務"""
        while self.running:
            try:
                await self._send_appointment_reminders()
                # 每小時檢查一次
                await asyncio.sleep(3600)
            except Exception as e:
                print(f"預約提醒任務錯誤: {str(e)}")
                await asyncio.sleep(300)  # 錯誤時等待5分鐘
    
    async def _status_update_task(self):
        """預約狀態更新任務"""
        while self.running:
            try:
                await self._update_appointment_statuses()
                # 每30分鐘檢查一次
                await asyncio.sleep(1800)
            except Exception as e:
                print(f"狀態更新任務錯誤: {str(e)}")
                await asyncio.sleep(300)
    
    async def _cleanup_task(self):
        """清理任務"""
        while self.running:
            try:
                await self._cleanup_old_data()
                # 每天執行一次
                await asyncio.sleep(86400)
            except Exception as e:
                print(f"清理任務錯誤: {str(e)}")
                await asyncio.sleep(3600)
    
    async def _send_appointment_reminders(self):
        """發送預約提醒"""
        print("檢查預約提醒...")
        
        with get_db_session() as db_session:
            merchant_repo = SQLMerchantRepository(db_session)
            appointment_repo = SQLAppointmentRepository(db_session)
            user_repo = SQLUserRepository(db_session)
            
            # 取得所有活躍商家
            merchants = merchant_repo.list_active()
            
            for merchant in merchants:
                try:
                    await self._send_merchant_reminders(
                        merchant, appointment_repo, user_repo
                    )
                except Exception as e:
                    print(f"商家 {merchant.name} 提醒發送失敗: {str(e)}")
    
    async def _send_merchant_reminders(self, merchant, appointment_repo, user_repo):
        """為特定商家發送提醒"""
        # 設定商家時區
        merchant_tz = pytz.timezone(merchant.timezone)
        now = datetime.now(merchant_tz)
        tomorrow = now.date() + timedelta(days=1)
        
        # 查找明天有預約的用戶
        appointments = appointment_repo.list_by_merchant_and_date(
            merchant.id, tomorrow
        )
        
        for appointment in appointments:
            try:
                # 檢查是否已發送提醒（這裡可以加入提醒記錄表）
                if self._should_send_reminder(appointment):
                    await self._send_single_reminder(
                        merchant, appointment, user_repo
                    )
            except Exception as e:
                print(f"發送預約 {appointment.id} 提醒失敗: {str(e)}")
    
    async def _send_single_reminder(self, merchant, appointment, user_repo):
        """發送單個預約提醒"""
        # 取得用戶資料
        user = user_repo.get_by_id(appointment.user_id)
        if not user:
            return
        
        # 創建 LINE 客戶端
        line_client = LineClient(merchant.line_channel_access_token)
        
        # 創建提醒訊息
        reminder_flex = FlexTemplates.appointment_reminder(
            merchant_name=merchant.name,
            user_name=user.name or "客戶",
            service_name=appointment.service.name if hasattr(appointment, 'service') else "美甲服務",
            appointment_date=appointment.appointment_date,
            appointment_time=appointment.appointment_time,
            appointment_id=appointment.id
        )
        
        # 發送提醒（這裡需要 LINE 用戶 ID，可能需要從用戶表取得）
        if hasattr(user, 'line_user_id') and user.line_user_id:
            success = await line_client.push_flex(
                user.line_user_id,
                reminder_flex,
                "預約提醒"
            )
            
            if success:
                print(f"已發送預約提醒給用戶 {user.line_user_id}")
            else:
                print(f"發送預約提醒失敗，用戶 {user.line_user_id}")
    
    def _should_send_reminder(self, appointment) -> bool:
        """判斷是否應該發送提醒"""
        # 這裡可以加入更複雜的邏輯
        # 例如：檢查是否已發送過、用戶偏好設定等
        return True
    
    async def _update_appointment_statuses(self):
        """更新預約狀態"""
        print("更新預約狀態...")
        
        with get_db_session() as db_session:
            merchant_repo = SQLMerchantRepository(db_session)
            appointment_repo = SQLAppointmentRepository(db_session)
            
            merchants = merchant_repo.list_active()
            
            for merchant in merchants:
                try:
                    await self._update_merchant_appointment_statuses(
                        merchant, appointment_repo
                    )
                except Exception as e:
                    print(f"更新商家 {merchant.name} 預約狀態失敗: {str(e)}")
    
    async def _update_merchant_appointment_statuses(self, merchant, appointment_repo):
        """更新特定商家的預約狀態"""
        merchant_tz = pytz.timezone(merchant.timezone)
        now = datetime.now(merchant_tz)
        
        # 查找需要更新狀態的預約
        # 例如：超時未到的預約標記為 no-show
        # 這裡需要根據業務邏輯實作
        
        pass
    
    async def _cleanup_old_data(self):
        """清理舊資料"""
        print("清理舊資料...")
        
        # 這裡可以加入清理邏輯
        # 例如：刪除過期的預約記錄、清理日誌等
        
        pass
    
    async def send_immediate_reminder(self, merchant_id: UUID, appointment_id: UUID):
        """立即發送預約提醒"""
        with get_db_session() as db_session:
            merchant_repo = SQLMerchantRepository(db_session)
            appointment_repo = SQLAppointmentRepository(db_session)
            user_repo = SQLUserRepository(db_session)
            
            merchant = merchant_repo.find_by_id(merchant_id)
            appointment = appointment_repo.find_by_id(appointment_id)
            
            if merchant and appointment:
                await self._send_single_reminder(
                    merchant, appointment, user_repo
                )
    
    async def schedule_appointment_reminder(
        self, 
        merchant_id: UUID, 
        appointment_id: UUID, 
        reminder_time: datetime
    ):
        """排程預約提醒"""
        # 這裡可以加入更複雜的排程邏輯
        # 例如：使用 Redis 或專用任務佇列
        pass


# 全域排程器實例
scheduler = AppointmentScheduler()


async def start_scheduler():
    """啟動全域排程器"""
    await scheduler.start()


async def stop_scheduler():
    """停止全域排程器"""
    await scheduler.stop()


# 用於測試的函數
async def test_reminder_system():
    """測試提醒系統"""
    print("測試提醒系統...")
    
    with get_db_session() as db_session:
        merchant_repo = SQLMerchantRepository(db_session)
        merchants = merchant_repo.list_active()
        
        print(f"找到 {len(merchants)} 個活躍商家")
        for merchant in merchants:
            print(f"  - {merchant.name} (ID: {merchant.id})")


if __name__ == "__main__":
    # 測試排程器
    asyncio.run(test_reminder_system())
