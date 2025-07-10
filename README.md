# Codelab: A TDD Workflow

Welcome to the Udatracker Codelab! This guide will walk you through implementing the backend logic and API for your project using a strict **Test-Driven Development (TDD)** workflow.

Your goal is to use the provided test suites to drive your implementation. You'll follow the classic **Red → Green → Refactor** cycle: run a test to see it fail, write the code to make it pass, and then move on to the next feature.
<img width="1261" height="805" alt="Screenshot 2025-07-10 at 19 39 56" src="https://github.com/user-attachments/assets/375894d2-6b0b-43a6-aca9-e0e8cc52d20a" />

---

## Part 1: Environment Setup

First, ensure your environment is ready.

1.  **Navigate to the Backend**:
    Open your terminal and `cd` into the `backend` directory.
    ```bash
    cd backend
    ```

2.  **Activate Your Virtual Environment**:
    If you haven't already, activate the virtual environment.
    ```bash
    # For macOS/Linux
    source venv/bin/activate

    # For Windows (PowerShell)
    # .\venv\Scripts\Activate.ps1
    ```

3.  **Ensure Dependencies are Installed**:
    Make sure you have `Flask` and `pytest` installed from your `requirements.txt` file.
    ```bash
    pip install -r requirements.txt
    ```

---
## Part 2: Unit Testing the `OrderTracker` (The TDD Cycle)

We will build the `OrderTracker` class one test at a time. Open both `backend/order_tracker.py` and the **empty** `backend/tests/test_order_tracker.py` files in your editor.

### Cycle 1: Adding a Basic Order

1.  **Write the First Test**: Add the following code to `tests/test_order_tracker.py`. This test checks if we can add a simple order.

    ```python
    # in backend/tests/test_order_tracker.py
    import pytest
    from unittest.mock import Mock
    from ..order_tracker import OrderTracker

    @pytest.fixture
    def mock_storage():
        """Provides a mock storage object for tests."""
        mock = Mock()
        mock.get_order.return_value = None
        return mock

    @pytest.fixture
    def order_tracker(mock_storage):
        """Provides an OrderTracker instance initialized with the mock storage."""
        return OrderTracker(mock_storage)

    def test_add_order_successfully(order_tracker, mock_storage):
        """Tests adding a new order with default 'pending' status."""
        order_tracker.add_order("ORD001", "Laptop", 1, "CUST001")
        
        # We expect save_order to be called once
        mock_storage.save_order.assert_called_once()
    ```

2.  **See it Fail (RED)**: Run the test. It will fail because the `add_order` method is empty.
    ```bash
    pytest tests/test_order_tracker.py
    ```

3.  **Write the Code (GREEN)**: In `order_tracker.py`, write the *minimum* code in the `add_order` method to make the test pass.

    ```python
    # in backend/order_tracker.py
    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status
        }
        self.storage.save_order(order_id, order)
    ```

4.  **See it Pass**: Run the test again. It should now pass.

### Cycle 2: Preventing Duplicate Orders

1.  **Write the Test**: Add a *new* test to `test_order_tracker.py` to check for duplicate IDs.

    ```python
    # Add to tests/test_order_tracker.py
    def test_add_order_raises_error_if_exists(order_tracker, mock_storage):
        """Tests that adding an order with a duplicate ID raises a ValueError."""
        # Simulate that the storage finds an existing order
        mock_storage.get_order.return_value = {"order_id": "ORD_EXISTING"}

        with pytest.raises(ValueError, match="Order with ID 'ORD_EXISTING' already exists."):
            order_tracker.add_order("ORD_EXISTING", "New Item", 1, "CUST001")
    ```

2.  **See it Fail (RED)**: Run `pytest`. The new test will fail.

3.  **Update the Code (GREEN)**: Add the validation logic to the `add_order` method in `order_tracker.py`.

    ```python
    # Update the add_order method in backend/order_tracker.py
    def add_order(self, order_id: str, item_name: str, quantity: int, customer_id: str, status: str = "pending"):
        # This is the new logic
        if self.storage.get_order(order_id):
            raise ValueError(f"Order with ID '{order_id}' already exists.")

        order = {
            "order_id": order_id,
            "item_name": item_name,
            "quantity": quantity,
            "customer_id": customer_id,
            "status": status
        }
        self.storage.save_order(order_id, order)
    ```

4.  **See it Pass**: Run the tests again. Both tests should now pass.

*(This TDD cycle of "Write Test -> See Fail -> Write Code -> See Pass" should be continued for all validation logic and all other methods like `get_order_by_id`, `update_order_status`, etc.)*

---
## Part 3: Building the API

Once all the unit tests for `OrderTracker` are written and passing, you can build the API layer. For this part, you are provided with the complete API test suite (`tests/test_api.py`).

1.  **See the API Tests Fail (RED)**: Run the integration tests. They will fail because the API endpoints in `app.py` are empty.
    ```bash
    pytest tests/test_api.py
    ```

2.  **Implement the API Endpoints (GREEN)**: Open `backend/app.py`. Fill in the logic for each route function to make the tests pass.

3.  **Final Test Run**: After implementing all endpoints, run the entire test suite.
    ```bash
    pytest tests/
    ```
    All tests should now pass.

---
## Part 4: Run the Full Application

Now for the final reward. Let's see your application in action!

1.  **Run the Flask Server**:
    ```bash
    python app.py
    ```

2.  **Open in Browser**:
    Open your web browser and go to `http://127.0.0.1:5000/`.

🎉 **Congratulations!** You have completed the project with a true test-first approach.
