# CI/CD Module for Green PM

# Cloud Build Service Account
resource "google_service_account" "cloudbuild" {
  account_id   = "${var.app_name}-${var.environment}-cloudbuild"
  display_name = "Green PM Cloud Build Service Account"
  project      = var.project_id
}

# IAM roles for Cloud Build
resource "google_project_iam_member" "cloudbuild_editor" {
  project = var.project_id
  role    = "roles/editor"
  member  = "serviceAccount:${google_service_account.cloudbuild.email}"
}

resource "google_project_iam_member" "cloudbuild_run_admin" {
  project = var.project_id
  role    = "roles/run.admin"
  member  = "serviceAccount:${google_service_account.cloudbuild.email}"
}

resource "google_project_iam_member" "cloudbuild_storage_admin" {
  project = var.project_id
  role    = "roles/storage.admin"
  member  = "serviceAccount:${google_service_account.cloudbuild.email}"
}

resource "google_project_iam_member" "cloudbuild_secret_accessor" {
  project = var.project_id
  role    = "roles/secretmanager.secretAccessor"
  member  = "serviceAccount:${google_service_account.cloudbuild.email}"
}

# GitHub connection (requires manual setup)
resource "google_cloudbuild_trigger" "backend_dev" {
  count       = var.enable_triggers && var.environment == "dev" ? 1 : 0
  name        = "${var.app_name}-backend-dev-trigger"
  project     = var.project_id
  description = "Trigger for backend development builds"

  github {
    owner = "YOUR_GITHUB_USERNAME"  # Replace with actual username
    name  = "greenpm"               # Replace with actual repo name
    push {
      branch = "^dev$"
    }
  }

  filename = "backend/cloudbuild.yaml"

  substitutions = {
    _ENVIRONMENT = "dev"
    _SERVICE_NAME = "${var.app_name}-${var.environment}-backend"
    _REGION = var.region
  }

  service_account = google_service_account.cloudbuild.id
}

resource "google_cloudbuild_trigger" "frontend_dev" {
  count       = var.enable_triggers && var.environment == "dev" ? 1 : 0
  name        = "${var.app_name}-frontend-dev-trigger"
  project     = var.project_id
  description = "Trigger for frontend development builds"

  github {
    owner = "YOUR_GITHUB_USERNAME"  # Replace with actual username
    name  = "greenpm"               # Replace with actual repo name
    push {
      branch = "^dev$"
    }
  }

  filename = "frontend/cloudbuild.yaml"

  substitutions = {
    _ENVIRONMENT = "dev"
    _SERVICE_NAME = "${var.app_name}-${var.environment}-frontend"
    _REGION = var.region
  }

  service_account = google_service_account.cloudbuild.id
}

resource "google_cloudbuild_trigger" "backend_prod" {
  count       = var.enable_triggers && var.environment == "prod" ? 1 : 0
  name        = "${var.app_name}-backend-prod-trigger"
  project     = var.project_id
  description = "Trigger for backend production builds"

  github {
    owner = "YOUR_GITHUB_USERNAME"  # Replace with actual username
    name  = "greenpm"               # Replace with actual repo name
    push {
      branch = "^main$"
    }
  }

  filename = "backend/cloudbuild.yaml"

  substitutions = {
    _ENVIRONMENT = "prod"
    _SERVICE_NAME = "${var.app_name}-${var.environment}-backend"
    _REGION = var.region
  }

  service_account = google_service_account.cloudbuild.id
}

resource "google_cloudbuild_trigger" "frontend_prod" {
  count       = var.enable_triggers && var.environment == "prod" ? 1 : 0
  name        = "${var.app_name}-frontend-prod-trigger"
  project     = var.project_id
  description = "Trigger for frontend production builds"

  github {
    owner = "YOUR_GITHUB_USERNAME"  # Replace with actual username
    name  = "greenpm"               # Replace with actual repo name
    push {
      branch = "^main$"
    }
  }

  filename = "frontend/cloudbuild.yaml"

  substitutions = {
    _ENVIRONMENT = "prod"
    _SERVICE_NAME = "${var.app_name}-${var.environment}-frontend"
    _REGION = var.region
  }

  service_account = google_service_account.cloudbuild.id
}