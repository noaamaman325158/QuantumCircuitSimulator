import pytest
import requests
import time
import concurrent.futures
import statistics


class TestPerformance:
    """
    Performance and load testing for the Quantum Circuit API
    """

    def test_concurrent_task_submission(self):
        """
        Test the API's ability to handle concurrent task submissions
        """
        complex_qasm_circuit = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[5];
        creg c[5];
        h q[0];
        h q[1];
        h q[2];
        h q[3];
        h q[4];
        cx q[0], q[1];
        cx q[1], q[2];
        cx q[2], q[3];
        cx q[3], q[4];
        measure q -> c;
        """

        num_tasks = 10

        submission_times = []
        task_ids = []

        with concurrent.futures.ThreadPoolExecutor(max_workers=num_tasks) as executor:
            def submit_task():
                start_time = time.time()
                response = requests.post(
                    "http://localhost:8000/api/tasks",
                    json={"qc": complex_qasm_circuit}
                )
                end_time = time.time()

                assert response.status_code == 202, "Task submission failed"
                return response.json().get("task_id"), end_time - start_time

            futures = [executor.submit(submit_task) for _ in range(num_tasks)]

            for future in concurrent.futures.as_completed(futures):
                task_id, submission_time = future.result()
                task_ids.append(task_id)
                submission_times.append(submission_time)

        assert len(task_ids) == num_tasks, "Failed to submit all tasks"

        avg_submission_time = statistics.mean(submission_times)
        max_submission_time = max(submission_times)

        print(f"\nSubmission Performance:")
        print(f"Average Submission Time: {avg_submission_time:.4f} seconds")
        print(f"Max Submission Time: {max_submission_time:.4f} seconds")

        assert avg_submission_time < 2.0, "Average task submission time is too high"
        assert max_submission_time < 5.0, "Maximum task submission time is too high"

        completed_tasks = 0
        max_wait_time = 60
        start_wait = time.time()

        while completed_tasks < num_tasks and time.time() - start_wait < max_wait_time:
            completed_this_round = 0
            for task_id in task_ids:
                status_response = requests.get(f"http://localhost:8000/tasks/api/{task_id}")
                status_data = status_response.json()

                if status_data.get("status") == "completed":
                    completed_this_round += 1
                elif status_data.get("status") == "error":
                    pytest.fail(f"Task {task_id} failed: {status_data.get('message', 'Unknown error')}")

            completed_tasks = completed_this_round
            if completed_tasks == num_tasks:
                break

            time.sleep(2)

        assert completed_tasks == num_tasks, f"Only {completed_tasks} of {num_tasks} tasks completed"

    def test_single_task_execution_time(self):
        """
        Measure the execution time for a single quantum circuit
        """
        complex_qasm_circuit = """
        OPENQASM 2.0;
        include "qelib1.inc";
        qreg q[8];
        creg c[8];
        h q[0];
        h q[1];
        h q[2];
        h q[3];
        h q[4];
        h q[5];
        h q[6];
        h q[7];
        cx q[0], q[1];
        cx q[1], q[2];
        cx q[2], q[3];
        cx q[3], q[4];
        cx q[4], q[5];
        cx q[5], q[6];
        cx q[6], q[7];
        measure q -> c;
        """

        start_time = time.time()
        submit_response = requests.post(
            "http://localhost:8000/api/tasks",
            json={"qc": complex_qasm_circuit}
        )
        assert submit_response.status_code == 202, "Task submission failed"

        task_id = submit_response.json().get("task_id")

        max_wait_time = 60
        start_wait = time.time()
        completed = False

        while not completed and time.time() - start_wait < max_wait_time:
            status_response = requests.get(f"http://localhost:8000/api/tasks/{task_id}")
            status_data = status_response.json()

            if status_data.get("status") == "completed":
                completed = True
                break
            elif status_data.get("status") == "error":
                pytest.fail(f"Task failed: {status_data.get('message', 'Unknown error')}")

            time.sleep(2)

        total_time = time.time() - start_time

        print(f"\nSingle Task Execution:")
        print(f"Total Execution Time: {total_time:.2f} seconds")

        assert completed, "Task did not complete within the time limit"
        assert total_time < 45, "Task took too long to complete"