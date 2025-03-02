from datetime import datetime

import pytest
from fastapi.testclient import TestClient
from mock import AsyncMock, patch

from app.db.models import Product, ProductReservation, Reservation
from app.dependencies import get_db_session
from app.main import app


@pytest.fixture
def make_reservation_url():
    return "reservation/make"


@pytest.fixture
def check_reservation_status_url():
    return "reservation/status/123"


@pytest.fixture
def confirm_reservation_url():
    return "reservation/confirm/123"


@pytest.fixture()
def fake_reservation():
    return Reservation(id=123, status="pending")


@pytest.fixture()
def fake_confirmed_reservation():
    return Reservation(id=123, status="confirmed")


@pytest.fixture()
def fake_product():
    return Product(id=456, name="Product", price=100, quantity=10)


@pytest.fixture()
def fake_product_reservation_q5():
    return ProductReservation(
        id=789,
        product_id=456,
        reservation_id=123,
        reservation_quantity=5,
        date=datetime(2025, 1, 1),
    )


@pytest.fixture
def request_payload_q5():
    return {
        "reservation_id": 123,
        "product_id": 456,
        "quantity": 5,
        "timestamp": "2025-01-23T10:20:30.400+02:30",
    }


@pytest.fixture
def request_payload_q30():
    return {
        "reservation_id": 123,
        "product_id": 456,
        "quantity": 30,
        "timestamp": "2025-01-23T10:20:30.400+02:30",
    }


@pytest.fixture
def request_payload_q7():
    return {
        "reservation_id": 123,
        "product_id": 456,
        "quantity": 7,
        "timestamp": "2025-01-23T10:20:30.400+02:30",
    }


@pytest.fixture()
def test_app_client(test_db_session) -> TestClient:
    app.dependency_overrides[get_db_session] = lambda: test_db_session
    test_client = TestClient(app)
    return test_client


@pytest.fixture()
def mock_get_empty_product(mocker):
    with patch("app.routes.get_product") as mock:
        mock.return_value = None
        yield mock


@pytest.fixture()
def mock_get_product(mocker, fake_product):
    with patch("app.routes.get_product") as mock:
        mock.return_value = fake_product
        yield mock


@pytest.fixture()
def mock_get_empty_reservation(mocker):
    with patch("app.routes.get_reservation") as mock:
        mock.return_value = None
        yield mock


@pytest.fixture()
def mock_get_reservation(mocker, fake_reservation):
    with patch("app.routes.get_reservation") as mock:
        mock.return_value = fake_reservation
        yield mock


@pytest.fixture()
def mock_add_reservation(mocker, fake_reservation):
    with patch("app.routes.add_reservation") as mock:
        mock.return_value = fake_reservation
        yield mock


@pytest.fixture()
def mock_get_product_reservation_q5(mocker, fake_product_reservation_q5):
    with patch("app.routes.get_product_reservation") as mock:
        mock.return_value = fake_product_reservation_q5
        yield mock


@pytest.fixture()
def mock_get_empty_product_reservation(mocker):
    with patch("app.routes.get_product_reservation") as mock:
        mock.return_value = None
        yield mock


@pytest.fixture
def mock_add_product_reservation(mocker):
    """
    Fixture to mock add_product_reservation with a side_effect that simulates
    creating a ProductReservation object based on passed arguments.
    """

    def create_product_reservation(reservation_id, product_id, quantity, date, session):
        product_reservation = ProductReservation(
            id=1,
            reservation_id=reservation_id,
            product_id=product_id,
            reservation_quantity=quantity,
            date=date,
        )
        return product_reservation

    with patch("app.routes.add_product_reservation", new_callable=AsyncMock) as mock:
        mock.side_effect = create_product_reservation
        yield mock


@pytest.fixture()
def mock_get_confirmed_reservation(mocker, fake_confirmed_reservation):
    with patch("app.routes.get_reservation") as mock:
        mock.return_value = fake_confirmed_reservation
        yield mock
