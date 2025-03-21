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
Except the tests, I attached some json file of scenarios  with explenation about each scenario - you can try them with nthe swagger interface or Postman.
```shell
   cd app/test/data_auxilary
   cat scenarios.json
```
Example for use-case:
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
## Deployment on AWS EKS
[eks.noaamaman.com/docs]
![Untitled scene(2)](https://github.com/user-attachments/assets/d5d3571b-c590-4a28-b601-c06c8152af32)


## Deployment on AWS EC2
(ec2.noaamaman.com/docs)
![ec2-qunatum(2)](https://github.com/user-attachments/assets/a6f87445-3b8e-4ff7-9b11-8d721d8999c2)

The project is deployed on an AWS EC2 instance using GitHub Actions for continuous deployment. The deployment process involves two workflows in the GitHub Actions CI/CD pipeline, the Docker Hub container registry, and the AWS EC2 service.

Here's an overview of the deployment process:

1. The deployment workflow is triggered when the "CI" workflow completes successfully on the "master" branch.

2. The workflow checks out the repository code and sets up the necessary tools and configurations.

3. It builds the Docker image for the web application and pushes it to Docker Hub, which serves as the container registry for storing and distributing the Docker images.

4. The workflow connects to the AWS EC2 instance using SSH.

5. On the EC2 instance, it stops any existing containers, prunes the Docker system, and pulls the latest Docker image from Docker Hub.

6. In addition, it starts the containers using Docker Compose, which includes the web application and Redis database.
   
7. Finally, Created some abstraction layer with CloudFront AWS service.

You can access the public version in this CloudFront Distribution and Route53 with HTTPS protocol:
(http://api.noaamaman.com/docs)

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
