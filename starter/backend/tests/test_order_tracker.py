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
    """Updating with None as new_status should raise ValueError without calling storage methods."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.update_order_status("ORD-001", None)

    mock_storage.get_order.assert_not_called()
    mock_storage.save_order.assert_not_called()


def test_update_order_status_non_string_new_status(order_tracker, mock_storage):
    """Updating with a non-string new_status should raise ValueError without calling storage methods."""
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


# --- Tests for list_all_orders ---

def test_list_all_orders_returns_all_orders(order_tracker, mock_storage):
    """list_all_orders should return a list of all orders with order_id merged in."""
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {"item_name": "Wireless Mouse", "quantity": 2, "customer_id": "CUST-001", "status": "pending"},
        "ORD-002": {"item_name": "Mechanical Keyboard", "quantity": 1, "customer_id": "CUST-002", "status": "shipped"},
    }

    result = order_tracker.list_all_orders()

    assert isinstance(result, list)
    assert len(result) == 2

    # Verify each order has order_id merged
    order_ids = {order["order_id"] for order in result}
    assert order_ids == {"ORD-001", "ORD-002"}

    # Verify all expected fields are present in each order
    for order in result:
        assert "order_id" in order
        assert "item_name" in order
        assert "quantity" in order
        assert "customer_id" in order
        assert "status" in order


def test_list_all_orders_empty_storage(order_tracker, mock_storage):
    """list_all_orders should return an empty list when storage has no orders."""
    mock_storage.get_all_orders.return_value = {}

    result = order_tracker.list_all_orders()

    assert result == []


def test_list_all_orders_single_order(order_tracker, mock_storage):
    """list_all_orders should return a list with one order when storage has one order."""
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {"item_name": "Monitor", "quantity": 3, "customer_id": "CUST-010", "status": "delivered"},
    }

    result = order_tracker.list_all_orders()

    assert len(result) == 1
    assert result[0]["order_id"] == "ORD-001"
    assert result[0]["item_name"] == "Monitor"
    assert result[0]["quantity"] == 3
    assert result[0]["customer_id"] == "CUST-010"
    assert result[0]["status"] == "delivered"


def test_list_all_orders_calls_get_all_orders(order_tracker, mock_storage):
    """list_all_orders should call storage.get_all_orders exactly once."""
    mock_storage.get_all_orders.return_value = {}

    order_tracker.list_all_orders()

    mock_storage.get_all_orders.assert_called_once()


def test_list_all_orders_returns_copies(order_tracker, mock_storage):
    """list_all_orders should return copies of order data, not references to storage data."""
    original_order = {"item_name": "Test", "quantity": 1, "customer_id": "C-1", "status": "pending"}
    mock_storage.get_all_orders.return_value = {"ORD-001": original_order}

    result = order_tracker.list_all_orders()

    # Mutating the returned result should not affect the original storage data
    result[0]["item_name"] = "Mutated"

    assert original_order["item_name"] == "Test"


# --- Tests for list_orders_by_status ---

def test_list_orders_by_status_success(order_tracker, mock_storage):
    """list_orders_by_status should return only orders matching the given status."""
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {"item_name": "Wireless Mouse", "quantity": 2, "customer_id": "CUST-001", "status": "shipped"},
        "ORD-002": {"item_name": "Mechanical Keyboard", "quantity": 1, "customer_id": "CUST-002", "status": "pending"},
        "ORD-003": {"item_name": "Monitor", "quantity": 1, "customer_id": "CUST-003", "status": "shipped"},
    }

    result = order_tracker.list_orders_by_status("shipped")

    assert isinstance(result, list)
    assert len(result) == 2
    order_ids = {order["order_id"] for order in result}
    assert order_ids == {"ORD-001", "ORD-003"}

    for order in result:
        assert order["status"] == "shipped"
        assert "order_id" in order
        assert "item_name" in order
        assert "quantity" in order
        assert "customer_id" in order


def test_list_orders_by_status_empty_storage(order_tracker, mock_storage):
    """list_orders_by_status should return an empty list when storage has no orders."""
    mock_storage.get_all_orders.return_value = {}

    result = order_tracker.list_orders_by_status("pending")

    assert result == []


def test_list_orders_by_status_no_matching_orders(order_tracker, mock_storage):
    """list_orders_by_status should return an empty list when no orders match the status."""
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {"item_name": "Wireless Mouse", "quantity": 2, "customer_id": "CUST-001", "status": "pending"},
        "ORD-002": {"item_name": "Mechanical Keyboard", "quantity": 1, "customer_id": "CUST-002", "status": "processing"},
    }

    result = order_tracker.list_orders_by_status("shipped")

    assert result == []


def test_list_orders_by_status_single_match(order_tracker, mock_storage):
    """list_orders_by_status should return a single order when only one matches."""
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {"item_name": "Wireless Mouse", "quantity": 2, "customer_id": "CUST-001", "status": "delivered"},
        "ORD-002": {"item_name": "Mechanical Keyboard", "quantity": 1, "customer_id": "CUST-002", "status": "pending"},
    }

    result = order_tracker.list_orders_by_status("delivered")

    assert len(result) == 1
    assert result[0]["order_id"] == "ORD-001"
    assert result[0]["status"] == "delivered"


def test_list_orders_by_status_all_valid_statuses(order_tracker, mock_storage):
    """list_orders_by_status should work for every status in VALID_STATUSES."""
    orders_by_status = {status: [] for status in VALID_STATUSES}

    for i, status in enumerate(VALID_STATUSES):
        order_id = f"ORD-{i:03d}"
        orders_by_status[status].append({
            "item_name": f"Item {i}",
            "quantity": i + 1,
            "customer_id": f"CUST-{i:03d}",
            "status": status,
        })

    # Build the flat dict for the mock
    all_orders = {}
    for status_orders in orders_by_status.values():
        for order in status_orders:
            order_id = f"ORD-{order['quantity'] - 1:03d}"
            all_orders[order_id] = {"item_name": order["item_name"], "quantity": order["quantity"], "customer_id": order["customer_id"], "status": order["status"]}

    mock_storage.get_all_orders.return_value = all_orders

    for status in VALID_STATUSES:
        result = order_tracker.list_orders_by_status(status)
        assert len(result) == 1
        assert result[0]["status"] == status


def test_list_orders_by_status_empty_string(order_tracker, mock_storage):
    """list_orders_by_status with an empty string should raise ValueError."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.list_orders_by_status("")

    mock_storage.get_all_orders.assert_not_called()


