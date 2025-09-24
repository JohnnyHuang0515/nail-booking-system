import uuid
from datetime import date, time
from fastapi.testclient import TestClient
from sqlalchemy.orm import Session

from app.infrastructure.database.models import User, Service


def setup_user_and_service(db_session: Session) -> (uuid.UUID, uuid.UUID):
    user = User(line_user_id="appointment_test_user")
    service = Service(name="Appointment Test Service", price=100, duration_minutes=60)
    db_session.add(user)
    db_session.add(service)
    db_session.commit()
    return user.id, service.id


def test_create_and_get_appointment(test_client: TestClient, db_session: Session):
    # Arrange
    user_id, service_id = setup_user_and_service(db_session)
    appointment_data = {
        "user_id": str(user_id),
        "service_id": str(service_id),
        "appointment_date": "2025-11-11",
        "appointment_time": "15:00:00"
    }

    # Act: Create appointment
    create_response = test_client.post("/api/v1/appointments", json=appointment_data)

    # Assert: Check create response
    assert create_response.status_code == 201
    created_data = create_response.json()
    assert created_data["user_id"] == str(user_id)
    appointment_id = created_data["id"]

    # Act: Get appointments for that date range
    get_response = test_client.get("/api/v1/appointments?start_date=2025-11-10&end_date=2025-11-12")

    # Assert: Check get response
    assert get_response.status_code == 200
    retrieved_data = get_response.json()
    assert len(retrieved_data) == 1
    assert retrieved_data[0]["id"] == appointment_id


def test_update_and_delete_appointment(test_client: TestClient, db_session: Session):
    # Arrange
    user_id, service_id = setup_user_and_service(db_session)
    create_response = test_client.post("/api/v1/appointments", json={
        "user_id": str(user_id),
        "service_id": str(service_id),
        "appointment_date": "2025-12-12",
        "appointment_time": "12:00:00"
    })
    appointment_id = create_response.json()["id"]

    # Act: Update status
    update_response = test_client.put(f"/api/v1/appointments/{appointment_id}/status", json={"status": "completed"})

    # Assert: Check update response
    assert update_response.status_code == 200
    assert update_response.json()["status"] == "completed"

    # Act: Delete the appointment
    delete_response = test_client.delete(f"/api/v1/appointments/{appointment_id}")

    # Assert: Check delete response
    assert delete_response.status_code == 204
