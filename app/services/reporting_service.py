"""
資料與報表服務
負責商家統計、業務指標、顧客規模分析、匯出功能
"""
import logging
import csv
import io
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text, func

from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.infrastructure.repositories.sql_user_repository import SQLUserRepository
from app.infrastructure.repositories.sql_appointment_repository import SqlAppointmentRepository
from app.infrastructure.repositories.sql_transaction_repository import SqlTransactionRepository

logger = logging.getLogger(__name__)


class ReportingService:
    """資料與報表服務"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.merchant_repo = SQLMerchantRepository(db_session)
        self.user_repo = SQLUserRepository(db_session)
        self.appointment_repo = SqlAppointmentRepository(db_session)
        self.transaction_repo = SqlTransactionRepository(db_session)
    
    async def get_merchant_statistics(self) -> Dict[str, Any]:
        """
        取得商家統計
        
        Returns:
            Dict: 商家統計資料
        """
        try:
            # 1. 活躍商家數
            active_merchants = self.merchant_repo.list_active()
            active_count = len(active_merchants)
            
            # 2. 當月新開店數
            current_month = datetime.now().replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            new_merchants_this_month = await self._get_new_merchants_count(current_month)
            
            # 3. 停用數
            inactive_count = await self._get_inactive_merchants_count()
            
            # 4. 總商家數
            total_count = active_count + inactive_count
            
            return {
                "status": "success",
                "statistics": {
                    "total_merchants": total_count,
                    "active_merchants": active_count,
                    "inactive_merchants": inactive_count,
                    "new_merchants_this_month": new_merchants_this_month,
                    "growth_rate": self._calculate_growth_rate(new_merchants_this_month, active_count)
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"取得商家統計失敗: {str(e)}")
            raise
    
    async def get_business_metrics(self, merchant_id: UUID, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """
        取得業務指標
        
        Args:
            merchant_id: 商家ID
            start_date: 開始日期
            end_date: 結束日期
            
        Returns:
            Dict: 業務指標
        """
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            # 1. 預約數統計
            appointment_stats = await self._get_appointment_statistics(merchant_id, start_date, end_date)
            
            # 2. 完成率
            completion_rate = self._calculate_completion_rate(appointment_stats)
            
            # 3. 取消率
            cancellation_rate = self._calculate_cancellation_rate(appointment_stats)
            
            # 4. No-show 率
            no_show_rate = self._calculate_no_show_rate(appointment_stats)
            
            # 5. 客單價
            avg_order_value = await self._get_average_order_value(merchant_id, start_date, end_date)
            
            # 6. 營收統計
            revenue_stats = await self._get_revenue_statistics(merchant_id, start_date, end_date)
            
            return {
                "status": "success",
                "merchant_id": str(merchant_id),
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat()
                },
                "metrics": {
                    "appointments": appointment_stats,
                    "completion_rate": completion_rate,
                    "cancellation_rate": cancellation_rate,
                    "no_show_rate": no_show_rate,
                    "average_order_value": avg_order_value,
                    "revenue": revenue_stats
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"取得業務指標失敗: {str(e)}")
            raise
    
    async def get_customer_scale_analysis(self, merchant_id: UUID) -> Dict[str, Any]:
        """
        取得顧客規模分析
        
        Args:
            merchant_id: 商家ID
            
        Returns:
            Dict: 顧客規模分析
        """
        try:
            # 1. 累積顧客數
            total_customers = await self._get_total_customers_count(merchant_id)
            
            # 2. 近 30 日活躍顧客
            active_customers_30d = await self._get_active_customers_count(merchant_id, 30)
            
            # 3. 新顧客數（近 30 日）
            new_customers_30d = await self._get_new_customers_count(merchant_id, 30)
            
            # 4. 回購率
            repeat_customer_rate = await self._get_repeat_customer_rate(merchant_id)
            
            # 5. 顧客分佈分析
            customer_distribution = await self._get_customer_distribution(merchant_id)
            
            return {
                "status": "success",
                "merchant_id": str(merchant_id),
                "customer_scale": {
                    "total_customers": total_customers,
                    "active_customers_30d": active_customers_30d,
                    "new_customers_30d": new_customers_30d,
                    "repeat_customer_rate": repeat_customer_rate,
                    "customer_distribution": customer_distribution
                },
                "generated_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"取得顧客規模分析失敗: {str(e)}")
            raise
    
    async def export_merchant_list(self) -> str:
        """
        匯出商家清單
        
        Returns:
            str: CSV 格式的商家清單
        """
        try:
            merchants = self.merchant_repo.list_active()
            
            # 創建 CSV 內容
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 寫入標題行
            writer.writerow([
                "商家ID", "商家名稱", "LINE Channel ID", "LIFF ID", 
                "時區", "狀態", "創建時間", "用戶數", "預約數", "營收"
            ])
            
            # 寫入資料行
            for merchant in merchants:
                # 取得統計資料
                user_count = await self._get_merchant_user_count(merchant.id)
                appointment_count = await self._get_merchant_appointment_count(merchant.id)
                revenue = await self._get_merchant_revenue(merchant.id)
                
                writer.writerow([
                    str(merchant.id),
                    merchant.name,
                    merchant.line_channel_id,
                    merchant.liff_id or "",
                    merchant.timezone,
                    "活躍" if merchant.is_active else "停用",
                    merchant.created_at.isoformat(),
                    user_count,
                    appointment_count,
                    revenue
                ])
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"匯出商家清單失敗: {str(e)}")
            raise
    
    async def export_credentials_list(self) -> str:
        """
        匯出憑證清單（遮蔽後）
        
        Returns:
            str: CSV 格式的憑證清單
        """
        try:
            merchants = self.merchant_repo.list_active()
            
            # 創建 CSV 內容
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 寫入標題行
            writer.writerow([
                "商家ID", "商家名稱", "LINE Channel ID", "Channel Secret", 
                "Access Token", "LIFF ID", "狀態", "最後更新"
            ])
            
            # 寫入資料行
            for merchant in merchants:
                # 遮蔽敏感資訊
                masked_secret = self._mask_sensitive_data(merchant.line_channel_secret)
                masked_token = self._mask_sensitive_data(merchant.line_channel_access_token)
                
                writer.writerow([
                    str(merchant.id),
                    merchant.name,
                    merchant.line_channel_id,
                    masked_secret,
                    masked_token,
                    merchant.liff_id or "",
                    "活躍" if merchant.is_active else "停用",
                    merchant.created_at.isoformat()
                ])
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"匯出憑證清單失敗: {str(e)}")
            raise
    
    async def export_operational_report(self, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> str:
        """
        匯出營運報表
        
        Args:
            start_date: 開始日期
            end_date: 結束日期
            
        Returns:
            str: CSV 格式的營運報表
        """
        try:
            if not start_date:
                start_date = datetime.now() - timedelta(days=30)
            if not end_date:
                end_date = datetime.now()
            
            merchants = self.merchant_repo.list_active()
            
            # 創建 CSV 內容
            output = io.StringIO()
            writer = csv.writer(output)
            
            # 寫入標題行
            writer.writerow([
                "商家ID", "商家名稱", "期間", "預約數", "完成數", "取消數", 
                "No-show數", "完成率", "取消率", "No-show率", "營收", "客單價"
            ])
            
            # 寫入資料行
            for merchant in merchants:
                # 取得業務指標
                metrics = await self.get_business_metrics(merchant.id, start_date, end_date)
                
                appointment_stats = metrics["metrics"]["appointments"]
                revenue_stats = metrics["metrics"]["revenue"]
                
                writer.writerow([
                    str(merchant.id),
                    merchant.name,
                    f"{start_date.date()} ~ {end_date.date()}",
                    appointment_stats["total"],
                    appointment_stats["completed"],
                    appointment_stats["cancelled"],
                    appointment_stats["no_show"],
                    f"{metrics['metrics']['completion_rate']:.2%}",
                    f"{metrics['metrics']['cancellation_rate']:.2%}",
                    f"{metrics['metrics']['no_show_rate']:.2%}",
                    revenue_stats["total_revenue"],
                    metrics["metrics"]["average_order_value"]
                ])
            
            return output.getvalue()
            
        except Exception as e:
            logger.error(f"匯出營運報表失敗: {str(e)}")
            raise
    
    # 私有方法
    async def _get_new_merchants_count(self, since_date: datetime) -> int:
        """取得新商家數量"""
        try:
            result = self.db_session.execute(
                text("SELECT COUNT(*) FROM merchants WHERE created_at >= :since_date"),
                {"since_date": since_date}
            )
            return result.scalar() or 0
        except Exception:
            return 0
    
    async def _get_inactive_merchants_count(self) -> int:
        """取得停用商家數量"""
        try:
            result = self.db_session.execute(
                text("SELECT COUNT(*) FROM merchants WHERE is_active = false")
            )
            return result.scalar() or 0
        except Exception:
            return 0
    
    def _calculate_growth_rate(self, new_count: int, total_count: int) -> float:
        """計算成長率"""
        if total_count == 0:
            return 0.0
        return (new_count / total_count) * 100
    
    async def _get_appointment_statistics(self, merchant_id: UUID, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """取得預約統計"""
        try:
            result = self.db_session.execute(
                text("""
                    SELECT 
                        COUNT(*) as total,
                        SUM(CASE WHEN status = 'completed' THEN 1 ELSE 0 END) as completed,
                        SUM(CASE WHEN status = 'cancelled' THEN 1 ELSE 0 END) as cancelled,
                        SUM(CASE WHEN status = 'no_show' THEN 1 ELSE 0 END) as no_show
                    FROM appointments 
                    WHERE merchant_id = :merchant_id 
                    AND appointment_date BETWEEN :start_date AND :end_date
                """),
                {
                    "merchant_id": str(merchant_id),
                    "start_date": start_date.date(),
                    "end_date": end_date.date()
                }
            )
            
            row = result.fetchone()
            if row:
                return {
                    "total": row.total or 0,
                    "completed": row.completed or 0,
                    "cancelled": row.cancelled or 0,
                    "no_show": row.no_show or 0
                }
            else:
                return {"total": 0, "completed": 0, "cancelled": 0, "no_show": 0}
                
        except Exception:
            return {"total": 0, "completed": 0, "cancelled": 0, "no_show": 0}
    
    def _calculate_completion_rate(self, appointment_stats: Dict[str, Any]) -> float:
        """計算完成率"""
        total = appointment_stats["total"]
        if total == 0:
            return 0.0
        return appointment_stats["completed"] / total
    
    def _calculate_cancellation_rate(self, appointment_stats: Dict[str, Any]) -> float:
        """計算取消率"""
        total = appointment_stats["total"]
        if total == 0:
            return 0.0
        return appointment_stats["cancelled"] / total
    
    def _calculate_no_show_rate(self, appointment_stats: Dict[str, Any]) -> float:
        """計算 No-show 率"""
        total = appointment_stats["total"]
        if total == 0:
            return 0.0
        return appointment_stats["no_show"] / total
    
    async def _get_average_order_value(self, merchant_id: UUID, start_date: datetime, end_date: datetime) -> float:
        """取得平均客單價"""
        try:
            result = self.db_session.execute(
                text("""
                    SELECT AVG(amount) as avg_amount
                    FROM transactions 
                    WHERE merchant_id = :merchant_id 
                    AND created_at BETWEEN :start_date AND :end_date
                """),
                {
                    "merchant_id": str(merchant_id),
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            row = result.fetchone()
            return float(row.avg_amount) if row and row.avg_amount else 0.0
            
        except Exception:
            return 0.0
    
    async def _get_revenue_statistics(self, merchant_id: UUID, start_date: datetime, end_date: datetime) -> Dict[str, Any]:
        """取得營收統計"""
        try:
            result = self.db_session.execute(
                text("""
                    SELECT 
                        SUM(amount) as total_revenue,
                        COUNT(*) as transaction_count,
                        AVG(amount) as avg_transaction
                    FROM transactions 
                    WHERE merchant_id = :merchant_id 
                    AND created_at BETWEEN :start_date AND :end_date
                """),
                {
                    "merchant_id": str(merchant_id),
                    "start_date": start_date,
                    "end_date": end_date
                }
            )
            
            row = result.fetchone()
            if row:
                return {
                    "total_revenue": float(row.total_revenue) if row.total_revenue else 0.0,
                    "transaction_count": row.transaction_count or 0,
                    "average_transaction": float(row.avg_transaction) if row.avg_transaction else 0.0
                }
            else:
                return {"total_revenue": 0.0, "transaction_count": 0, "average_transaction": 0.0}
                
        except Exception:
            return {"total_revenue": 0.0, "transaction_count": 0, "average_transaction": 0.0}
    
    async def _get_total_customers_count(self, merchant_id: UUID) -> int:
        """取得累積顧客數"""
        try:
            result = self.db_session.execute(
                text("SELECT COUNT(*) FROM users WHERE merchant_id = :merchant_id"),
                {"merchant_id": str(merchant_id)}
            )
            return result.scalar() or 0
        except Exception:
            return 0
    
    async def _get_active_customers_count(self, merchant_id: UUID, days: int) -> int:
        """取得活躍顧客數"""
        try:
            since_date = datetime.now() - timedelta(days=days)
            result = self.db_session.execute(
                text("""
                    SELECT COUNT(DISTINCT user_id) 
                    FROM appointments 
                    WHERE merchant_id = :merchant_id 
                    AND created_at >= :since_date
                """),
                {
                    "merchant_id": str(merchant_id),
                    "since_date": since_date
                }
            )
            return result.scalar() or 0
        except Exception:
            return 0
    
    async def _get_new_customers_count(self, merchant_id: UUID, days: int) -> int:
        """取得新顧客數"""
        try:
            since_date = datetime.now() - timedelta(days=days)
            result = self.db_session.execute(
                text("""
                    SELECT COUNT(*) 
                    FROM users 
                    WHERE merchant_id = :merchant_id 
                    AND created_at >= :since_date
                """),
                {
                    "merchant_id": str(merchant_id),
                    "since_date": since_date
                }
            )
            return result.scalar() or 0
        except Exception:
            return 0
    
    async def _get_repeat_customer_rate(self, merchant_id: UUID) -> float:
        """取得回購率"""
        try:
            # 計算有多次預約的顧客比例
            result = self.db_session.execute(
                text("""
                    SELECT 
                        COUNT(*) as total_customers,
                        SUM(CASE WHEN appointment_count > 1 THEN 1 ELSE 0 END) as repeat_customers
                    FROM (
                        SELECT user_id, COUNT(*) as appointment_count
                        FROM appointments 
                        WHERE merchant_id = :merchant_id
                        GROUP BY user_id
                    ) customer_stats
                """),
                {"merchant_id": str(merchant_id)}
            )
            
            row = result.fetchone()
            if row and row.total_customers > 0:
                return row.repeat_customers / row.total_customers
            else:
                return 0.0
                
        except Exception:
            return 0.0
    
    async def _get_customer_distribution(self, merchant_id: UUID) -> Dict[str, Any]:
        """取得顧客分佈分析"""
        try:
            result = self.db_session.execute(
                text("""
                    SELECT 
                        COUNT(*) as total_customers,
                        AVG(appointment_count) as avg_appointments_per_customer,
                        MAX(appointment_count) as max_appointments_per_customer
                    FROM (
                        SELECT user_id, COUNT(*) as appointment_count
                        FROM appointments 
                        WHERE merchant_id = :merchant_id
                        GROUP BY user_id
                    ) customer_stats
                """),
                {"merchant_id": str(merchant_id)}
            )
            
            row = result.fetchone()
            if row:
                return {
                    "total_customers": row.total_customers or 0,
                    "avg_appointments_per_customer": float(row.avg_appointments_per_customer) if row.avg_appointments_per_customer else 0.0,
                    "max_appointments_per_customer": row.max_appointments_per_customer or 0
                }
            else:
                return {"total_customers": 0, "avg_appointments_per_customer": 0.0, "max_appointments_per_customer": 0}
                
        except Exception:
            return {"total_customers": 0, "avg_appointments_per_customer": 0.0, "max_appointments_per_customer": 0}
    
    async def _get_merchant_user_count(self, merchant_id: UUID) -> int:
        """取得商家用戶數"""
        return await self._get_total_customers_count(merchant_id)
    
    async def _get_merchant_appointment_count(self, merchant_id: UUID) -> int:
        """取得商家預約數"""
        try:
            result = self.db_session.execute(
                text("SELECT COUNT(*) FROM appointments WHERE merchant_id = :merchant_id"),
                {"merchant_id": str(merchant_id)}
            )
            return result.scalar() or 0
        except Exception:
            return 0
    
    async def _get_merchant_revenue(self, merchant_id: UUID) -> float:
        """取得商家營收"""
        try:
            result = self.db_session.execute(
                text("SELECT SUM(amount) FROM transactions WHERE merchant_id = :merchant_id"),
                {"merchant_id": str(merchant_id)}
            )
            return float(result.scalar()) if result.scalar() else 0.0
        except Exception:
            return 0.0
    
    def _mask_sensitive_data(self, data: str) -> str:
        """遮蔽敏感資料"""
        if not data or len(data) < 8:
            return "***"
        return data[:4] + "*" * (len(data) - 8) + data[-4:]
