from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, date
import uuid

from app.infrastructure.database.session import get_db_session
from app.infrastructure.database.models import BillingRecord, Merchant
from app.schemas.billing import BillingRecordResponse, BillingSummaryResponse

router = APIRouter()


@router.get("/billing/records", response_model=List[BillingRecordResponse])
async def get_billing_records(
    merchant_id: Optional[str] = Query(None, description="Filter by merchant ID"),
    status: Optional[str] = Query(None, description="Filter by status (paid, pending, overdue)"),
    start_date: Optional[str] = Query(None, description="Start date for filtering (YYYY-MM-DD)"),
    end_date: Optional[str] = Query(None, description="End date for filtering (YYYY-MM-DD)"),
    db: Session = Depends(get_db_session)
):
    """Get all billing records with optional filtering."""
    try:
        query = db.query(BillingRecord)
        
        # 應用篩選條件
        if merchant_id:
            query = query.filter(BillingRecord.merchant_id == merchant_id)
        
        if status:
            query = query.filter(BillingRecord.status == status)
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(BillingRecord.billing_period_start >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(BillingRecord.billing_period_end <= end_dt)
        
        # 按創建時間降序排列
        records = query.order_by(BillingRecord.created_at.desc()).all()
        
        result = []
        for record in records:
            # 獲取商家名稱
            merchant = db.query(Merchant).filter(Merchant.id == record.merchant_id).first()
            merchant_name = merchant.name if merchant else "未知商家"
            
            result.append(BillingRecordResponse(
                id=str(record.id),
                merchant_id=str(record.merchant_id),
                merchant_name=merchant_name,
                plan=record.plan,
                amount=float(record.amount),
                status=record.status,
                billing_period=f"{record.billing_period_start.strftime('%Y-%m-%d')} 至 {record.billing_period_end.strftime('%Y-%m-%d')}",
                due_date=record.due_date.isoformat(),
                paid_at=record.paid_at.isoformat() if record.paid_at else None,
                created_at=record.created_at.isoformat()
            ))
        
        return result
    except Exception as e:
        print(f"Get billing records error: {e}")
        import traceback
        traceback.print_exc()
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/billing/summary", response_model=BillingSummaryResponse)
async def get_billing_summary(
    db: Session = Depends(get_db_session)
):
    """Get billing summary statistics."""
    try:
        # 計算總收入
        total_revenue_records = db.query(BillingRecord).filter(
            BillingRecord.status == "paid"
        ).with_entities(BillingRecord.amount).all()
        total_revenue_sum = sum(float(record.amount) for record in total_revenue_records)
        
        # 計算待收款
        pending_records = db.query(BillingRecord).filter(
            BillingRecord.status == "pending"
        ).with_entities(BillingRecord.amount).all()
        pending_sum = sum(float(record.amount) for record in pending_records)
        
        # 計算逾期金額
        overdue_records = db.query(BillingRecord).filter(
            BillingRecord.status == "overdue"
        ).with_entities(BillingRecord.amount).all()
        overdue_sum = sum(float(record.amount) for record in overdue_records)
        
        # 計算活躍商家數量
        active_merchants = len(db.query(BillingRecord).filter(
            BillingRecord.status == "paid"
        ).distinct(BillingRecord.merchant_id).all())
        
        return BillingSummaryResponse(
            total_revenue=total_revenue_sum,
            pending_amount=pending_sum,
            overdue_amount=overdue_sum,
            active_merchants=active_merchants
        )
    except Exception as e:
        print(f"Get billing summary error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")


@router.get("/billing/export")
async def export_billing_records(
    format: str = Query("csv", description="Export format (csv, json)"),
    merchant_id: Optional[str] = Query(None, description="Filter by merchant ID"),
    status: Optional[str] = Query(None, description="Filter by status"),
    start_date: Optional[str] = Query(None, description="Start date for filtering"),
    end_date: Optional[str] = Query(None, description="End date for filtering"),
    db: Session = Depends(get_db_session)
):
    """Export billing records in specified format."""
    try:
        # 使用相同的查詢邏輯
        query = db.query(BillingRecord)
        
        if merchant_id:
            query = query.filter(BillingRecord.merchant_id == merchant_id)
        
        if status:
            query = query.filter(BillingRecord.status == status)
        
        if start_date:
            start_dt = datetime.strptime(start_date, "%Y-%m-%d").date()
            query = query.filter(BillingRecord.billing_period_start >= start_dt)
        
        if end_date:
            end_dt = datetime.strptime(end_date, "%Y-%m-%d").date()
            query = query.filter(BillingRecord.billing_period_end <= end_dt)
        
        records = query.order_by(BillingRecord.created_at.desc()).all()
        
        if format == "csv":
            # 生成 CSV 內容
            csv_content = "商家ID,商家名稱,方案,金額,狀態,帳單期間,到期日,付款日期,創建時間\n"
            
            for record in records:
                merchant = db.query(Merchant).filter(Merchant.id == record.merchant_id).first()
                merchant_name = merchant.name if merchant else "未知商家"
                
                csv_content += f"{record.merchant_id},{merchant_name},{record.plan},{record.amount},{record.status},"
                csv_content += f"{record.billing_period_start.strftime('%Y-%m-%d')} 至 {record.billing_period_end.strftime('%Y-%m-%d')},"
                csv_content += f"{record.due_date.isoformat()},"
                csv_content += f"{record.paid_at.isoformat() if record.paid_at else ''},"
                csv_content += f"{record.created_at.isoformat()}\n"
            
            return {"content": csv_content, "content_type": "text/csv"}
        
        elif format == "json":
            # 生成 JSON 內容
            result = []
            for record in records:
                merchant = db.query(Merchant).filter(Merchant.id == record.merchant_id).first()
                merchant_name = merchant.name if merchant else "未知商家"
                
                result.append({
                    "id": record.id,
                    "merchant_id": record.merchant_id,
                    "merchant_name": merchant_name,
                    "plan": record.plan,
                    "amount": record.amount,
                    "status": record.status,
                    "billing_period_start": record.billing_period_start.isoformat(),
                    "billing_period_end": record.billing_period_end.isoformat(),
                    "due_date": record.due_date.isoformat(),
                    "paid_at": record.paid_at.isoformat() if record.paid_at else None,
                    "created_at": record.created_at.isoformat()
                })
            
            return {"content": result, "content_type": "application/json"}
        
        else:
            raise HTTPException(status_code=400, detail="Unsupported export format")
            
    except Exception as e:
        print(f"Export billing records error: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
