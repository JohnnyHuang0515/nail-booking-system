from datetime import datetime
from fastapi.testclient import TestClient


def test_set_and_get_business_hours(test_client: TestClient):
    # Arrange
    business_hours_data = [
        {"day_of_week": 0, "start_time": "09:00:00", "end_time": "18:00:00"}, # Monday
        {"day_of_week": 2, "start_time": "10:00:00", "end_time": "20:00:00"}  # Wednesday
    ]

    # Act: Set business hours
    post_response = test_client.post("/api/v1/schedule/business_hours", json=business_hours_data)

    # Assert: Check post response
    assert post_response.status_code == 200
    posted_data = post_response.json()
    assert len(posted_data) == 2

    # Act: Get business hours
    get_response = test_client.get("/api/v1/schedule/business_hours")

    # Assert: Check get response
    assert get_response.status_code == 200
    retrieved_data = get_response.json()
    assert len(retrieved_data) == 2
    assert any(d["day_of_week"] == 0 for d in retrieved_data)


def test_add_and_delete_time_off(test_client: TestClient):
    # Arrange
    time_off_data = {
        "start_datetime": "2025-10-10T10:00:00Z",
        "end_datetime": "2025-10-10T12:00:00Z",
        "reason": "Doctor's appointment"
    }

    # Act: Add time off
    post_response = test_client.post("/api/v1/schedule/time_off", json=time_off_data)

    # Assert: Check post response
    assert post_response.status_code == 201
    posted_data = post_response.json()
    assert posted_data["reason"] == "Doctor's appointment"
    time_off_id = posted_data["id"]

    # Act: Get time off for that date
    get_response = test_client.get(f"/api/v1/schedule/time_off?for_date=2025-10-10")
    assert get_response.status_code == 200
    assert len(get_response.json()) == 1

    # Act: Delete the time off
    delete_response = test_client.delete(f"/api/v1/schedule/time_off/{time_off_id}")

    # Assert: Check delete response
    assert delete_response.status_code == 204

    # Act: Verify it's gone
    get_after_delete_response = test_client.get(f"/api/v1/schedule/time_off?for_date=2025-10-10")
    assert get_after_delete_response.status_code == 200
    assert len(get_after_delete_response.json()) == 0
