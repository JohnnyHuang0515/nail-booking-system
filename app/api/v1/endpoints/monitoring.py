"""
監控與健診 API
"""
from fastapi import APIRouter, HTTPException, Depends
from typing import List, Optional, Dict, Any
from uuid import UUID
from pydantic import BaseModel

from app.infrastructure.database.session import get_db_session
from app.services.monitoring_service import MonitoringService

router = APIRouter()


@router.get("/merchants/{merchant_id}/monitoring/webhook-health")
async def get_webhook_health(
    merchant_id: UUID,
    db_session = Depends(get_db_session)
):
    """取得 Webhook 健康狀態"""
    try:
        monitoring_service = MonitoringService(db_session)
        result = await monitoring_service.get_webhook_health(merchant_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得 Webhook 健康狀態失敗: {str(e)}")


@router.get("/merchants/{merchant_id}/monitoring/push-quota")
async def get_push_quota_status(
    merchant_id: UUID,
    db_session = Depends(get_db_session)
):
    """取得推播配額狀態"""
    try:
        monitoring_service = MonitoringService(db_session)
        result = await monitoring_service.get_push_quota_status(merchant_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得推播配額狀態失敗: {str(e)}")


@router.get("/merchants/{merchant_id}/monitoring/task-queue")
async def get_task_queue_status(
    merchant_id: UUID,
    db_session = Depends(get_db_session)
):
    """取得任務排程狀態"""
    try:
        monitoring_service = MonitoringService(db_session)
        result = await monitoring_service.get_task_queue_status(merchant_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得任務排程狀態失敗: {str(e)}")


@router.get("/merchants/{merchant_id}/monitoring/availability")
async def get_availability_status(
    merchant_id: UUID,
    db_session = Depends(get_db_session)
):
    """取得可用性狀態"""
    try:
        monitoring_service = MonitoringService(db_session)
        result = await monitoring_service.get_availability_status(merchant_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得可用性狀態失敗: {str(e)}")


@router.get("/monitoring/overview")
async def get_platform_overview(db_session = Depends(get_db_session)):
    """取得平台總覽監控"""
    try:
        monitoring_service = MonitoringService(db_session)
        result = await monitoring_service.get_platform_overview()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得平台總覽失敗: {str(e)}")


@router.get("/monitoring/merchants/{merchant_id}/comprehensive")
async def get_comprehensive_monitoring(
    merchant_id: UUID,
    db_session = Depends(get_db_session)
):
    """取得商家綜合監控報告"""
    try:
        monitoring_service = MonitoringService(db_session)
        
        # 取得所有監控項目
        webhook_health = await monitoring_service.get_webhook_health(merchant_id)
        push_quota = await monitoring_service.get_push_quota_status(merchant_id)
        task_queue = await monitoring_service.get_task_queue_status(merchant_id)
        availability = await monitoring_service.get_availability_status(merchant_id)
        
        # 計算綜合健康分數
        health_scores = []
        if webhook_health["status"] == "healthy":
            health_scores.append(1.0)
        elif webhook_health["status"] == "warning":
            health_scores.append(0.7)
        else:
            health_scores.append(0.3)
        
        if push_quota["status"] == "success":
            health_scores.append(1.0)
        else:
            health_scores.append(0.5)
        
        if task_queue["status"] == "healthy":
            health_scores.append(1.0)
        elif task_queue["status"] == "warning":
            health_scores.append(0.7)
        else:
            health_scores.append(0.3)
        
        if availability["status"] == "healthy":
            health_scores.append(1.0)
        elif availability["status"] == "warning":
            health_scores.append(0.7)
        else:
            health_scores.append(0.3)
        
        overall_health_score = sum(health_scores) / len(health_scores)
        
        # 判斷整體狀態
        if overall_health_score >= 0.9:
            overall_status = "healthy"
        elif overall_health_score >= 0.7:
            overall_status = "warning"
        else:
            overall_status = "critical"
        
        return {
            "status": "success",
            "merchant_id": str(merchant_id),
            "overall_status": overall_status,
            "overall_health_score": overall_health_score,
            "monitoring_details": {
                "webhook_health": webhook_health,
                "push_quota": push_quota,
                "task_queue": task_queue,
                "availability": availability
            },
            "recommendations": await _generate_recommendations(
                webhook_health, push_quota, task_queue, availability
            ),
            "generated_at": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得綜合監控報告失敗: {str(e)}")


@router.get("/monitoring/alerts")
async def get_monitoring_alerts(
    severity: Optional[str] = None,
    merchant_id: Optional[UUID] = None,
    db_session = Depends(get_db_session)
):
    """取得監控告警"""
    try:
        monitoring_service = MonitoringService(db_session)
        
        # 這裡可以實作告警系統的邏輯
        # 例如：檢查所有商家的健康狀態，找出需要告警的項目
        
        alerts = [
            {
                "id": "alert-1",
                "merchant_id": "merchant-1",
                "severity": "warning",
                "type": "webhook_health",
                "message": "Webhook 成功率低於 95%",
                "created_at": "2024-01-01T00:00:00Z",
                "status": "active"
            },
            {
                "id": "alert-2",
                "merchant_id": "merchant-2",
                "severity": "critical",
                "type": "push_quota",
                "message": "推播配額使用率超過 90%",
                "created_at": "2024-01-01T00:00:00Z",
                "status": "active"
            }
        ]
        
        # 根據參數篩選告警
        if severity:
            alerts = [alert for alert in alerts if alert["severity"] == severity]
        
        if merchant_id:
            alerts = [alert for alert in alerts if alert["merchant_id"] == str(merchant_id)]
        
        return {
            "status": "success",
            "alerts": alerts,
            "total_count": len(alerts),
            "retrieved_at": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得監控告警失敗: {str(e)}")


@router.post("/monitoring/alerts/{alert_id}/acknowledge")
async def acknowledge_alert(
    alert_id: str,
    db_session = Depends(get_db_session)
):
    """確認告警"""
    try:
        # 這裡可以實作告警確認的邏輯
        # 例如：更新告警狀態為已確認
        
        return {
            "status": "success",
            "message": "告警已確認",
            "alert_id": alert_id,
            "acknowledged_at": "2024-01-01T00:00:00Z"
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"確認告警失敗: {str(e)}")


async def _generate_recommendations(
    webhook_health: Dict[str, Any],
    push_quota: Dict[str, Any],
    task_queue: Dict[str, Any],
    availability: Dict[str, Any]
) -> List[str]:
    """產生建議"""
    recommendations = []
    
    # Webhook 健康建議
    if webhook_health["status"] != "healthy":
        if webhook_health.get("success_rate", 1.0) < 0.95:
            recommendations.append("建議檢查 Webhook 端點設定和網路連線")
        if webhook_health.get("error_distribution", {}).get("timeout", 0) > 0:
            recommendations.append("建議優化 Webhook 處理邏輯，減少超時錯誤")
    
    # 推播配額建議
    if push_quota["status"] == "success":
        daily_usage = push_quota.get("daily_usage", {})
        if daily_usage.get("percentage", 0) > 80:
            recommendations.append("推播配額使用率較高，建議監控使用情況")
    
    # 任務排程建議
    if task_queue["status"] != "healthy":
        task_summary = task_queue.get("task_summary", {})
        if task_summary.get("failed", 0) > 0:
            recommendations.append("有任務執行失敗，建議檢查任務日誌")
        if task_summary.get("retry", 0) > 0:
            recommendations.append("有任務需要重試，建議檢查系統負載")
    
    # 可用性建議
    if availability["status"] != "healthy":
        if availability.get("api_error_rate", 0) > 0.01:
            recommendations.append("API 錯誤率較高，建議檢查系統穩定性")
        if availability.get("liff_availability", {}).get("availability_rate", 1.0) < 0.99:
            recommendations.append("LIFF 可用性較低，建議檢查前端部署")
    
    return recommendations
