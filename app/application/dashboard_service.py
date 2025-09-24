from datetime import date, timedelta
from app.domain.booking.repository import AbstractAppointmentRepository


class DashboardService:
    def __init__(self, appointment_repo: AbstractAppointmentRepository):
        self.appointment_repo = appointment_repo

    def get_summary(self):
        today = date.today()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)

        # Get appointments for today and this week
        today_appointments = self.appointment_repo.list_by_date(today)
        week_appointments = self.appointment_repo.list_by_date_range(start_of_week, end_of_week)

        # Calculate weekly summary
        weekly_summary = { (start_of_week + timedelta(days=i)).isoformat(): 0 for i in range(7) }
        for appt in week_appointments:
            day_str = appt.appointment_date.isoformat()
            if day_str in weekly_summary:
                weekly_summary[day_str] += 1
        
        return {
            "today_appointments": today_appointments,
            "weekly_summary": weekly_summary,
        }
