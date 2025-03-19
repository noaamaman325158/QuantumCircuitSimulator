import json
import uuid
from fastapi import FastAPI, BackgroundTasks, HTTPException
from pydantic import BaseModel
from models.TaskResult import TaskResult
from models.QuantumCircuitRequest import QuantumCircuitRequest
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


class TaskResponse(BaseModel):
    task_id: str
    message: str





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
    task_id = str(uuid.uuid4())

    try:
        redis_client.hset(
            f"task:{task_id}",
            mapping={
                "status": "pending",
                "message": "Task submitted successfully."
            }
        )

        background_tasks.add_task(process_quantum_circuit, task_id, request.qc)

        return TaskResponse(
            task_id=task_id,
            message="Task submitted successfully."
        )
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


@app.get("/tasks/{task_id}", response_model=TaskResult)
async def get_task_result(task_id: str):
    """
    Retrieve the results of a previously submitted quantum circuit using its unique task identifier.

    - **task_id**: Unique identifier for the task

    Returns the task status and results if completed.
    """
    try:
        task_data = redis_client.hgetall(f"task:{task_id}")

        if not task_data:
            return {
                "status": "error",
                "message": "Task not found."
            }

        if task_data.get("status") == "pending" or task_data.get("status") == "processing":
            return {
                "status": "pending",
                "message": "Task is still in progress."
            }

        if task_data.get("status") == "completed" and "result" in task_data:
            try:
                result = json.loads(task_data["result"])
                return {
                    "status": "completed",
                    "result": result
                }
            except json.JSONDecodeError:
                logger.error(f"Failed to parse result JSON for task {task_id}")
                return {
                    "status": "error",
                    "message": "Error parsing task results."
                }
        return {
            "status": "error",
            "message": task_data.get("message", "Unknown error occurred.")
        }

    except Exception as e:
        logger.error(f"Error retrieving task result: {str(e)}")
        return {
            "status": "error",
            "message": "An error occurred while retrieving the task."
        }


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