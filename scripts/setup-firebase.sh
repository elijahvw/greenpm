#!/bin/bash

# Green PM - Firebase Setup Script
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

echo "🔥 Firebase Setup for Green PM"
echo "================================"
echo

log_info "This script will help you set up Firebase for Green PM authentication."
echo

# Check if Firebase CLI is installed
if ! command -v firebase &> /dev/null; then
    log_warning "Firebase CLI is not installed. Installing now..."
    npm install -g firebase-tools
fi

# Login to Firebase
log_info "Please login to Firebase..."
firebase login

# Create Firebase project
log_info "Creating Firebase project..."
echo
echo "You have two options:"
echo "1. Create a new Firebase project"
echo "2. Use existing Firebase project"
echo

read -p "Choose option (1 or 2): " option

if [[ "$option" == "1" ]]; then
    read -p "Enter Firebase project ID (e.g., greenpm-dev): " firebase_project_id
    firebase projects:create $firebase_project_id --display-name "Green PM"
    log_success "Firebase project created: $firebase_project_id"
else
    firebase projects:list
    read -p "Enter existing Firebase project ID: " firebase_project_id
fi

# Set Firebase project
firebase use $firebase_project_id

# Enable Authentication
log_info "Enabling Firebase Authentication..."
firebase projects:list

echo
log_warning "Please complete the following steps in the Firebase Console:"
echo "1. Go to https://console.firebase.google.com/project/$firebase_project_id"
echo "2. Click on 'Authentication' in the left sidebar"
echo "3. Click 'Get started'"
echo "4. Go to 'Sign-in method' tab"
echo "5. Enable 'Email/Password' provider"
echo "6. (Optional) Enable 'Google' provider"
echo

read -p "Press Enter after completing the above steps..."

# Generate service account key
log_info "Generating service account key..."
mkdir -p config

# Create service account
gcloud iam service-accounts create firebase-admin-$firebase_project_id \
    --display-name="Firebase Admin for Green PM" \
    --project=$PROJECT_ID

# Grant necessary roles
gcloud projects add-iam-policy-binding $PROJECT_ID \
    --member="serviceAccount:firebase-admin-$firebase_project_id@$PROJECT_ID.iam.gserviceaccount.com" \
    --role="roles/firebase.admin"

# Generate and download key
gcloud iam service-accounts keys create config/firebase-admin-key.json \
    --iam-account=firebase-admin-$firebase_project_id@$PROJECT_ID.iam.gserviceaccount.com \
    --project=$PROJECT_ID

log_success "Service account key generated: config/firebase-admin-key.json"

# Get Firebase config for web app
echo
log_info "Now we need to create a web app in Firebase..."
echo
log_warning "Please complete the following steps:"
echo "1. Go to https://console.firebase.google.com/project/$firebase_project_id"
echo "2. Click on the gear icon (Project settings)"
echo "3. Scroll down to 'Your apps' section"
echo "4. Click 'Add app' and select the web icon (</>"
echo "5. Enter app nickname: 'Green PM Web'"
echo "6. Check 'Also set up Firebase Hosting' (optional)"
echo "7. Click 'Register app'"
echo "8. Copy the firebaseConfig object"
echo

read -p "Press Enter after completing the above steps..."

echo
echo "Please paste your Firebase config object here (the entire firebaseConfig = {...} part):"
echo "Example:"
echo 'const firebaseConfig = {'
echo '  apiKey: "your-api-key",'
echo '  authDomain: "your-project.firebaseapp.com",'
echo '  projectId: "your-project-id",'
echo '  storageBucket: "your-project.appspot.com",'
echo '  messagingSenderId: "123456789",'
echo '  appId: "your-app-id"'
echo '};'
echo
echo "Paste here (press Ctrl+D when done):"

# Read the config
firebase_web_config=$(cat)

# Extract just the JSON part
firebase_json=$(echo "$firebase_web_config" | sed -n 's/.*firebaseConfig = \({.*}\).*/\1/p')

if [[ -z "$firebase_json" ]]; then
    log_error "Could not parse Firebase config. Please try again."
    exit 1
fi

# Save to file
echo "$firebase_json" > config/firebase-web-config.json
log_success "Firebase web config saved to: config/firebase-web-config.json"

# Display next steps
echo
log_success "Firebase setup completed!"
echo
log_info "Next steps:"
echo "1. Use the service account key for backend: config/firebase-admin-key.json"
echo "2. Use the web config for frontend: config/firebase-web-config.json"
echo "3. Run the secrets setup script to configure these in Google Cloud"
echo
echo "To set up secrets:"
echo "  ./scripts/setup-secrets.sh dev"
echo "  ./scripts/setup-secrets.sh prod"