"""
營業時間資料存取層
"""
from typing import List, Optional
from uuid import UUID
from sqlalchemy.orm import Session
from sqlalchemy import select
from datetime import time

from app.infrastructure.database.models import BusinessHour


class SQLBusinessHourRepository:
    """營業時間資料存取實作"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
    
    def create(self, merchant_id: UUID, day_of_week: int, start_time: str, end_time: str, branch_id: Optional[UUID] = None) -> BusinessHour:
        """
        創建營業時間
        
        Args:
            merchant_id: 商家ID
            day_of_week: 星期幾 (0=Sunday, 1=Monday, ..., 6=Saturday)
            start_time: 開始時間 (HH:MM 格式)
            end_time: 結束時間 (HH:MM 格式)
            branch_id: 分店ID (可選)
            
        Returns:
            BusinessHour: 創建的營業時間記錄
        """
        # 轉換時間格式
        start_time_obj = time.fromisoformat(start_time)
        end_time_obj = time.fromisoformat(end_time)
        
        business_hour = BusinessHour(
            merchant_id=merchant_id,
            branch_id=branch_id,
            day_of_week=day_of_week,
            start_time=start_time_obj,
            end_time=end_time_obj
        )
        
        self.db_session.add(business_hour)
        self.db_session.flush()
        return business_hour
    
    def find_by_merchant(self, merchant_id: UUID, branch_id: Optional[UUID] = None) -> List[BusinessHour]:
        """
        根據商家ID查找營業時間
        
        Args:
            merchant_id: 商家ID
            branch_id: 分店ID (可選)
            
        Returns:
            List[BusinessHour]: 營業時間列表
        """
        stmt = select(BusinessHour).where(BusinessHour.merchant_id == merchant_id)
        
        if branch_id:
            stmt = stmt.where(BusinessHour.branch_id == branch_id)
        else:
            stmt = stmt.where(BusinessHour.branch_id.is_(None))
        
        result = self.db_session.execute(stmt)
        return list(result.scalars().all())
    
    def find_by_merchant_and_day(self, merchant_id: UUID, day_of_week: int, branch_id: Optional[UUID] = None) -> Optional[BusinessHour]:
        """
        根據商家ID和星期幾查找營業時間
        
        Args:
            merchant_id: 商家ID
            day_of_week: 星期幾
            branch_id: 分店ID (可選)
            
        Returns:
            Optional[BusinessHour]: 營業時間記錄
        """
        stmt = select(BusinessHour).where(
            BusinessHour.merchant_id == merchant_id,
            BusinessHour.day_of_week == day_of_week
        )
        
        if branch_id:
            stmt = stmt.where(BusinessHour.branch_id == branch_id)
        else:
            stmt = stmt.where(BusinessHour.branch_id.is_(None))
        
        result = self.db_session.execute(stmt)
        return result.scalar_one_or_none()
    
    def update(self, business_hour_id: UUID, start_time: Optional[str] = None, end_time: Optional[str] = None) -> Optional[BusinessHour]:
        """
        更新營業時間
        
        Args:
            business_hour_id: 營業時間ID
            start_time: 新的開始時間 (HH:MM 格式)
            end_time: 新的結束時間 (HH:MM 格式)
            
        Returns:
            Optional[BusinessHour]: 更新後的營業時間記錄
        """
        stmt = select(BusinessHour).where(BusinessHour.id == business_hour_id)
        result = self.db_session.execute(stmt)
        business_hour = result.scalar_one_or_none()
        
        if not business_hour:
            return None
        
        if start_time:
            business_hour.start_time = time.fromisoformat(start_time)
        if end_time:
            business_hour.end_time = time.fromisoformat(end_time)
        
        self.db_session.flush()
        return business_hour
    
    def delete(self, business_hour_id: UUID) -> bool:
        """
        刪除營業時間
        
        Args:
            business_hour_id: 營業時間ID
            
        Returns:
            bool: 刪除是否成功
        """
        stmt = select(BusinessHour).where(BusinessHour.id == business_hour_id)
        result = self.db_session.execute(stmt)
        business_hour = result.scalar_one_or_none()
        
        if not business_hour:
            return False
        
        self.db_session.delete(business_hour)
        self.db_session.flush()
        return True
    
    def delete_by_merchant(self, merchant_id: UUID, branch_id: Optional[UUID] = None) -> int:
        """
        刪除商家的所有營業時間
        
        Args:
            merchant_id: 商家ID
            branch_id: 分店ID (可選)
            
        Returns:
            int: 刪除的記錄數
        """
        stmt = select(BusinessHour).where(BusinessHour.merchant_id == merchant_id)
        
        if branch_id:
            stmt = stmt.where(BusinessHour.branch_id == branch_id)
        else:
            stmt = stmt.where(BusinessHour.branch_id.is_(None))
        
        result = self.db_session.execute(stmt)
        business_hours = list(result.scalars().all())
        
        for business_hour in business_hours:
            self.db_session.delete(business_hour)
        
        self.db_session.flush()
        return len(business_hours)
    
    def get_weekly_schedule(self, merchant_id: UUID, branch_id: Optional[UUID] = None) -> List[dict]:
        """
        取得一週的營業時間表
        
        Args:
            merchant_id: 商家ID
            branch_id: 分店ID (可選)
            
        Returns:
            List[dict]: 一週的營業時間表
        """
        business_hours = self.find_by_merchant(merchant_id, branch_id)
        
        # 初始化一週的營業時間
        weekly_schedule = []
        for day in range(7):  # 0=Sunday, 1=Monday, ..., 6=Saturday
            day_schedule = {
                "day_of_week": day,
                "day_name": self._get_day_name(day),
                "is_open": False,
                "start_time": None,
                "end_time": None
            }
            
            # 查找該天的營業時間
            for bh in business_hours:
                if bh.day_of_week == day:
                    day_schedule.update({
                        "is_open": True,
                        "start_time": bh.start_time.strftime("%H:%M"),
                        "end_time": bh.end_time.strftime("%H:%M")
                    })
                    break
            
            weekly_schedule.append(day_schedule)
        
        return weekly_schedule
    
    def _get_day_name(self, day_of_week: int) -> str:
        """取得星期名稱"""
        day_names = ["週日", "週一", "週二", "週三", "週四", "週五", "週六"]
        return day_names[day_of_week]