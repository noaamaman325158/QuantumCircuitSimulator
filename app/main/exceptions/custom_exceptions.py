from app.main.exceptions.qunatum_circuit_error import QuantumCircuitError


class RedisConnectionError(QuantumCircuitError):
    """Exception raised for errors in the Redis connection."""
    def __init__(self, host, port, message="Failed to connect to Redis"):
        self.host = host
        self.port = port
        self.message = f"{message} at {host}:{port}"
        super().__init__(self.message)

class TaskProcessingError(QuantumCircuitError):
    """Exception raised for errors during task processing."""
    def __init__(self, task_id, message="Error processing task"):
        self.task_id = task_id
        self.message = f"{message}: {task_id}"
        super().__init__(self.message)

class QASMParsingError(QuantumCircuitError):
    """Exception raised for errors in QASM parsing."""
    def __init__(self, message="QASM parsing failed", original_qasm=None):
        self.message = message
        self.original_qasm = original_qasm
        super().__init__(self.message)

class CircuitExecutionError(QuantumCircuitError):
    """Exception raised for errors during circuit execution."""
    def __init__(self, message="Circuit execution failed"):
        self.message = message
        super().__init__(self.message)


class QuantumTaskError(Exception):
    """Base exception for quantum task processing errors."""
    def __init__(self, message="An error occurred during quantum task processing"):
        self.message = message
        super().__init__(self.message)


class TaskTimeoutError(QuantumTaskError):
    """Exception raised when a task exceeds its maximum processing time."""
    def __init__(self, task_id=None, timeout=None,
                 message="Quantum circuit task processing timed out"):
        self.task_id = task_id
        self.timeout = timeout
        full_message = message
        if task_id:
            full_message += f" for task {task_id}"
        if timeout:
            full_message += f" after {timeout} seconds"
        super().__init__(full_message)
