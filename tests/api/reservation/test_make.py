import pytest
from fastapi.testclient import TestClient
from mock import ANY, AsyncMock


@pytest.mark.asyncio
async def test_no_product(
    test_app_client: TestClient,
    request_payload_q5: dict,
    make_reservation_url: str,
    mock_get_empty_product,
):
    response = test_app_client.post(make_reservation_url, json=request_payload_q5)

    assert response.status_code == 404
    assert response.json() == {
        "message": "Product not found",
        "reservation_id": 123,
        "status": "error",
    }
    assert mock_get_empty_product.assert_awaited_once


@pytest.mark.asyncio
async def test_reservation_product_already_reserved(
    test_app_client: TestClient,
    request_payload_q5: dict,
    make_reservation_url: str,
    mock_get_product: AsyncMock,
    mock_get_reservation: AsyncMock,
    mock_get_product_reservation_q5: AsyncMock,
):
    response = test_app_client.post(make_reservation_url, json=request_payload_q5)

    assert response.status_code == 409
    assert response.json() == {
        "message": "This product is already reserved",
        "reservation_id": 123,
        "status": "error",
    }

    assert mock_get_product.assert_awaited_once
    assert mock_get_reservation.assert_awaited_once
    assert mock_get_product_reservation_q5.assert_awaited_once


@pytest.mark.asyncio
async def test_change_product_reservation_not_enough_products(
    test_app_client: TestClient,
    request_payload_q30: dict,
    make_reservation_url: str,
    mock_get_product: AsyncMock,
    mock_get_reservation: AsyncMock,
    mock_get_product_reservation_q5: AsyncMock,
):
    response = test_app_client.post(make_reservation_url, json=request_payload_q30)

    assert response.status_code == 422
    assert response.json() == {
        "message": "Not enough products available",
        "reservation_id": 123,
        "status": "error",
    }

    assert mock_get_product.assert_awaited_once
    assert mock_get_reservation.assert_awaited_once
    assert mock_get_product_reservation_q5.assert_awaited_once


@pytest.mark.asyncio
async def test_change_product_reservation_successful(
    test_app_client: TestClient,
    request_payload_q7: dict,
    make_reservation_url: str,
    mock_get_product: AsyncMock,
    mock_get_reservation: AsyncMock,
    mock_get_product_reservation_q5: AsyncMock,
):
    response = test_app_client.post(make_reservation_url, json=request_payload_q7)

    assert response.status_code == 200
    assert response.json() == {
        "message": "Reservation created/updated",
        "reservation_id": 123,
        "status": "success",
    }

    assert mock_get_product.assert_awaited_once
    assert mock_get_reservation.assert_awaited_once
    assert mock_get_product_reservation_q5.assert_awaited_once

    assert mock_get_product.return_value.quantity == 8
    assert mock_get_product_reservation_q5.return_value.reservation_quantity == 7


@pytest.mark.asyncio
async def test_add_product_reservation_successful(
    test_app_client: TestClient,
    request_payload_q7: dict,
    make_reservation_url: str,
    mock_get_product: AsyncMock,
    mock_get_reservation: AsyncMock,
    mock_get_empty_product_reservation: AsyncMock,
    mock_add_product_reservation: AsyncMock,
):
    response = test_app_client.post(make_reservation_url, json=request_payload_q7)

    assert response.status_code == 200
    assert response.json() == {
        "message": "Reservation created/updated",
        "reservation_id": 123,
        "status": "success",
    }

    mock_add_product_reservation.assert_awaited_once_with(
        request_payload_q7["reservation_id"],
        request_payload_q7["product_id"],
        request_payload_q7["quantity"],
        ANY,
        ANY,
    )

    mock_get_product.assert_awaited_once()
    mock_get_reservation.assert_awaited_once()
    mock_get_empty_product_reservation.assert_awaited_once()

    assert mock_get_product.return_value.quantity == 3


@pytest.mark.asyncio
async def test_make_reservation_closed(
    test_app_client: TestClient,
    request_payload_q7: dict,
    make_reservation_url: str,
    mock_get_product: AsyncMock,
    mock_get_confirmed_reservation: AsyncMock,
):
    response = test_app_client.post(make_reservation_url, json=request_payload_q7)

    assert response.status_code == 409
    assert response.json() == {
        "message": "Reservation is closed or confirmed",
        "reservation_id": 123,
        "status": "error",
    }
    mock_get_product.assert_awaited_once()
    mock_get_confirmed_reservation.assert_awaited_once()
