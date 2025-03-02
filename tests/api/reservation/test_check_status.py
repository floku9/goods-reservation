import pytest
from fastapi.testclient import TestClient
from mock import AsyncMock


@pytest.mark.asyncio
async def test_get_reservation_not_found(
    test_app_client: TestClient,
    check_reservation_status_url: str,
    mock_get_empty_reservation: AsyncMock,
):
    response = test_app_client.get(check_reservation_status_url)

    assert response.status_code == 404
    assert response.json() == {
        "message": "Reservation not found",
        "reservation_id": 123,
        "status": "error",
    }
    mock_get_empty_reservation.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_reservation_successful(
    test_app_client: TestClient,
    check_reservation_status_url: str,
    mock_get_reservation: AsyncMock,
):
    response = test_app_client.get(check_reservation_status_url)
    assert response.status_code == 200
    assert response.json() == {
        "message": "Reservation status: pending",
        "reservation_id": 123,
        "status": "success",
    }
    mock_get_reservation.assert_awaited_once()
