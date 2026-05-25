# Chatbot Deployment and CI/CD Specification

## Project Goal

Deploy the provided chatbot application repositories on an AWS Linux VM using containerized deployment with Docker Compose and establish a CI/CD pipeline using GitHub Actions.

The CI/CD process should initially support only manual execution to provide controlled deployments during early phases.

---

## Requirements

### Repository Analysis

Read and analyze all provided repository.

Identify:

- Application framework and language
- Build process
- Runtime dependencies
- Environment variables
- Startup commands
- External integrations
- Network/port requirements
- Docker requirements
- Deployment prerequisites

Expected deliverables:

- Dependency mapping
- Deployment requirements
- Missing configuration identification
- Runtime architecture recommendations

---

## Infrastructure Requirements

### Target Environment

Cloud Provider: VM alredy created

- AWS

VM Type:

- AWS EC2 Linux VM

Preferred Operating Systems:

- Ubuntu Server LTS
- Amazon Linux 2023

---

## Deployment Architecture

Expected deployment architecture:

User
↓
Application URL
↓
AWS EC2 Linux VM
↓
Docker Compose
↓
Application Containers

GitHub Actions
↓
SSH
↓
EC2 Deployment

---

## CI/CD Platform

Platform:

- GitHub Actions

Trigger Type:

Manual only

Implementation:

```yaml
on:
  workflow_dispatch:
```

Initial restrictions:

- No push trigger
- No PR trigger
- No scheduled execution

---

## CI Pipeline Requirements

CI workflow should perform:

### Source Checkout

- Clone repository

### Dependency Validation

Perform:

- Dependency installation
- Build validation
- Package validation
- Optional linting
- Optional test execution

Examples:

```bash
npm install
pip install -r requirements.txt
mvn install
```

---

## Docker Build Requirements

CI should:

### Build Docker Image

Requirements:

- Create Docker image from repository
- Use Dockerfile from project
- Apply image tags

Example:

```bash
docker build -t chatbot-app:${GITHUB_SHA} .
```

Optional:

Push image to registry:

- Docker Hub
https://hub.docker.com/repositories/pawarmahesh2511

---

## CD Pipeline Requirements

Deployment should use Docker Compose.

Deployment flow:

1. Trigger GitHub Action manually
2. Checkout repository
3. Build Docker image
4. Connect to EC2 using SSH
5. Copy required deployment files
6. Generate .env file
7. Pull latest image
8. Stop existing containers
9. Start updated containers
10. Run health checks
11. Return deployment status

---

## Environment Variable Management

### .env Auto Generation

Requirement:

`.env` should be dynamically generated during deployment.

Rules:

- Do not commit `.env`
- Generate automatically from GitHub Secrets
- Store only on deployment server

Example:

```bash
cat <<EOF > .env
OPENAI_API_KEY=${{ secrets.OPENAI_API_KEY }}
DATABASE_URL=${{ secrets.DATABASE_URL }}
APP_ENV=${{ secrets.APP_ENV }}
PORT=${{ secrets.PORT }}
EOF
```

Add to `.gitignore`

```bash
.env
```

---

## GitHub Secrets Requirements

Secrets should include:

VM Access:

- EC2_HOST
- EC2_USERNAME
- EC2_SSH_KEY

Application Secrets:

- OPENAI_API_KEY
- DATABASE_URL

---

## Docker Compose Requirements

Dokcer compose alredy present in repo
---

## Expected Deliverables

- check Dockerfile
- check docker-compose.yml
- GitHub Actions workflow YAML
- Deployment scripts
- Auto-generated .env logic
- CI/CD documentation
- Rollback documentation