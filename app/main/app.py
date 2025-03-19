from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from typing import Dict, Optional
import logging
import redis
import os

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6380))

try:
    redis_client = redis.Redis(
        host=REDIS_HOST,
        port=REDIS_PORT,
        db=0,
        decode_responses=True
    )
    redis_client.ping()
    logger.info(f"Successfully connected to Redis at {REDIS_HOST}:{REDIS_PORT}")
except redis.ConnectionError as e:
    logger.error(f"Failed to connect to Redis: {str(e)}")
    logger.error(f"Connection details: {REDIS_HOST}:{REDIS_PORT}")

app = FastAPI(
    title="Quantum Circuit API",
    description="API for executing Quantum Circuits asynchronously",
    version="1.0.0"
)


class QuantumCircuitRequest(BaseModel):
    qc: str


class TaskResponse(BaseModel):
    task_id: str
    message: str


class TaskResult(BaseModel):
    status: str
    result: Optional[Dict[str, int]] = None
    message: Optional[str] = None


def process_quantum_circuit(task_id: str, qc_data: str):
    """
    Simulate processing of a quantum circuit.
    :param task_id: Unique identifier for the task
    :param qc_data: Serialized quantum circuit in QASM3 format
    """


@app.post("/tasks", response_model=TaskResponse, status_code=202)
async def create_task(request: QuantumCircuitRequest, background_tasks: BackgroundTasks):
    """
    Submit a quantum circuit for asynchronous processing.

    - **qc**: Serialized quantum circuit in QASM3 format

    Returns a unique task ID for tracking the processing status.
    """



@app.get("/tasks/{task_id}", response_model=TaskResult)
async def get_task_result(task_id: str):
    """
    Retrieve the results of a previously submitted quantum circuit using its unique task identifier.

    - **task_id**: Unique identifier for the task

    Returns the task status and results if completed.
    """



@app.get("/test-redis")
async def test_redis_connection():
    """
    Test the connection to the Redis server.
    """
    try:
        redis_client.ping()
        info = redis_client.info()
        return {
            "status": "success",
            "message": "Connected to Redis",
            "version": info.get("redis_version", "unknown"),
            "clients_connected": info.get("connected_clients", "unknown")
        }
    except redis.RedisError as e:
        logger.error(f"Redis connection test failed: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail=f"Failed to connect to Redis at {REDIS_HOST}:{REDIS_PORT}"
        )



if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)