from datetime import date, timedelta, time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infrastructure.database.models import User, Service, Appointment


def test_get_dashboard_summary(test_client: TestClient, db_session: Session):
    # Arrange: Create a user and service
    user = User(line_user_id="dashboard_test_user")
    service = Service(name="Dashboard Test Service", price=100, duration_minutes=60)
    db_session.add(user)
    db_session.add(service)
    db_session.commit()

    # Arrange: Create an appointment for today
    today = date.today()
    db_session.add(Appointment(
        user_id=user.id,
        service_id=service.id,
        appointment_date=today,
        appointment_time=time(12, 0)
    ))
    db_session.commit()

    # Act
    response = test_client.get("/api/v1/dashboard/summary")

    # Assert
    assert response.status_code == 200
    data = response.json()
    
    # Check today's appointments
    assert len(data["today_appointments"]) == 1
    assert data["today_appointments"][0]["user_id"] == str(user.id)

    # Check weekly summary
    today_iso = today.isoformat()
    assert data["weekly_summary"][today_iso] == 1
