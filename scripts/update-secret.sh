#!/bin/bash

# Green PM - Update Single Secret Script
set -e

PROJECT_ID="greenpm"

if [[ $# -ne 3 ]]; then
    echo "Usage: $0 <environment> <secret-name> <secret-value>"
    echo
    echo "Available secrets:"
    echo "  stripe-secret-key"
    echo "  stripe-publishable-key" 
    echo "  stripe-webhook-secret"
    echo "  twilio-account-sid"
    echo "  twilio-auth-token"
    echo "  twilio-phone-number"
    echo "  sendgrid-api-key"
    echo "  firebase-config"
    echo
    echo "Examples:"
    echo "  $0 dev stripe-secret-key sk_test_..."
    echo "  $0 dev sendgrid-api-key SG...."
    echo "  $0 dev firebase-config '{\"apiKey\":\"...\"}'"
    exit 1
fi

ENVIRONMENT=$1
SECRET_NAME=$2
SECRET_VALUE=$3

FULL_SECRET_NAME="greenpm-${ENVIRONMENT}-${SECRET_NAME}"

echo "Updating secret: $FULL_SECRET_NAME"
echo "$SECRET_VALUE" | gcloud secrets versions add $FULL_SECRET_NAME --data-file=- --project=$PROJECT_ID

echo "✅ Secret updated successfully!"