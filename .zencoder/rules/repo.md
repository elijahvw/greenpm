---
description: Repository Information Overview
alwaysApply: true
---

# Green PM - Rental Property Management Platform

## Summary
Green PM is a comprehensive SaaS platform for rental property management built on Google Cloud Platform. It provides landlords, tenants, and property managers with tools to streamline rental operations including property listings, lease management, financial management, maintenance tracking, and communication.

## Structure
- **backend/**: FastAPI Python backend application
- **frontend/**: React TypeScript frontend application
- **infrastructure/**: Terraform IaC for GCP deployment
- **scripts/**: Deployment and setup scripts
- **docs/**: Project documentation

## Projects

### Backend (FastAPI)
**Configuration File**: backend/requirements.txt

#### Language & Runtime
**Language**: Python
**Version**: 3.11
**Framework**: FastAPI 0.104.1
**Database ORM**: SQLAlchemy 2.0.23
**Migration Tool**: Alembic 1.12.1

#### Dependencies
**Main Dependencies**:
- fastapi==0.104.1
- uvicorn[standard]==0.24.0
- sqlalchemy==2.0.23
- pydantic==2.5.0
- stripe==7.8.0
- twilio==8.10.3
- sendgrid==6.11.0
- google-cloud-storage==2.10.0
- firebase-admin==6.4.0

**Development Dependencies**:
- pytest==7.4.3
- pytest-asyncio==0.21.1
- httpx==0.25.2

#### Build & Installation
```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

#### Docker
**Dockerfile**: backend/Dockerfile
**Base Image**: python:3.11-slim
**Exposed Port**: 8000
**Run Command**: uvicorn src.main:app --host 0.0.0.0 --port ${PORT:-8000}

#### Testing
**Framework**: pytest
**Test Location**: backend/
**Run Command**:
```bash
cd backend
pytest
```

### Frontend (React)
**Configuration File**: frontend/package.json

#### Language & Runtime
**Language**: TypeScript
**Version**: 4.9.5
**Framework**: React 18.2.0
**Package Manager**: npm

#### Dependencies
**Main Dependencies**:
- react==18.2.0
- typescript==4.9.5
- @reduxjs/toolkit==1.9.7
- react-query==3.39.3
- @stripe/react-stripe-js==2.4.0
- tailwindcss==3.3.6

**Development Dependencies**:
- autoprefixer==10.4.16
- postcss==8.4.32

#### Build & Installation
```bash
cd frontend
npm install
npm start
```

#### Docker
**Dockerfile**: frontend/Dockerfile
**Build Image**: node:18-alpine
**Production Image**: nginx:alpine
**Exposed Port**: 3000
**Build Command**: npm run build

### Infrastructure (Terraform)
**Configuration File**: infrastructure/terraform/main.tf

#### Specification & Tools
**Type**: Infrastructure as Code
**Version**: Terraform >= 1.0
**Cloud Provider**: Google Cloud Platform
**Required APIs**: Compute, Cloud Run, Cloud SQL, Storage, Secret Manager, etc.

#### Key Resources
**Main Files**:
- infrastructure/terraform/main.tf
- infrastructure/terraform/variables.tf
- infrastructure/terraform/modules/

**Configuration Structure**:
- VPC Network
- Cloud SQL (PostgreSQL)
- Cloud Storage
- Secret Manager
- Cloud Run Services
- Load Balancer
- CI/CD

#### Usage & Operations
**Key Commands**:
```bash
./scripts/deploy.sh setup
./scripts/deploy.sh deploy dev
./scripts/deploy.sh deploy prod
```

## Deployment
The platform is deployed on Google Cloud Platform using Terraform and Cloud Build. The deployment process is automated through scripts in the scripts/ directory. The application is containerized using Docker and deployed to Cloud Run.

## Integration Points
- **Stripe**: Payment processing
- **Twilio**: SMS notifications
- **SendGrid**: Email notifications
- **Firebase**: Authentication (optional)
- **Google Cloud Storage**: File storage
- **Google Cloud SQL**: PostgreSQL database