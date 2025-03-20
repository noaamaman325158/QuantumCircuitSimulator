import asyncio
import json
import uuid
from dotenv import load_dotenv

from fastapi import FastAPI, BackgroundTasks, HTTPException
from fastapi.middleware.cors import CORSMiddleware  # Import CORS middleware

from app.main.models.QuantumCircuitRequest import QuantumCircuitRequest
from app.main.models.TaskResponse import TaskResponse
from app.main.models.PendingTaskResponse import PendingTaskResponse
from app.main.service.quantum_circuit_service import QuantumCircuitService
from app.main.models.CompletedTaskResponse import CompletedTaskResponse
from app.main.models.ErrorTaskResponse import ErrorTaskResponse
from app.main.exceptions.custom_exceptions import QASMParsingError, CircuitExecutionError, RedisConnectionError, \
    TaskProcessingError, TaskTimeoutError

import logging
import redis
import os

load_dotenv()

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

REDIS_HOST = os.getenv("REDIS_HOST", "localhost")
REDIS_PORT = int(os.getenv("REDIS_PORT", 6378))
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
    raise RedisConnectionError(host=REDIS_HOST, port=REDIS_PORT)

app = FastAPI(
    title="Quantum Circuit API",
    description="API for executing Quantum Circuits asynchronously",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3001", "https://front.noaamaman.com"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)


async def process_quantum_circuit(task_id: str, qasm_string: str, timeout: int = 30):
    """
    Process a quantum circuit asynchronously.

    Args:
        task_id: Unique task identifier
        qasm_string: QASM representation of a quantum circuit
        timeout: Maximum processing time in seconds
    """
    try:

        await asyncio.sleep(30)
        # Create an instance of the service
        service = QuantumCircuitService(shots=1024)

        # Execute the quantum circuit with a timeout
        result = await asyncio.wait_for(service.execute_qasm(qasm_string), timeout=timeout)

        # Store the result in Redis
        if result.get("error", False):
            # Store error result
            redis_client.hset(
                f"task:{task_id}",
                mapping={
                    "status": "error",
                    "message": result.get("message", "Unknown error")
                }
            )
        else:
            # Store successful result
            redis_client.hset(
                f"task:{task_id}",
                mapping={
                    "status": "completed",
                    "result": json.dumps(result.get("counts", {}))
                }
            )

        logger.info(f"Task {task_id} completed successfully")
    except asyncio.TimeoutError:
        logger.error(f"Task {task_id} timed out after {timeout} seconds")
        redis_client.hset(
            f"task:{task_id}",
            mapping={
                "status": "error",
                "message": f"Task timed out after {timeout} seconds"
            }
        )
        raise TaskTimeoutError(task_id=task_id, timeout=timeout)
    except QASMParsingError as e:
        logger.error(f"QASM parsing error for task {task_id}: {str(e)}")
        redis_client.hset(
            f"task:{task_id}",
            mapping={
                "status": "error",
                "message": f"QASM parsing error: {str(e)}"
            }
        )
    except CircuitExecutionError as e:
        logger.error(f"Circuit execution error for task {task_id}: {str(e)}")
        redis_client.hset(
            f"task:{task_id}",
            mapping={
                "status": "error",
                "message": f"Circuit execution error: {str(e)}"
            }
        )
    except Exception as e:
        logger.error(f"Unexpected error processing task {task_id}: {str(e)}")
        redis_client.hset(
            f"task:{task_id}",
            mapping={
                "status": "error",
                "message": f"Unexpected error: {str(e)}"
            }
        )
        raise TaskProcessingError(task_id=task_id, message=str(e))


@app.post("/tasks", response_model=TaskResponse, status_code=202)
async def create_task(request: QuantumCircuitRequest, background_tasks: BackgroundTasks):
    """
    Submit a quantum circuit for asynchronous processing.

    - **qc**: Serialized quantum circuit in QASM3 format

    Returns a unique task ID for tracking the processing status.
    """
    task_id = str(uuid.uuid4())

    try:
        # Set initial task status in Redis
        redis_client.hset(
            f"task:{task_id}",
            mapping={
                "status": "pending",
                "message": "Task submitted successfully."
            }
        )

        # Add the processing task to background tasks
        background_tasks.add_task(process_quantum_circuit, task_id, request.qc)
        return TaskResponse(
            task_id=task_id,
            message="Task submitted successfully."
        )
    except Exception as e:
        logger.error(f"Error creating task: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error creating task: {str(e)}")


@app.get("/tasks/{task_id}", response_model=None)
async def get_task(task_id: str):
    """
    Retrieve the status and results of a previously submitted task.

    Args:
        task_id: Unique task identifier

    Returns:
        Current status and results (if completed) of the task
    """
    try:
        # Get task data from Redis
        task_data = redis_client.hgetall(f"task:{task_id}")

        if not task_data:
            return ErrorTaskResponse(
                status="error",
                message="Task not found."
            )

        # Convert bytes to strings if necessary
        task_data = {k.decode() if isinstance(k, bytes) else k:
                         v.decode() if isinstance(v, bytes) else v
                     for k, v in task_data.items()}

        status = task_data.get("status")

        if status == "completed":
            # Parse the result JSON
            result_data = json.loads(task_data.get("result", "{}"))
            return CompletedTaskResponse(
                status="completed",
                result=result_data
            )
        elif status == "error":
            return ErrorTaskResponse(
                status="error",
                message=task_data.get("message", "Unknown error")
            )
        else:
            # Status is "pending" or any other state
            return PendingTaskResponse(
                status="pending",
                message=task_data.get("message", "Task is still in progress.")
            )

    except Exception as e:
        logger.error(f"Error retrieving task {task_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving task: {str(e)}")




@app.get("/tasks")
async def get_all_tasks():
    """
    Retrieve all tasks in the system.
    """
    try:
        # Get all keys matching the pattern "task:*"
        task_keys = redis_client.keys("task:*")

        tasks = []
        for key in task_keys:
            task_id = key.replace("task:", "")
            task_data = redis_client.hgetall(key)

            # Process task data
            task_info = {
                "task_id": task_id,
                "status": task_data.get("status", "unknown")
            }

            if "message" in task_data:
                task_info["message"] = task_data["message"]

            tasks.append(task_info)

        return tasks
    except Exception as e:
        logger.error(f"Error retrieving all tasks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Error retrieving tasks: {str(e)}")


@app.get("/test-redis")
async def check_redis_connection():
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

    uvicorn.run(app, host="0.0.0.0", port=8001)  # Changed port to 8001