def test_list_orders_by_status_whitespace_only(order_tracker, mock_storage):
    """list_orders_by_status with a whitespace-only string should raise ValueError."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.list_orders_by_status("   ")

    mock_storage.get_all_orders.assert_not_called()


def test_list_orders_by_status_none(order_tracker, mock_storage):
    """list_orders_by_status with None should raise ValueError."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.list_orders_by_status(None)

    mock_storage.get_all_orders.assert_not_called()


def test_list_orders_by_status_non_string_type(order_tracker, mock_storage):
    """list_orders_by_status with a non-string type should raise ValueError."""
    with pytest.raises(ValueError, match="status"):
        order_tracker.list_orders_by_status(12345)

    mock_storage.get_all_orders.assert_not_called()


def test_list_orders_by_status_invalid_status_value(order_tracker, mock_storage):
    """list_orders_by_status with a status not in VALID_STATUSES should raise ValueError."""
    with pytest.raises(ValueError, match="Invalid status"):
        order_tracker.list_orders_by_status("invalid_status")

    mock_storage.get_all_orders.assert_not_called()


def test_list_orders_by_status_case_sensitive(order_tracker, mock_storage):
    """list_orders_by_status should be case-sensitive: 'Shipped' should not match 'shipped'."""
    mock_storage.get_all_orders.return_value = {
        "ORD-001": {"item_name": "Wireless Mouse", "quantity": 2, "customer_id": "CUST-001", "status": "shipped"},
    }

    result = order_tracker.list_orders_by_status("Shipped")

    assert result == []


def test_list_orders_by_status_returns_copies(order_tracker, mock_storage):
    """list_orders_by_status should return copies of order data, not references to storage data."""
    original_order = {"item_name": "Test", "quantity": 1, "customer_id": "C-1", "status": "pending"}
    mock_storage.get_all_orders.return_value = {"ORD-001": original_order}

    result = order_tracker.list_orders_by_status("pending")

    # Mutating the returned result should not affect the original storage data
    result[0]["item_name"] = "Mutated"

    assert original_order["item_name"] == "Test"
