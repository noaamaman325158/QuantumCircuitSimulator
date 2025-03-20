import pytest
import requests
import uuid


class TestErrorHandling:
    """
    Integration tests for error handling scenarios
    """

    def test_invalid_circuit_submission(self):
        """
        Test submission of an invalid quantum circuit
        """
        # Various invalid circuit scenarios
        invalid_circuits = [
            "INVALID CIRCUIT",
            "",
            None,
            "OPENQASM 2.0; random garbage",
            "{malformed: json}"
        ]

        for invalid_circuit in invalid_circuits:
            response = requests.post(
                "http://localhost:8000/tasks",
                json={"qc": invalid_circuit}
            )

            # Expect a client error (400 or 422)
            assert response.status_code in [400, 422], f"Failed to handle invalid circuit: {invalid_circuit}"

    def test_nonexistent_task_retrieval(self):
        """
        Test retrieving a non-existent task
        """
        # Generate a random UUID
        nonexistent_task_id = str(uuid.uuid4())

        response = requests.get(f"http://localhost:8000/tasks/{nonexistent_task_id}")

        # Verify error response
        assert response.status_code == 404, "Non-existent task should return 404"

        error_data = response.json()
        assert error_data.get("status") == "error", "Error response should have 'error' status"
        assert "not found" in error_data.get("message", "").lower(), "Error message should indicate task not found"

    def test_malformed_request(self):
        """
        Test API response to malformed requests
        """
        # Malformed JSON
        malformed_requests = [
            {"invalid_key": "value"},  # Missing "qc" key
            {},  # Empty payload
        ]

        for payload in malformed_requests:
            response = requests.post(
                "http://localhost:8000/tasks",
                json=payload
            )

            # Expect a client error (400 or 422)
            assert response.status_code in [400, 422], f"Failed to handle malformed request: {payload}"

            error_data = response.json()
            assert "error" in error_data.get("status", "").lower(), "Error response should indicate an error"