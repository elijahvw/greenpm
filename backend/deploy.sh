#!/bin/bash

# Green PM Backend Deployment Script
set -e

# Configuration
PROJECT_ID="your-project-id"
REGION="us-central1"
SERVICE_NAME="greenpm-backend"
DATABASE_INSTANCE="greenpm-db"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Green PM Backend Deployment${NC}"

# Check if required variables are set
if [ -z "$PROJECT_ID" ] || [ "$PROJECT_ID" = "your-project-id" ]; then
    echo -e "${RED}ERROR: Please set PROJECT_ID in this script${NC}"
    exit 1
fi

# Build and push Docker image
echo -e "${YELLOW}Building Docker image...${NC}"
docker build -t gcr.io/$PROJECT_ID/$SERVICE_NAME .
docker push gcr.io/$PROJECT_ID/$SERVICE_NAME

# Deploy to Cloud Run
echo -e "${YELLOW}Deploying to Cloud Run...${NC}"
gcloud run deploy $SERVICE_NAME \
    --image gcr.io/$PROJECT_ID/$SERVICE_NAME \
    --platform managed \
    --region $REGION \
    --set-env-vars DATABASE_URL="postgresql://greenpm-user:YOUR_PASSWORD@/greenpm?host=/cloudsql/$PROJECT_ID:$REGION:$DATABASE_INSTANCE" \
    --set-env-vars JWT_SECRET_KEY="your-jwt-secret-key" \
    --set-env-vars JWT_ALGORITHM="HS256" \
    --set-env-vars JWT_ACCESS_TOKEN_EXPIRE_MINUTES=30 \
    --set-env-vars APP_NAME="Green PM" \
    --set-env-vars ENVIRONMENT="production" \
    --add-cloudsql-instances $PROJECT_ID:$REGION:$DATABASE_INSTANCE \
    --allow-unauthenticated \
    --memory=512Mi \
    --cpu=1 \
    --timeout=300 \
    --concurrency=100 \
    --min-instances=0 \
    --max-instances=10

echo -e "${GREEN}Deployment completed successfully!${NC}"

# Get service URL
SERVICE_URL=$(gcloud run services describe $SERVICE_NAME --region=$REGION --format='value(status.url)')
echo -e "${GREEN}Service URL: $SERVICE_URL${NC}"

# Test health endpoint
echo -e "${YELLOW}Testing health endpoint...${NC}"
curl -f $SERVICE_URL/health || echo -e "${RED}Health check failed${NC}"

echo -e "${GREEN}Deployment process completed!${NC}"