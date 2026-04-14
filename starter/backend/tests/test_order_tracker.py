import pytest
from unittest.mock import Mock, call
from ..order_tracker import OrderTracker

# --- Fixtures for Unit Tests ---

@pytest.fixture
def mock_storage():
    """
    Provides a mock storage object for tests.
    This mock will be configured to simulate various storage behaviors.
    """
    mock = Mock()
    # By default, mock get_order to return None (no order found)
    mock.get_order.return_value = None
    # By default, mock get_all_orders to return an empty dict
    mock.get_all_orders.return_value = {}
    return mock

@pytest.fixture
def order_tracker(mock_storage):
    """
    Provides an OrderTracker instance initialized with the mock_storage.
    """
    return OrderTracker(mock_storage)


# --- Tests for add_order ---

def test_add_order_success(order_tracker, mock_storage):
    """Adding a valid order should call save_order with correct order_id and order_data."""
    order_tracker.add_order(
        order_id="ORD-001",
        item_name="Wireless Mouse",
        quantity=2,
        customer_id="CUST-001",
    )
    mock_storage.save_order.assert_called_once_with(
        "ORD-001",
        {
            "item_name": "Wireless Mouse",
            "quantity": 2,
            "customer_id": "CUST-001",
            "status": "pending",
        },
    )


def test_add_order_custom_status(order_tracker, mock_storage):
    """Adding an order with a custom status should save that status instead of the default."""
    order_tracker.add_order(
        order_id="ORD-002",
        item_name="Mechanical Keyboard",
        quantity=1,
        customer_id="CUST-002",
        status="shipped",
    )
    mock_storage.save_order.assert_called_once_with(
        "ORD-002",
        {
            "item_name": "Mechanical Keyboard",
            "quantity": 1,
            "customer_id": "CUST-002",
            "status": "shipped",
        },
    )


def test_add_order_duplicate_id(order_tracker, mock_storage):
    """Adding an order with a duplicate ID should raise ValueError and not call save_order."""
    # Simulate an existing order
    mock_storage.get_order.return_value = {
        "item_name": "Old Item",
        "quantity": 1,
        "customer_id": "CUST-OLD",
        "status": "pending",
    }

    with pytest.raises(ValueError, match="already exists"):
        order_tracker.add_order(
            order_id="ORD-001",
            item_name="New Item",
            quantity=3,
            customer_id="CUST-003",
        )

    mock_storage.save_order.assert_not_called()


def test_add_order_invalid_quantity(order_tracker, mock_storage):
    """Adding an order with a non-positive quantity should raise ValueError and not call save_order."""
    with pytest.raises(ValueError, match="quantity"):
        order_tracker.add_order(
            order_id="ORD-003",
            item_name="Monitor",
            quantity=0,
            customer_id="CUST-004",
        )

    mock_storage.save_order.assert_not_called()

    # Also test negative quantity
    with pytest.raises(ValueError, match="quantity"):
        order_tracker.add_order(
            order_id="ORD-004",
            item_name="Monitor",
            quantity=-5,
            customer_id="CUST-005",
        )

    mock_storage.save_order.assert_not_called()


def test_add_order_missing_fields(order_tracker, mock_storage):
    """Adding an order with blank required fields should raise ValueError."""
    # Blank item_name
    with pytest.raises(ValueError, match="item_name"):
        order_tracker.add_order(
            order_id="ORD-005",
            item_name="",
            quantity=1,
            customer_id="CUST-006",
        )
    mock_storage.save_order.assert_not_called()

    # Blank customer_id
    with pytest.raises(ValueError, match="customer_id"):
        order_tracker.add_order(
            order_id="ORD-006",
            item_name="Webcam",
            quantity=1,
            customer_id="",
        )
    mock_storage.save_order.assert_not_called()

    # Blank order_id
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.add_order(
            order_id="",
            item_name="Webcam",
            quantity=1,
            customer_id="CUST-007",
        )
    mock_storage.save_order.assert_not_called()
