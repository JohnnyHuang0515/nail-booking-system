from datetime import date, time, datetime
from sqlalchemy.orm import Session

from app.infrastructure.database.models import Appointment, BusinessHour, TimeOff, User, Service

# Predefined slots for reference
SLOT_1200 = time(12, 0)
SLOT_1500 = time(15, 0)
SLOT_1800 = time(18, 0)


def test_get_available_slots_on_a_free_day(test_client, db_session: Session):
    # Arrange: Set up a normal weekday (Monday)
    db_session.add(BusinessHour(day_of_week=0, start_time=time(10, 0), end_time=time(20, 0)))
    db_session.commit()

    # Act
    response = test_client.get("/api/v1/slots/2025-09-22")  # A Monday

    # Assert
    assert response.status_code == 200
    slots = [time.fromisoformat(s) for s in response.json()]
    assert slots == [SLOT_1200, SLOT_1500, SLOT_1800]


def test_get_available_slots_when_one_is_booked(test_client, db_session: Session):
    # Arrange: A user, a service, and a booking at 15:00
    user = User(line_user_id="test_user_1")
    service = Service(name="Test Service", price=100, duration_minutes=60)
    db_session.add(user)
    db_session.add(service)
    db_session.commit()

    db_session.add(Appointment(
        user_id=user.id,
        service_id=service.id,
        appointment_date=date(2025, 9, 23),  # A Tuesday
        appointment_time=SLOT_1500
    ))
    db_session.add(BusinessHour(day_of_week=1, start_time=time(10, 0), end_time=time(20, 0)))
    db_session.commit()

    # Act
    response = test_client.get("/api/v1/slots/2025-09-23")

    # Assert
    assert response.status_code == 200
    slots = [time.fromisoformat(s) for s in response.json()]
    assert slots == [SLOT_1200, SLOT_1800]


def test_get_available_slots_on_a_closed_day(test_client, db_session: Session):
    # Arrange: No business hours for Wednesday
    # (Assuming db is clean for this test function)

    # Act
    response = test_client.get("/api/v1/slots/2025-09-24")  # A Wednesday

    # Assert
    assert response.status_code == 200
    assert response.json() == []


def test_get_available_slots_with_a_time_off(test_client, db_session: Session):
    # Arrange: Business hours for Thursday, but a time-off blocking the afternoon
    db_session.add(BusinessHour(day_of_week=3, start_time=time(10, 0), end_time=time(20, 0)))
    db_session.add(TimeOff(
        start_datetime=datetime(2025, 9, 25, 14, 0),
        end_datetime=datetime(2025, 9, 25, 17, 0),
        reason="Personal appointment"
    ))
    db_session.commit()

    # Act
    response = test_client.get("/api/v1/slots/2025-09-25")  # A Thursday

    # Assert
    assert response.status_code == 200
    slots = [time.fromisoformat(s) for s in response.json()]
    # 15:00 slot is blocked by the time-off
    assert slots == [SLOT_1200, SLOT_1800]
