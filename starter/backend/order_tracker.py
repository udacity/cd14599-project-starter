# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

VALID_STATUSES = {"pending", "processing", "shipped", "delivered", "cancelled"}


class OrderTracker:
    """
    Manages customer orders, providing functionalities to add, update,
    and retrieve order information.
    """
    def __init__(self, storage):
        required_methods = ['save_order', 'get_order', 'get_all_orders']
        for method in required_methods:
            if not hasattr(storage, method) or not callable(getattr(storage, method)):
                raise TypeError(f"Storage object must implement a callable '{method}' method.")
        self.storage = storage

    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        # Validate required fields are non-empty strings
        if not order_id or not order_id.strip():
            raise ValueError("order_id must be a non-empty string.")
        if not item_name or not item_name.strip():
            raise ValueError("item_name must be a non-empty string.")
        if not customer_id or not customer_id.strip():
            raise ValueError("customer_id must be a non-empty string.")

        # Validate quantity is a positive integer
        if not isinstance(quantity, int) or quantity <= 0:
            raise ValueError("quantity must be a positive integer.")

        # Check for duplicate order ID
        if self.storage.get_order(order_id) is not None:
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        # Build order data and save
        order_data = {
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status,
        }
        self.storage.save_order(order_id, order_data)

    def get_order_by_id(self, order_id: str):
        """
        Retrieve an order by its ID.

        Args:
            order_id: The unique identifier of the order to retrieve.

        Returns:
            A dict containing the order data including the order_id,
            or None if no order with the given ID exists.

        Raises:
            ValueError: If order_id is empty or not a string.
        """
        if not isinstance(order_id, str) or not order_id.strip():
            raise ValueError("order_id must be a non-empty string.")

        order_data = self.storage.get_order(order_id)
        if order_data is None:
            return None

        # Return a copy with order_id included for convenience
        result = order_data.copy()
        result["order_id"] = order_id
        return result

    def update_order_status(self, order_id: str, new_status: str):
        """
        Update the status of an existing order.

        Args:
            order_id: The unique identifier of the order to update.
            new_status: The new status to set. Must be one of the valid statuses.

        Raises:
            ValueError: If order_id is invalid, new_status is invalid,
                        or the order does not exist.
        """
        # Validate order_id
        if not isinstance(order_id, str) or not order_id.strip():
            raise ValueError("order_id must be a non-empty string.")

        # Validate new_status
        if not isinstance(new_status, str) or not new_status.strip():
            raise ValueError("new_status must be a non-empty string.")
        if new_status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: '{new_status}'. Valid statuses are: {sorted(VALID_STATUSES)}")

        # Check order existence
        order_data = self.storage.get_order(order_id)
        if order_data is None:
            raise ValueError(f"Order with ID '{order_id}' does not exist.")

        # Update only the status field
        updated_order = order_data.copy()
        updated_order["status"] = new_status
        self.storage.save_order(order_id, updated_order)

    def list_all_orders(self):
        """
        Retrieve all orders from storage.

        Returns:
            A list of dicts, each containing the order data including the order_id.
            Returns an empty list when no orders exist.
        """
        all_orders = self.storage.get_all_orders()
        result = []
        for order_id, order_data in all_orders.items():
            merged = order_data.copy()
            merged["order_id"] = order_id
            result.append(merged)
        return result

    def list_orders_by_status(self, status: str):
        """
        Retrieve orders filtered by their status.

        Args:
            status: The status to filter by. Must be one of the valid statuses.

        Returns:
            A list of dicts, each containing the order data including the order_id,
            for orders matching the given status. Returns an empty list when no
            orders match.

        Raises:
            ValueError: If status is empty, not a string, or not in VALID_STATUSES.
        """
        if not isinstance(status, str) or not status.strip():
            raise ValueError("status must be a non-empty string.")
        if status not in VALID_STATUSES:
            raise ValueError(f"Invalid status: '{status}'. Valid statuses are: {sorted(VALID_STATUSES)}")

        all_orders = self.storage.get_all_orders()
        result = []
        for order_id, order_data in all_orders.items():
            if order_data.get("status") == status:
                merged = order_data.copy()
                merged["order_id"] = order_id
                result.append(merged)
        return result
