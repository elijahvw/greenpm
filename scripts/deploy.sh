#!/bin/bash

# Green PM Deployment Script
set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Configuration
PROJECT_ID="greenpm"
REGION="us-central1"
ENVIRONMENTS=("dev" "prod")

# Functions
log_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

log_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

log_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if gcloud is installed and authenticated
check_gcloud() {
    if ! command -v gcloud &> /dev/null; then
        log_error "gcloud CLI is not installed. Please install it first."
        exit 1
    fi

    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "No active gcloud authentication found. Please run 'gcloud auth login'"
        exit 1
    fi

    # Set project
    gcloud config set project $PROJECT_ID
    log_success "Using project: $PROJECT_ID"
}

# Check if Terraform is installed
check_terraform() {
    if ! command -v terraform &> /dev/null; then
        log_error "Terraform is not installed. Please install it first."
        exit 1
    fi
    log_success "Terraform is available"
}

# Enable required APIs
enable_apis() {
    log_info "Enabling required Google Cloud APIs..."
    
    apis=(
        "compute.googleapis.com"
        "run.googleapis.com"
        "sql-component.googleapis.com"
        "sqladmin.googleapis.com"
        "storage.googleapis.com"
        "secretmanager.googleapis.com"
        "cloudbuild.googleapis.com"
        "firebase.googleapis.com"
        "identitytoolkit.googleapis.com"
        "cloudresourcemanager.googleapis.com"
        "iam.googleapis.com"
        "servicenetworking.googleapis.com"
    )
    
    for api in "${apis[@]}"; do
        log_info "Enabling $api..."
        gcloud services enable $api --project=$PROJECT_ID
    done
    
    log_success "All APIs enabled successfully"
}

# Create Terraform state buckets
create_state_buckets() {
    log_info "Creating Terraform state buckets..."
    
    for env in "${ENVIRONMENTS[@]}"; do
        bucket_name="${PROJECT_ID}-${env}-terraform-state"
        
        if ! gsutil ls -b gs://$bucket_name &> /dev/null; then
            log_info "Creating bucket: $bucket_name"
            gsutil mb -p $PROJECT_ID -c STANDARD -l $REGION gs://$bucket_name
            gsutil versioning set on gs://$bucket_name
            log_success "Created bucket: $bucket_name"
        else
            log_info "Bucket already exists: $bucket_name"
        fi
    done
}

# Deploy infrastructure for an environment
deploy_infrastructure() {
    local env=$1
    log_info "Deploying infrastructure for environment: $env"
    
    cd infrastructure/terraform/environments/$env
    
    # Initialize Terraform
    terraform init
    
    # Plan deployment
    terraform plan -var="environment=$env"
    
    # Ask for confirmation
    read -p "Do you want to apply these changes? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        terraform apply -var="environment=$env" -auto-approve
        log_success "Infrastructure deployed for $env environment"
    else
        log_warning "Deployment cancelled for $env environment"
    fi
    
    cd ../../../../
}

# Setup secrets
setup_secrets() {
    local env=$1
    log_info "Setting up secrets for environment: $env"
    
    # Check if secrets exist, if not create placeholders
    secrets=(
        "stripe-secret-key"
        "stripe-publishable-key"
        "stripe-webhook-secret"
        "twilio-account-sid"
        "twilio-auth-token"
        "twilio-phone-number"
        "sendgrid-api-key"
        "firebase-config"
    )
    
    for secret in "${secrets[@]}"; do
        secret_name="greenpm-${env}-${secret}"
        
        if ! gcloud secrets describe $secret_name --project=$PROJECT_ID &> /dev/null; then
            log_info "Creating secret: $secret_name"
            echo "PLACEHOLDER_VALUE" | gcloud secrets create $secret_name --data-file=- --project=$PROJECT_ID
            log_warning "Created placeholder for $secret_name - please update with actual value"
        else
            log_info "Secret already exists: $secret_name"
        fi
    done
}

# Build and deploy applications
deploy_applications() {
    local env=$1
    log_info "Deploying applications for environment: $env"
    
    # Submit backend build
    log_info "Building and deploying backend..."
    gcloud builds submit backend/ \
        --config=backend/cloudbuild.yaml \
        --substitutions=_ENVIRONMENT=$env,_SERVICE_NAME=greenpm-${env}-backend,_REGION=$REGION \
        --project=$PROJECT_ID
    
    # Submit frontend build
    log_info "Building and deploying frontend..."
    gcloud builds submit frontend/ \
        --config=frontend/cloudbuild.yaml \
        --substitutions=_ENVIRONMENT=$env,_SERVICE_NAME=greenpm-${env}-frontend,_REGION=$REGION \
        --project=$PROJECT_ID
    
    log_success "Applications deployed for $env environment"
}

# Main deployment function
deploy_environment() {
    local env=$1
    
    log_info "Starting deployment for $env environment"
    
    # Deploy infrastructure
    deploy_infrastructure $env
    
    # Setup secrets
    setup_secrets $env
    
    # Deploy applications
    deploy_applications $env
    
    log_success "Deployment completed for $env environment"
    
    # Get service URLs
    backend_url=$(gcloud run services describe greenpm-${env}-backend --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
    frontend_url=$(gcloud run services describe greenpm-${env}-frontend --region=$REGION --project=$PROJECT_ID --format="value(status.url)")
    
    echo
    log_success "Deployment URLs:"
    echo "Backend:  $backend_url"
    echo "Frontend: $frontend_url"
    echo
}

# Show help
show_help() {
    echo "Green PM Deployment Script"
    echo
    echo "Usage: $0 [COMMAND] [ENVIRONMENT]"
    echo
    echo "Commands:"
    echo "  setup     - Initial setup (enable APIs, create buckets)"
    echo "  deploy    - Deploy infrastructure and applications"
    echo "  infra     - Deploy only infrastructure"
    echo "  apps      - Deploy only applications"
    echo "  secrets   - Setup secrets"
    echo "  help      - Show this help message"
    echo
    echo "Environments:"
    echo "  dev       - Development environment"
    echo "  prod      - Production environment"
    echo
    echo "Examples:"
    echo "  $0 setup"
    echo "  $0 deploy dev"
    echo "  $0 infra prod"
    echo "  $0 apps dev"
}

# Main script logic
main() {
    local command=$1
    local environment=$2
    
    # Check prerequisites
    check_gcloud
    check_terraform
    
    case $command in
        "setup")
            enable_apis
            create_state_buckets
            log_success "Initial setup completed"
            ;;
        "deploy")
            if [[ -z $environment ]]; then
                log_error "Environment is required for deploy command"
                show_help
                exit 1
            fi
            deploy_environment $environment
            ;;
        "infra")
            if [[ -z $environment ]]; then
                log_error "Environment is required for infra command"
                show_help
                exit 1
            fi
            deploy_infrastructure $environment
            ;;
        "apps")
            if [[ -z $environment ]]; then
                log_error "Environment is required for apps command"
                show_help
                exit 1
            fi
            deploy_applications $environment
            ;;
        "secrets")
            if [[ -z $environment ]]; then
                log_error "Environment is required for secrets command"
                show_help
                exit 1
            fi
            setup_secrets $environment
            ;;
        "help"|"--help"|"-h")
            show_help
            ;;
        *)
            log_error "Unknown command: $command"
            show_help
            exit 1
            ;;
    esac
}

# Run main function with all arguments
main "$@"