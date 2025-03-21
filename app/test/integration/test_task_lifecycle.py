import pytest
import requests
import time
import uuid


class TestTaskLifecycle:
    """
    Integration tests for the complete task lifecycle
    """

    def test_successful_task_submission_and_completion(self):
        """
        Test a complete task submission, processing, and retrieval workflow
        """
        qasm_circuit = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[2];
        creg c[2];
        h q[0];
        cx q[0], q[1];
        measure q -> c;
        """

        submit_response = requests.post(
            "http://localhost:8000/tasks",
            json={"qc": qasm_circuit}
        )
        assert submit_response.status_code == 202, "Task submission failed"

        task_data = submit_response.json()
        task_id = task_data.get("task_id")
        assert task_id is not None, "No task ID returned"

        max_attempts = 30
        for attempt in range(max_attempts):
            status_response = requests.get(f"http://localhost:8000/tasks/{task_id}")
            status_data = status_response.json()

            if status_data.get("status") == "completed":
                assert "result" in status_data, "No results in completed task"
                results = status_data["result"]

                assert isinstance(results, dict), "Results should be a dictionary"
                assert len(results) > 0, "Results dictionary is empty"

                for state, count in results.items():
                    assert isinstance(state, str), "Result keys should be strings"
                    assert isinstance(count, int), "Result values should be integers"
                    assert count >= 0, "Measurement count cannot be negative"

                break

            elif status_data.get("status") == "error":
                pytest.fail(f"Task failed: {status_data.get('message', 'Unknown error')}")

            time.sleep(2)
        else:
            pytest.fail("Task did not complete within expected time")

    def test_multiple_task_submissions(self):
        """
        Test submitting multiple quantum circuits concurrently
        """
        qasm_circuit = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[2];
        creg c[2];
        h q[0];
        cx q[0], q[1];
        measure q -> c;
        """

        task_ids = []
        for _ in range(5):
            submit_response = requests.post(
                "http://localhost:8000/tasks",
                json={"qc": qasm_circuit}
            )
            assert submit_response.status_code == 202, "Task submission failed"
            task_ids.append(submit_response.json().get("task_id"))

        completed_tasks = 0
        max_attempts = 40
        for _ in range(max_attempts):
            completed_this_round = 0
            for task_id in task_ids:
                status_response = requests.get(f"http://localhost:8000/tasks/{task_id}")
                status_data = status_response.json()

                if status_data.get("status") == "completed":
                    completed_this_round += 1
                elif status_data.get("status") == "error":
                    pytest.fail(f"Task {task_id} failed: {status_data.get('message', 'Unknown error')}")

            completed_tasks = completed_this_round
            if completed_tasks == len(task_ids):
                break

            time.sleep(2)

        assert completed_tasks == len(task_ids), f"Only {completed_tasks} of {len(task_ids)} tasks completed"