from fastapi import APIRouter, Depends
from pydantic import BaseModel
from typing import Dict

from app.application.dashboard_service import DashboardService
from app.domain.booking.models import Appointment
from app.api.v1.dependencies import get_dashboard_service

router = APIRouter()


class DashboardSummary(BaseModel):
    today_appointments: list[Appointment]
    weekly_summary: Dict[str, int]


@router.get("/dashboard/summary")
def get_dashboard_summary(service: DashboardService = Depends(get_dashboard_service)):
    """Get a summary of data for the admin dashboard."""
    try:
        return service.get_summary()
    except Exception as e:
        print(f"Dashboard error: {e}")
        return {
            "today_appointments": [],
            "weekly_summary": {}
        }
