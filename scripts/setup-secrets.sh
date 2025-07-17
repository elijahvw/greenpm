#!/bin/bash

# Green PM - Secrets Setup Script
# This script helps you set up all required secrets for the platform

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ID="greenpm"

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

# Function to create or update a secret
create_or_update_secret() {
    local secret_name=$1
    local secret_value=$2
    local environment=$3
    
    full_secret_name="greenpm-${environment}-${secret_name}"
    
    if gcloud secrets describe $full_secret_name --project=$PROJECT_ID &> /dev/null; then
        log_info "Updating existing secret: $full_secret_name"
        echo "$secret_value" | gcloud secrets versions add $full_secret_name --data-file=- --project=$PROJECT_ID
    else
        log_info "Creating new secret: $full_secret_name"
        echo "$secret_value" | gcloud secrets create $full_secret_name --data-file=- --project=$PROJECT_ID
    fi
    
    log_success "Secret $full_secret_name updated successfully"
}

# Function to setup secrets for an environment
setup_environment_secrets() {
    local env=$1
    
    log_info "Setting up secrets for $env environment"
    echo
    
    # Stripe secrets
    echo -e "${YELLOW}Stripe Configuration:${NC}"
    read -p "Enter Stripe Secret Key (sk_...): " stripe_secret_key
    read -p "Enter Stripe Publishable Key (pk_...): " stripe_publishable_key
    read -p "Enter Stripe Webhook Secret (whsec_...): " stripe_webhook_secret
    
    create_or_update_secret "stripe-secret-key" "$stripe_secret_key" $env
    create_or_update_secret "stripe-publishable-key" "$stripe_publishable_key" $env
    create_or_update_secret "stripe-webhook-secret" "$stripe_webhook_secret" $env
    
    echo
    
    # Twilio secrets
    echo -e "${YELLOW}Twilio Configuration:${NC}"
    read -p "Enter Twilio Account SID: " twilio_account_sid
    read -p "Enter Twilio Auth Token: " twilio_auth_token
    read -p "Enter Twilio Phone Number (+1234567890): " twilio_phone_number
    
    create_or_update_secret "twilio-account-sid" "$twilio_account_sid" $env
    create_or_update_secret "twilio-auth-token" "$twilio_auth_token" $env
    create_or_update_secret "twilio-phone-number" "$twilio_phone_number" $env
    
    echo
    
    # SendGrid secrets
    echo -e "${YELLOW}SendGrid Configuration:${NC}"
    read -p "Enter SendGrid API Key (SG....): " sendgrid_api_key
    
    create_or_update_secret "sendgrid-api-key" "$sendgrid_api_key" $env
    
    echo
    
    # Firebase configuration (optional)
    echo -e "${YELLOW}Firebase Configuration (Optional):${NC}"
    read -p "Do you want to configure Firebase Auth? (y/N): " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "Please paste your Firebase configuration JSON (press Ctrl+D when done):"
        firebase_config=$(cat)
        create_or_update_secret "firebase-config" "$firebase_config" $env
    else
        create_or_update_secret "firebase-config" "{}" $env
    fi
    
    log_success "All secrets configured for $env environment"
}

# Main function
main() {
    local environment=$1
    
    if [[ -z $environment ]]; then
        echo "Usage: $0 [dev|prod]"
        echo
        echo "This script helps you configure all required secrets for Green PM."
        echo
        echo "Before running this script, make sure you have:"
        echo "1. Stripe account with API keys"
        echo "2. Twilio account with phone number"
        echo "3. SendGrid account with API key"
        echo "4. (Optional) Firebase project configuration"
        echo
        exit 1
    fi
    
    if [[ "$environment" != "dev" && "$environment" != "prod" ]]; then
        log_error "Environment must be 'dev' or 'prod'"
        exit 1
    fi
    
    # Check if gcloud is authenticated
    if ! gcloud auth list --filter=status:ACTIVE --format="value(account)" | grep -q .; then
        log_error "No active gcloud authentication found. Please run 'gcloud auth login'"
        exit 1
    fi
    
    # Set project
    gcloud config set project $PROJECT_ID
    
    log_info "Setting up secrets for Green PM - $environment environment"
    log_warning "Make sure you have all required API keys ready!"
    echo
    
    read -p "Press Enter to continue or Ctrl+C to cancel..."
    echo
    
    setup_environment_secrets $environment
    
    echo
    log_success "Secret setup completed for $environment environment!"
    log_info "You can now deploy the applications using: ./scripts/deploy.sh apps $environment"
}

main "$@"