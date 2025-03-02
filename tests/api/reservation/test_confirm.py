import pytest
from fastapi.testclient import TestClient
from mock import AsyncMock


@pytest.mark.asyncio
async def test_confirm_reservation_successful(
    test_app_client: TestClient,
    confirm_reservation_url: str,
    mock_get_reservation: AsyncMock,
):
    response = test_app_client.put(confirm_reservation_url)

    assert response.status_code == 200
    assert response.json() == {
        "message": "Reservation confirmed",
        "reservation_id": 123,
        "status": "success",
    }

    assert mock_get_reservation.assert_awaited_once
    assert mock_get_reservation.return_value.status == "confirmed"


@pytest.mark.asyncio
async def test_confirm_reservation_not_found(
    test_app_client: TestClient,
    confirm_reservation_url: str,
    mock_get_empty_reservation: AsyncMock,
):
    response = test_app_client.put(confirm_reservation_url)

    assert response.status_code == 404
    assert response.json() == {
        "message": "Reservation not found",
        "reservation_id": 123,
        "status": "error",
    }
    assert mock_get_empty_reservation.assert_awaited_once


@pytest.mark.asyncio
async def test_confirm_reservation_already_confirmed(
    test_app_client: TestClient,
    confirm_reservation_url: str,
    mock_get_confirmed_reservation: AsyncMock,
):
    response = test_app_client.put(confirm_reservation_url)
    assert response.status_code == 409
    assert response.json() == {
        "message": "Reservation is closed or confirmed",
        "reservation_id": 123,
        "status": "error",
    }
    assert mock_get_confirmed_reservation.assert_awaited_once
