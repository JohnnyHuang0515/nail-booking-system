"""
資料與報表 API
"""
from fastapi import APIRouter, HTTPException, Depends, Response
from typing import List, Optional, Dict, Any
from uuid import UUID
from datetime import datetime, timedelta
from pydantic import BaseModel

from app.infrastructure.database.session import get_db_session
from app.services.reporting_service import ReportingService

router = APIRouter()


class DateRangeRequest(BaseModel):
    """日期範圍請求"""
    start_date: Optional[datetime] = None
    end_date: Optional[datetime] = None


@router.get("/reports/merchant-statistics")
async def get_merchant_statistics(db_session = Depends(get_db_session)):
    """取得商家統計"""
    try:
        reporting_service = ReportingService(db_session)
        result = await reporting_service.get_merchant_statistics()
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得商家統計失敗: {str(e)}")


@router.get("/merchants/{merchant_id}/reports/business-metrics")
async def get_business_metrics(
    merchant_id: UUID,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db_session = Depends(get_db_session)
):
    """取得業務指標"""
    try:
        reporting_service = ReportingService(db_session)
        result = await reporting_service.get_business_metrics(merchant_id, start_date, end_date)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得業務指標失敗: {str(e)}")


@router.get("/merchants/{merchant_id}/reports/customer-scale")
async def get_customer_scale_analysis(
    merchant_id: UUID,
    db_session = Depends(get_db_session)
):
    """取得顧客規模分析"""
    try:
        reporting_service = ReportingService(db_session)
        result = await reporting_service.get_customer_scale_analysis(merchant_id)
        
        return result
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得顧客規模分析失敗: {str(e)}")


@router.get("/reports/export/merchant-list")
async def export_merchant_list(db_session = Depends(get_db_session)):
    """匯出商家清單"""
    try:
        reporting_service = ReportingService(db_session)
        csv_content = await reporting_service.export_merchant_list()
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=merchant_list.csv"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"匯出商家清單失敗: {str(e)}")


@router.get("/reports/export/credentials-list")
async def export_credentials_list(db_session = Depends(get_db_session)):
    """匯出憑證清單（遮蔽後）"""
    try:
        reporting_service = ReportingService(db_session)
        csv_content = await reporting_service.export_credentials_list()
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=credentials_list.csv"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"匯出憑證清單失敗: {str(e)}")


@router.get("/reports/export/operational-report")
async def export_operational_report(
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    db_session = Depends(get_db_session)
):
    """匯出營運報表"""
    try:
        reporting_service = ReportingService(db_session)
        csv_content = await reporting_service.export_operational_report(start_date, end_date)
        
        return Response(
            content=csv_content,
            media_type="text/csv",
            headers={"Content-Disposition": "attachment; filename=operational_report.csv"}
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"匯出營運報表失敗: {str(e)}")


@router.get("/reports/dashboard")
async def get_dashboard_data(db_session = Depends(get_db_session)):
    """取得儀表板資料"""
    try:
        reporting_service = ReportingService(db_session)
        
        # 取得各種統計資料
        merchant_stats = await reporting_service.get_merchant_statistics()
        
        # 這裡可以添加更多儀表板資料
        # 例如：平台總覽、趨勢分析、熱門服務等
        
        return {
            "status": "success",
            "dashboard_data": {
                "merchant_statistics": merchant_stats,
                "platform_overview": {
                    "total_revenue": 1000000,
                    "total_appointments": 5000,
                    "total_customers": 1000,
                    "system_uptime": "99.9%"
                },
                "trends": {
                    "revenue_growth": 15.5,
                    "customer_growth": 8.2,
                    "appointment_growth": 12.1
                },
                "top_services": [
                    {"name": "基礎美甲", "count": 500, "revenue": 400000},
                    {"name": "法式美甲", "count": 300, "revenue": 360000},
                    {"name": "彩繪美甲", "count": 200, "revenue": 300000}
                ]
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得儀表板資料失敗: {str(e)}")


@router.get("/reports/analytics/trends")
async def get_analytics_trends(
    period: str = "30d",
    db_session = Depends(get_db_session)
):
    """取得趨勢分析"""
    try:
        # 根據期間計算日期範圍
        if period == "7d":
            days = 7
        elif period == "30d":
            days = 30
        elif period == "90d":
            days = 90
        else:
            days = 30
        
        end_date = datetime.now()
        start_date = end_date - timedelta(days=days)
        
        reporting_service = ReportingService(db_session)
        
        # 這裡可以實作趨勢分析邏輯
        # 例如：每日營收趨勢、預約趨勢、用戶增長趨勢等
        
        return {
            "status": "success",
            "period": period,
            "date_range": {
                "start_date": start_date.isoformat(),
                "end_date": end_date.isoformat()
            },
            "trends": {
                "revenue": [
                    {"date": "2024-01-01", "value": 10000},
                    {"date": "2024-01-02", "value": 12000},
                    {"date": "2024-01-03", "value": 15000}
                ],
                "appointments": [
                    {"date": "2024-01-01", "value": 50},
                    {"date": "2024-01-02", "value": 60},
                    {"date": "2024-01-03", "value": 75}
                ],
                "customers": [
                    {"date": "2024-01-01", "value": 100},
                    {"date": "2024-01-02", "value": 105},
                    {"date": "2024-01-03", "value": 110}
                ]
            },
            "generated_at": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得趨勢分析失敗: {str(e)}")


@router.get("/reports/analytics/performance")
async def get_performance_analytics(
    merchant_id: Optional[UUID] = None,
    db_session = Depends(get_db_session)
):
    """取得性能分析"""
    try:
        reporting_service = ReportingService(db_session)
        
        if merchant_id:
            # 單一商家性能分析
            business_metrics = await reporting_service.get_business_metrics(merchant_id)
            customer_scale = await reporting_service.get_customer_scale_analysis(merchant_id)
            
            return {
                "status": "success",
                "merchant_id": str(merchant_id),
                "performance": {
                    "business_metrics": business_metrics,
                    "customer_scale": customer_scale,
                    "performance_score": 85.5,
                    "rank": 3
                },
                "generated_at": datetime.now().isoformat()
            }
        else:
            # 平台整體性能分析
            merchant_stats = await reporting_service.get_merchant_statistics()
            
            return {
                "status": "success",
                "platform_performance": {
                    "merchant_statistics": merchant_stats,
                    "overall_score": 88.2,
                    "top_performers": [
                        {"merchant_id": "merchant-1", "score": 95.0, "name": "台北時尚美甲"},
                        {"merchant_id": "merchant-2", "score": 92.5, "name": "高雄藝術美甲"},
                        {"merchant_id": "merchant-3", "score": 90.0, "name": "台中精品美甲"}
                    ]
                },
                "generated_at": datetime.now().isoformat()
            }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"取得性能分析失敗: {str(e)}")
