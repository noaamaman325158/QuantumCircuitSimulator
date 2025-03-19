# Quantum Circuit Simulator

This project is a Quantum Circuit Simulator that allows users to execute quantum circuits asynchronously. It provides an API for submitting quantum circuits in QASM format and retrieves the results of the execution.

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
  git@github.com:noaamaman325158/QuantumCircuitSimulator.git
```
2.Navigate to the project directory:
```shell
   cd quantum-circuit-simulator
```
3.Start the containers using Docker Compose:
```shell
   docker-compose up -d
```
4. Access the API endpoints:
   - Submit a quantum circuit: `POST http://localhost:8000/tasks`
   - Retrieve the status and result of a task: `GET http://localhost:8000/tasks/{task_id}`

## API Documentation(Swagger)
The API documentation for the Quantum Circuit Simulator can be found at `http://localhost:8000/docs` when running the project locally.
It provides details about the available endpoints, request/response formats, and authentication requirements.

## Deployment on AWS EC2

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
