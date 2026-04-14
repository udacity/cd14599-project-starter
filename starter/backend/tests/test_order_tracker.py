import pytest
from unittest.mock import Mock, call
from ..order_tracker import OrderTracker, VALID_STATUSES

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


# --- Tests for get_order_by_id ---

def test_get_order_by_id_success(order_tracker, mock_storage):
    """Retrieving an existing order should return the order data with order_id included."""
    mock_storage.get_order.return_value = {
        "item_name": "Wireless Mouse",
        "quantity": 2,
        "customer_id": "CUST-001",
        "status": "pending",
    }

    result = order_tracker.get_order_by_id("ORD-001")

    mock_storage.get_order.assert_called_once_with("ORD-001")
    assert result is not None
    assert result["order_id"] == "ORD-001"
    assert result["item_name"] == "Wireless Mouse"
    assert result["quantity"] == 2
    assert result["customer_id"] == "CUST-001"
    assert result["status"] == "pending"


def test_get_order_by_id_not_found(order_tracker, mock_storage):
    """Retrieving a non-existent order should return None."""
    mock_storage.get_order.return_value = None

    result = order_tracker.get_order_by_id("ORD-NONEXISTENT")

    mock_storage.get_order.assert_called_once_with("ORD-NONEXISTENT")
    assert result is None


def test_get_order_by_id_empty_string(order_tracker, mock_storage):
    """Retrieving an order with an empty order_id should raise ValueError."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.get_order_by_id("")

    mock_storage.get_order.assert_not_called()


def test_get_order_by_id_whitespace_only(order_tracker, mock_storage):
    """Retrieving an order with a whitespace-only order_id should raise ValueError."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.get_order_by_id("   ")

    mock_storage.get_order.assert_not_called()


def test_get_order_by_id_non_string_type(order_tracker, mock_storage):
    """Retrieving an order with a non-string order_id should raise ValueError."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.get_order_by_id(12345)

    mock_storage.get_order.assert_not_called()


def test_get_order_by_id_none_value(order_tracker, mock_storage):
    """Retrieving an order with None as order_id should raise ValueError."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.get_order_by_id(None)

    mock_storage.get_order.assert_not_called()


# --- Tests for update_order_status ---

def test_update_order_status_success(order_tracker, mock_storage):
    """Successfully updating an order's status should call save_order with the updated order data."""
    # Simulate an existing order with "pending" status
    mock_storage.get_order.return_value = {
        "item_name": "Wireless Mouse",
        "quantity": 2,
        "customer_id": "CUST-001",
        "status": "pending",
    }

    order_tracker.update_order_status("ORD-001", "shipped")

    # Verify get_order was called with the correct order_id
    mock_storage.get_order.assert_called_once_with("ORD-001")

    # Verify save_order was called with the updated order data
    mock_storage.save_order.assert_called_once_with(
        "ORD-001",
        {
            "item_name": "Wireless Mouse",
            "quantity": 2,
            "customer_id": "CUST-001",
            "status": "shipped",
        },
    )


def test_update_order_status_preserves_all_fields(order_tracker, mock_storage):
    """Updating status should preserve item_name, quantity, and customer_id unchanged."""
    original_order = {
        "item_name": "Mechanical Keyboard",
        "quantity": 5,
        "customer_id": "CUST-042",
        "status": "processing",
    }
    mock_storage.get_order.return_value = original_order

    order_tracker.update_order_status("ORD-042", "delivered")

    # Extract the saved order data from the mock call
    call_args = mock_storage.save_order.call_args
    saved_order = call_args[0][1]

    assert saved_order["item_name"] == "Mechanical Keyboard"
    assert saved_order["quantity"] == 5
    assert saved_order["customer_id"] == "CUST-042"
    assert saved_order["status"] == "delivered"


def test_update_order_status_nonexistent_order(order_tracker, mock_storage):
    """Updating a non-existent order should raise ValueError and not call save_order."""
    # By default, mock_storage.get_order returns None (order not found)

    with pytest.raises(ValueError, match="does not exist"):
        order_tracker.update_order_status("ORD-NONEXISTENT", "shipped")

    mock_storage.save_order.assert_not_called()


def test_update_order_status_invalid_status(order_tracker, mock_storage):
    """Updating with an invalid status value should raise ValueError and not call save_order."""
    mock_storage.get_order.return_value = {
        "item_name": "Wireless Mouse",
        "quantity": 2,
        "customer_id": "CUST-001",
        "status": "pending",
    }

    with pytest.raises(ValueError, match="status"):
        order_tracker.update_order_status("ORD-001", "invalid_status")

    mock_storage.save_order.assert_not_called()


def test_update_order_status_empty_order_id(order_tracker, mock_storage):
    """Updating with an empty order_id should raise ValueError without calling storage methods."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.update_order_status("", "shipped")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_whitespace_order_id(order_tracker, mock_storage):
    """Updating with a whitespace-only order_id should raise ValueError without calling storage methods."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.update_order_status("   ", "shipped")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_none_order_id(order_tracker, mock_storage):
    """Updating with None as order_id should raise ValueError without calling storage methods."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.update_order_status(None, "shipped")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_non_string_order_id(order_tracker, mock_storage):
    """Updating with a non-string order_id should raise ValueError without calling storage methods."""
    with pytest.raises(ValueError, match="order_id"):
        order_tracker.update_order_status(12345, "shipped")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_empty_new_status(order_tracker, mock_storage):
    """Updating with an empty new_status should raise ValueError and not call storage methods."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.update_order_status("ORD-001", "")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_whitespace_new_status(order_tracker, mock_storage):
    """Updating with a whitespace-only new_status should raise ValueError and not call storage methods."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.update_order_status("ORD-001", "   ")

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_none_new_status(order_tracker, mock_storage):
    """Updating with None as new_status should raise ValueError and not call storage methods."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.update_order_status("ORD-001", None)

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_non_string_new_status(order_tracker, mock_storage):
    """Updating with a non-string new_status should raise ValueError and not call storage methods."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.update_order_status("ORD-001", 42)

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_all_valid_transitions(order_tracker, mock_storage):
    """Any transition between valid statuses should be allowed."""
    mock_storage.get_order.return_value = {
        "item_name": "Test Item",
        "quantity": 1,
        "customer_id": "CUST-001",
        "status": "pending",
    }

    # Test transitioning from pending to every other valid status
    for new_status in VALID_STATUSES - {"pending"}:
        mock_storage.reset_mock()
        mock_storage.get_order.return_value = {
            "item_name": "Test Item",
            "quantity": 1,
            "customer_id": "CUST-001",
            "status": "pending",
        }
        order_tracker.update_order_status("ORD-001", new_status)
        call_args = mock_storage.save_order.call_args
        assert call_args[0][1]["status"] == new_status
