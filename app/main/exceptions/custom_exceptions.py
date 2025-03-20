from app.main.exceptions.qunatum_circuit_error import QuantumCircuitError


class RedisConnectionError(QuantumCircuitError):
    """Exception raised for errors in the Redis connection."""
    def __init__(self, message="Failed to connect to Redis"):
        self.message = message
        super().__init__(self.message)

class KafkaConnectionError(QuantumCircuitError):
    """Exception raised for errors in the Kafka connection."""
    def __init__(self, message="Failed to connect to Kafka"):
        self.message = message
        super().__init__(self.message)

class TaskProcessingError(QuantumCircuitError):
    """Exception raised for errors during task processing."""
    def __init__(self, task_id, message="Error processing task"):
        self.task_id = task_id
        self.message = f"{message}: {task_id}"
        super().__init__(self.message)

class QASMParsingError(Exception):
    """
    Custom exception for QASM circuit parsing errors.
    """
    def __init__(self, message: str, original_qasm: str = None):
        """
        Initialize the QASMParsingError.
        """
        self.message = message
        self.original_qasm = original_qasm
        super().__init__(message)