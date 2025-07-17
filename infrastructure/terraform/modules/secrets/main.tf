# Secrets Module for Green PM

# JWT Secret
resource "google_secret_manager_secret" "jwt_secret" {
  secret_id = "${var.app_name}-${var.environment}-jwt-secret"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

resource "random_password" "jwt_secret" {
  length  = 32
  special = true
}

resource "google_secret_manager_secret_version" "jwt_secret" {
  secret      = google_secret_manager_secret.jwt_secret.id
  secret_data = random_password.jwt_secret.result
}

# Firebase Config
resource "google_secret_manager_secret" "firebase_config" {
  secret_id = "${var.app_name}-${var.environment}-firebase-config"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

# Stripe API Keys
resource "google_secret_manager_secret" "stripe_secret_key" {
  secret_id = "${var.app_name}-${var.environment}-stripe-secret-key"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

resource "google_secret_manager_secret" "stripe_publishable_key" {
  secret_id = "${var.app_name}-${var.environment}-stripe-publishable-key"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

resource "google_secret_manager_secret" "stripe_webhook_secret" {
  secret_id = "${var.app_name}-${var.environment}-stripe-webhook-secret"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

# Twilio API Keys
resource "google_secret_manager_secret" "twilio_account_sid" {
  secret_id = "${var.app_name}-${var.environment}-twilio-account-sid"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

resource "google_secret_manager_secret" "twilio_auth_token" {
  secret_id = "${var.app_name}-${var.environment}-twilio-auth-token"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

resource "google_secret_manager_secret" "twilio_phone_number" {
  secret_id = "${var.app_name}-${var.environment}-twilio-phone-number"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

# SendGrid API Key
resource "google_secret_manager_secret" "sendgrid_api_key" {
  secret_id = "${var.app_name}-${var.environment}-sendgrid-api-key"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

# Application Secret Key
resource "google_secret_manager_secret" "app_secret_key" {
  secret_id = "${var.app_name}-${var.environment}-app-secret-key"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

resource "random_password" "app_secret_key" {
  length  = 32
  special = true
}

resource "google_secret_manager_secret_version" "app_secret_key" {
  secret      = google_secret_manager_secret.app_secret_key.id
  secret_data = random_password.app_secret_key.result
}

# Encryption Key
resource "google_secret_manager_secret" "encryption_key" {
  secret_id = "${var.app_name}-${var.environment}-encryption-key"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

resource "random_password" "encryption_key" {
  length  = 32
  special = false
}

resource "google_secret_manager_secret_version" "encryption_key" {
  secret      = google_secret_manager_secret.encryption_key.id
  secret_data = base64encode(random_password.encryption_key.result)
}