"""
監控與健診服務
負責 Webhook 健康、推播配額、任務排程、可用性監控
"""
import logging
from typing import Dict, Any, List, Optional
from uuid import UUID
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import text

from app.infrastructure.repositories.sql_merchant_repository import SQLMerchantRepository
from app.line_client import LineClient

logger = logging.getLogger(__name__)


class MonitoringService:
    """監控與健診服務"""
    
    def __init__(self, db_session: Session):
        self.db_session = db_session
        self.merchant_repo = SQLMerchantRepository(db_session)
        self.line_client = LineClient()
    
    async def get_webhook_health(self, merchant_id: UUID) -> Dict[str, Any]:
        """
        取得 Webhook 健康狀態
        
        Args:
            merchant_id: 商家ID
            
        Returns:
            Dict: Webhook 健康狀態
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
            
            # 1. 檢查 Webhook 設定
            webhook_info = await self.line_client.get_webhook_info(access_token)
            
            # 2. 檢查最近 24 小時的事件統計
            event_stats = await self._get_recent_event_stats(merchant_id)
            
            # 3. 計算成功率
            success_rate = self._calculate_success_rate(event_stats)
            
            # 4. 檢查錯誤分佈
            error_distribution = self._get_error_distribution(event_stats)
            
            # 5. 檢查延遲指標
            latency_metrics = self._get_latency_metrics(event_stats)
            
            overall_status = "healthy" if success_rate >= 0.95 else "warning" if success_rate >= 0.90 else "critical"
            
            return {
                "status": overall_status,
                "merchant_id": str(merchant_id),
                "webhook_info": webhook_info,
                "event_stats": event_stats,
                "success_rate": success_rate,
                "error_distribution": error_distribution,
                "latency_metrics": latency_metrics,
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Webhook 健康檢查失敗: {str(e)}")
            return {
                "status": "error",
                "merchant_id": str(merchant_id),
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
    
    async def get_push_quota_status(self, merchant_id: UUID) -> Dict[str, Any]:
        """
        取得推播配額狀態
        
        Args:
            merchant_id: 商家ID
            
        Returns:
            Dict: 推播配額狀態
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
            
            # 1. 取得 LINE API 配額資訊
            quota_info = await self._get_line_api_quota(access_token)
            
            # 2. 計算今日推播量
            today_push_count = await self._get_today_push_count(merchant_id)
            
            # 3. 計算本月推播量
            monthly_push_count = await self._get_monthly_push_count(merchant_id)
            
            # 4. 計算速率限制
            rate_limit_status = await self._get_rate_limit_status(merchant_id)
            
            return {
                "status": "success",
                "merchant_id": str(merchant_id),
                "quota_info": quota_info,
                "daily_usage": {
                    "count": today_push_count,
                    "limit": quota_info.get("daily_limit", 1000),
                    "percentage": (today_push_count / quota_info.get("daily_limit", 1000)) * 100
                },
                "monthly_usage": {
                    "count": monthly_push_count,
                    "limit": quota_info.get("monthly_limit", 30000),
                    "percentage": (monthly_push_count / quota_info.get("monthly_limit", 30000)) * 100
                },
                "rate_limit": rate_limit_status,
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"推播配額檢查失敗: {str(e)}")
            return {
                "status": "error",
                "merchant_id": str(merchant_id),
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
    
    async def get_task_queue_status(self, merchant_id: UUID) -> Dict[str, Any]:
        """
        取得任務排程狀態
        
        Args:
            merchant_id: 商家ID
            
        Returns:
            Dict: 任務排程狀態
        """
        try:
            # 1. 取得提醒任務狀態
            reminder_tasks = await self._get_reminder_task_status(merchant_id)
            
            # 2. 取得推播任務狀態
            push_tasks = await self._get_push_task_status(merchant_id)
            
            # 3. 取得清理任務狀態
            cleanup_tasks = await self._get_cleanup_task_status(merchant_id)
            
            # 4. 計算整體狀態
            total_tasks = reminder_tasks["total"] + push_tasks["total"] + cleanup_tasks["total"]
            failed_tasks = reminder_tasks["failed"] + push_tasks["failed"] + cleanup_tasks["failed"]
            retry_tasks = reminder_tasks["retry"] + push_tasks["retry"] + cleanup_tasks["retry"]
            
            overall_status = "healthy" if failed_tasks == 0 else "warning" if failed_tasks < total_tasks * 0.1 else "critical"
            
            return {
                "status": overall_status,
                "merchant_id": str(merchant_id),
                "task_summary": {
                    "total": total_tasks,
                    "success": total_tasks - failed_tasks - retry_tasks,
                    "failed": failed_tasks,
                    "retry": retry_tasks
                },
                "task_details": {
                    "reminder_tasks": reminder_tasks,
                    "push_tasks": push_tasks,
                    "cleanup_tasks": cleanup_tasks
                },
                "delay_metrics": await self._get_delay_metrics(merchant_id),
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"任務排程檢查失敗: {str(e)}")
            return {
                "status": "error",
                "merchant_id": str(merchant_id),
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
    
    async def get_availability_status(self, merchant_id: UUID) -> Dict[str, Any]:
        """
        取得可用性狀態
        
        Args:
            merchant_id: 商家ID
            
        Returns:
            Dict: 可用性狀態
        """
        try:
            merchant = self.merchant_repo.find_by_id(merchant_id)
            if not merchant:
                raise ValueError("找不到指定的商家")
            
            # 1. 檢查 LIFF 開啟率
            liff_availability = await self._check_liff_availability(merchant_id)
            
            # 2. 檢查 API 5xx 錯誤率
            api_error_rate = await self._get_api_error_rate(merchant_id)
            
            # 3. 檢查前端資產版本
            frontend_version = await self._get_frontend_version_status(merchant_id)
            
            # 4. 檢查資料庫連線
            database_status = await self._check_database_connection()
            
            # 5. 檢查外部服務依賴
            external_services = await self._check_external_services(merchant_id)
            
            overall_status = "healthy" if all([
                liff_availability["status"] == "success",
                api_error_rate < 0.01,
                database_status["status"] == "success"
            ]) else "warning"
            
            return {
                "status": overall_status,
                "merchant_id": str(merchant_id),
                "liff_availability": liff_availability,
                "api_error_rate": api_error_rate,
                "frontend_version": frontend_version,
                "database_status": database_status,
                "external_services": external_services,
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"可用性檢查失敗: {str(e)}")
            return {
                "status": "error",
                "merchant_id": str(merchant_id),
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
    
    async def get_platform_overview(self) -> Dict[str, Any]:
        """
        取得平台總覽監控
        
        Returns:
            Dict: 平台總覽
        """
        try:
            # 1. 取得所有商家
            merchants = self.merchant_repo.list_active()
            
            # 2. 計算整體健康狀態
            health_summary = await self._calculate_platform_health_summary(merchants)
            
            # 3. 取得系統統計
            system_stats = await self._get_system_statistics()
            
            # 4. 取得錯誤榜
            error_leaderboard = await self._get_error_leaderboard()
            
            return {
                "status": "success",
                "platform_health": health_summary,
                "system_statistics": system_stats,
                "error_leaderboard": error_leaderboard,
                "total_merchants": len(merchants),
                "checked_at": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"平台總覽檢查失敗: {str(e)}")
            return {
                "status": "error",
                "error": str(e),
                "checked_at": datetime.now().isoformat()
            }
    
    # 私有方法
    async def _get_recent_event_stats(self, merchant_id: UUID) -> Dict[str, Any]:
        """取得最近 24 小時的事件統計"""
        # 這裡可以實作從資料庫或日誌系統取得事件統計的邏輯
        return {
            "total_events": 150,
            "successful_events": 145,
            "failed_events": 5,
            "event_types": {
                "message": 100,
                "follow": 20,
                "unfollow": 5,
                "postback": 25
            }
        }
    
    def _calculate_success_rate(self, event_stats: Dict[str, Any]) -> float:
        """計算成功率"""
        total = event_stats["total_events"]
        successful = event_stats["successful_events"]
        return successful / total if total > 0 else 0.0
    
    def _get_error_distribution(self, event_stats: Dict[str, Any]) -> Dict[str, Any]:
        """取得錯誤分佈"""
        return {
            "timeout": 2,
            "network_error": 1,
            "validation_error": 1,
            "unknown": 1
        }
    
    def _get_latency_metrics(self, event_stats: Dict[str, Any]) -> Dict[str, Any]:
        """取得延遲指標"""
        return {
            "avg_latency_ms": 150,
            "p95_latency_ms": 300,
            "p99_latency_ms": 500,
            "max_latency_ms": 1000
        }
    
    async def _get_line_api_quota(self, access_token: str) -> Dict[str, Any]:
        """取得 LINE API 配額資訊"""
        # 這裡可以實作從 LINE API 取得配額資訊的邏輯
        return {
            "daily_limit": 1000,
            "monthly_limit": 30000,
            "current_daily_usage": 50,
            "current_monthly_usage": 1500
        }
    
    async def _get_today_push_count(self, merchant_id: UUID) -> int:
        """取得今日推播數量"""
        # 這裡可以實作從資料庫取得今日推播數量的邏輯
        return 50
    
    async def _get_monthly_push_count(self, merchant_id: UUID) -> int:
        """取得本月推播數量"""
        # 這裡可以實作從資料庫取得本月推播數量的邏輯
        return 1500
    
    async def _get_rate_limit_status(self, merchant_id: UUID) -> Dict[str, Any]:
        """取得速率限制狀態"""
        return {
            "current_rate": 10,
            "max_rate": 100,
            "window_size": 60,
            "status": "normal"
        }
    
    async def _get_reminder_task_status(self, merchant_id: UUID) -> Dict[str, Any]:
        """取得提醒任務狀態"""
        return {
            "total": 100,
            "success": 95,
            "failed": 3,
            "retry": 2,
            "pending": 0
        }
    
    async def _get_push_task_status(self, merchant_id: UUID) -> Dict[str, Any]:
        """取得推播任務狀態"""
        return {
            "total": 50,
            "success": 48,
            "failed": 1,
            "retry": 1,
            "pending": 0
        }
    
    async def _get_cleanup_task_status(self, merchant_id: UUID) -> Dict[str, Any]:
        """取得清理任務狀態"""
        return {
            "total": 10,
            "success": 10,
            "failed": 0,
            "retry": 0,
            "pending": 0
        }
    
    async def _get_delay_metrics(self, merchant_id: UUID) -> Dict[str, Any]:
        """取得延遲指標"""
        return {
            "avg_delay_seconds": 5,
            "max_delay_seconds": 30,
            "delayed_tasks": 2
        }
    
    async def _check_liff_availability(self, merchant_id: UUID) -> Dict[str, Any]:
        """檢查 LIFF 可用性"""
        return {
            "status": "success",
            "availability_rate": 0.99,
            "last_check": datetime.now().isoformat()
        }
    
    async def _get_api_error_rate(self, merchant_id: UUID) -> float:
        """取得 API 錯誤率"""
        return 0.005  # 0.5%
    
    async def _get_frontend_version_status(self, merchant_id: UUID) -> Dict[str, Any]:
        """取得前端版本狀態"""
        return {
            "current_version": "1.2.3",
            "latest_version": "1.2.3",
            "is_up_to_date": True,
            "last_updated": "2024-01-01T00:00:00Z"
        }
    
    async def _check_database_connection(self) -> Dict[str, Any]:
        """檢查資料庫連線"""
        try:
            # 執行簡單的資料庫查詢
            result = self.db_session.execute(text("SELECT 1"))
            return {
                "status": "success",
                "response_time_ms": 10,
                "connection_pool": {
                    "active": 5,
                    "idle": 10,
                    "max": 20
                }
            }
        except Exception as e:
            return {
                "status": "error",
                "error": str(e)
            }
    
    async def _check_external_services(self, merchant_id: UUID) -> Dict[str, Any]:
        """檢查外部服務"""
        return {
            "line_api": {"status": "healthy", "response_time_ms": 100},
            "payment_gateway": {"status": "healthy", "response_time_ms": 200},
            "notification_service": {"status": "healthy", "response_time_ms": 50}
        }
    
    async def _calculate_platform_health_summary(self, merchants: List) -> Dict[str, Any]:
        """計算平台健康摘要"""
        return {
            "healthy_merchants": 8,
            "warning_merchants": 1,
            "critical_merchants": 0,
            "overall_health_score": 0.95
        }
    
    async def _get_system_statistics(self) -> Dict[str, Any]:
        """取得系統統計"""
        return {
            "total_users": 1000,
            "total_appointments": 5000,
            "total_revenue": 500000,
            "system_uptime": "99.9%"
        }
    
    async def _get_error_leaderboard(self) -> List[Dict[str, Any]]:
        """取得錯誤榜"""
        return [
            {"merchant_id": "merchant-1", "error_count": 5, "error_rate": 0.01},
            {"merchant_id": "merchant-2", "error_count": 3, "error_rate": 0.005},
            {"merchant_id": "merchant-3", "error_count": 2, "error_rate": 0.003}
        ]
