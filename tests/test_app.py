import copy
from urllib.parse import quote

import pytest
from fastapi.testclient import TestClient

from src.app import activities, app

INITIAL_ACTIVITIES = copy.deepcopy(activities)
client = TestClient(app)


@pytest.fixture(autouse=True)
def reset_activities():
    activities.clear()
    activities.update(copy.deepcopy(INITIAL_ACTIVITIES))
    yield


def test_get_activities_returns_all_activities():
    # Arrange
    expected_activity_name = "Chess Club"

    # Act
    response = client.get("/activities")

    # Assert
    assert response.status_code == 200
    data = response.json()
    assert isinstance(data, dict)
    assert expected_activity_name in data
    assert data[expected_activity_name]["schedule"] == "Fridays, 3:30 PM - 5:00 PM"


def test_signup_for_activity_adds_new_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "test.student@mergington.edu"
    expected_message = f"Signed up {participant_email} for {activity_name}"
    encoded_activity = quote(activity_name, safe="")

    # Act
    response = client.post(
        f"/activities/{encoded_activity}/signup",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": expected_message}
    assert participant_email in activities[activity_name]["participants"]


def test_signup_for_activity_returns_error_for_duplicate_participant():
    # Arrange
    activity_name = "Chess Club"
    existing_email = "michael@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    expected_detail = f"{existing_email} is already signed up for {activity_name}"

    # Act
    response = client.post(
        f"/activities/{encoded_activity}/signup",
        params={"email": existing_email},
    )

    # Assert
    assert response.status_code == 400
    assert response.json()["detail"] == expected_detail


def test_remove_participant_removes_existing_participant():
    # Arrange
    activity_name = "Chess Club"
    participant_email = "michael@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    expected_message = f"Removed {participant_email} from {activity_name}"

    # Act
    response = client.delete(
        f"/activities/{encoded_activity}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 200
    assert response.json() == {"message": expected_message}
    assert participant_email not in activities[activity_name]["participants"]


def test_remove_participant_returns_error_for_missing_participant():
    # Arrange
    activity_name = "Chess Club"
    missing_email = "missing.student@mergington.edu"
    encoded_activity = quote(activity_name, safe="")
    expected_detail = f"{missing_email} is not signed up for {activity_name}"

    # Act
    response = client.delete(
        f"/activities/{encoded_activity}/participants",
        params={"email": missing_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == expected_detail


def test_invalid_activity_signup_returns_not_found():
    # Arrange
    invalid_activity = "Nonexistent Activity"
    participant_email = "ghost.student@mergington.edu"
    encoded_activity = quote(invalid_activity, safe="")
    expected_detail = "Activity not found"

    # Act
    response = client.post(
        f"/activities/{encoded_activity}/signup",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == expected_detail


def test_invalid_activity_remove_participant_returns_not_found():
    # Arrange
    invalid_activity = "Nonexistent Activity"
    participant_email = "ghost.student@mergington.edu"
    encoded_activity = quote(invalid_activity, safe="")
    expected_detail = "Activity not found"

    # Act
    response = client.delete(
        f"/activities/{encoded_activity}/participants",
        params={"email": participant_email},
    )

    # Assert
    assert response.status_code == 404
    assert response.json()["detail"] == expected_detail
