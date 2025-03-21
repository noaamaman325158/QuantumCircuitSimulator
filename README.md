# Quantum Circuit Simulator

This project is a Quantum Circuit Simulator that allows users to execute quantum circuits asynchronously. It provides an API for submitting quantum circuits in QASM format and retrieves the results of the execution.

![Screenshot from 2025-03-20 22-52-21](https://github.com/user-attachments/assets/619849ed-4935-457f-af26-dde715c9273a)


## Project Setup

The project consists of two main components:
1. Web Application: A FastAPI-based web application that handles the API endpoints for submitting quantum circuits and retrieving results.
2. Redis Database: A Redis database is used as a message broker and result storage for the asynchronous execution of quantum circuits.

The project is containerized using Docker and can be run using Docker Compose.

### Prerequisites

Before setting up the project, ensure that you have the following prerequisites installed:
- Docker: [Install Docker](https://docs.docker.com/get-docker/)
- Docker Compose: [Install Docker Compose](https://docs.docker.com/compose/install/)

### Configuration

The project uses environment variables for configuration. You can set the following environment variables in the `docker-compose.yml` file:
- `REDIS_HOST`: The hostname of the Redis database (default: `redis`).
- `REDIS_PORT`: The port number of the Redis database (default: `6379`).

### Running the Project

To run the project locally using Docker Compose, follow these steps:

1. Clone the repository:
  ```shell
  git clone git@github.com:noaamaman325158/QuantumCircuitSimulator.git
```
2.Navigate to the project directory:
```shell
   cd QuantumCircuitSimulator
```
3.Start the containers using Docker Compose:
```shell
   docker-compose -f docker-compose.yml up -d
```
4. Access the API endpoints:
   - Submit a quantum circuit: `POST http://localhost:8000/tasks`
   - Retrieve the status and result of a task: `GET http://localhost:8000/tasks/{task_id}`
### Observe Different scenarios
In addition to the tests, there are JSON files with predefined scenarios and explanations that you can try with the Swagger interface or Postman.
```shell
   cd app/test/data_auxilary
   cat scenarios.json
```
Example use-case:
```json
   {
    "name": "GHZ State",
    "description": "Creates a Greenberger-Horne-Zeilinger (GHZ) state among three qubits. Expected outcome: Equal probability of measuring '000' and '111' (binary 0 and 7 in decimal).",
    "circuit": {
      "qc": "OPENQASM 3.0;\nqreg q[3];\ncreg c[3];\nh q[0];\ncx q[0], q[1];\ncx q[1], q[2];\nmeasure q -> c;"
    },
    "expected_results": {
      "unique_outcomes": 2,
      "distribution": "Approximately 50% each for states '0' (000) and '7' (111)"
    },
    "execution_time": "Fast (< 1 second)"
  }
```
## API Documentation(Swagger)
The API documentation for the Quantum Circuit Simulator can be found at `http://localhost:8000/docs` when running the project locally.
It provides details about the available endpoints, request/response formats, and authentication requirements.
## Run Tests
Install locally the dependency of pytest.
```shell
   pip install pytest
```
And run command:
```shell
   python -m pytest
```

![image](https://github.com/user-attachments/assets/f052f946-b65f-4f8f-879d-8c38ae80d784)

## Deployment on AWS EC2

(https://ec2.noaamaman.com/docs)

![image](https://github.com/user-attachments/assets/753354a7-b19a-47bf-9aa8-69f436329885)


The project is deployed on an AWS EC2 instance using GitHub Actions for continuous deployment. The deployment process involves two workflows in the GitHub Actions CI/CD pipeline, the Docker Hub container registry, and the AWS EC2 service.

Here's an overview of the deployment process:

1. The deployment workflow is triggered when the "CI" workflow completes successfully on the "master" branch.

2. The workflow checks out the repository code and sets up the necessary tools and configurations.

3. It builds the Docker image for the web application and pushes it to Docker Hub, which serves as the container registry for storing and distributing the Docker images.

4. The workflow connects to the AWS EC2 instance using SSH.

5. On the EC2 instance, it stops any existing containers, prunes the Docker system, and pulls the latest Docker image from Docker Hub.

6. In addition, it starts the containers using Docker Compose, which includes the web application and Redis database.
   
7. Finally, Created some abstraction layer with CloudFront AWS service.

The deployment workflow ensures that the latest version of the application is deployed on the EC2 instance whenever changes are pushed to the "master" branch.

The two GitHub Actions workflows involved in the deployment process are:

1. Continuous Integration (CI) Workflow:
   - Triggered on every push or pull request to the "master" branch.
   - Builds the application and runs tests to ensure code quality and functionality.
   - Upon successful completion, it triggers the deployment workflow.

2. Continuous Deployment (CD) Workflow:
   - Triggered when the CI workflow completes successfully on the "master" branch.
   - Builds the Docker image, pushes it to Docker Hub, and deploys the application to the AWS EC2 instance.

By leveraging GitHub Actions, Docker Hub, and AWS EC2, the project achieves automated and seamless deployment, ensuring that the latest version of the application is always available on the production environment.

## Deployment on AWS EKS

(https://eks.noaamaman.com/docs)

![Untitled scene(2)](https://github.com/user-attachments/assets/d5d3571b-c590-4a28-b601-c06c8152af32)

The Quantum Circuit Simulator is deployed on Amazon EKS (Elastic Kubernetes Service), providing a scalable, highly available, and managed Kubernetes environment. This deployment leverages a robust CI/CD pipeline implemented through GitHub Actions.
The EKS deployment consists of several interconnected components:

-- Application Pods: Running the FastAPI web service that handles user requests
-- Redis Cluster: Acting as a message broker and result storage for quantum circuit executions
-- Worker Pods: Processing the quantum simulation tasks asynchronously
-- Kafka Integration: Enabling event-driven architecture for handling larger workloads

When a new code change is pushed to the repository, the GitHub Actions CI/CD pipeline automatically:

Builds and tests the application
- Packages it into a Docker image
- Pushes the image to Amazon ECR (Elastic Container Registry)
- Updates the Kubernetes deployment configuration
- Applies the changes to the EKS cluster

This automated workflow ensures consistent deployments, minimizes human error, and enables rapid iteration.

### Scaling Advantages
The EKS deployment offers significant scaling benefits:

1)Horizontal Pod Autoscaling: The system automatically scales the number of pods based on CPU utilization or custom metrics, allowing it to handle varying workloads efficiently. This is particularly valuable for quantum circuit simulations, which can have unpredictable resource requirements.

2)Cluster Autoscaler: EKS can automatically adjust the number of worker nodes in the cluster, scaling infrastructure up during peak usage times and down during periods of low demand, optimizing cost efficiency.

3)Workload Distribution: With Kubernetes' native load balancing, computation-intensive quantum simulations are distributed across multiple worker pods, preventing any single node from becoming a bottleneck.

4)Microservices Architecture: The separation of the web application, worker processes, and Redis components allows each to scale independently according to their specific resource needs.

5)Zero-Downtime Deployments: Rolling updates enable new versions to be deployed without service interruption, ensuring continuous availability of the quantum simulation service.

The service is publicly accessible at eks.noaamaman.com/docs, where users can explore the API documentation and interact with the Quantum Circuit Simulator.

### Main Technolegies
![image](https://github.com/user-attachments/assets/50781b47-c182-4fb1-8626-5bdf32848f59)

