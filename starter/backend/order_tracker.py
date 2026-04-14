# This module contains the OrderTracker class, which encapsulates the core
# business logic for managing orders.

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
        pass

    def list_all_orders(self):
        pass

    def list_orders_by_status(self, status: str):
        pass
