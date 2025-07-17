# Storage Module for Green PM

# Documents bucket
resource "google_storage_bucket" "documents" {
  name          = "${var.app_name}-${var.environment}-documents-${random_id.bucket_suffix.hex}"
  location      = var.region
  project       = var.project_id
  force_destroy = var.environment != "prod"

  uniform_bucket_level_access = true

  versioning {
    enabled = var.environment == "prod"
  }

  lifecycle_rule {
    condition {
      age = var.environment == "prod" ? 365 : 90
    }
    action {
      type = "Delete"
    }
  }

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  labels = var.labels
}

# Property images bucket
resource "google_storage_bucket" "property_images" {
  name          = "${var.app_name}-${var.environment}-property-images-${random_id.bucket_suffix.hex}"
  location      = var.region
  project       = var.project_id
  force_destroy = var.environment != "prod"

  uniform_bucket_level_access = true

  versioning {
    enabled = false
  }

  lifecycle_rule {
    condition {
      age = var.environment == "prod" ? 730 : 180
    }
    action {
      type = "Delete"
    }
  }

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  labels = var.labels
}

# Maintenance images bucket
resource "google_storage_bucket" "maintenance_images" {
  name          = "${var.app_name}-${var.environment}-maintenance-images-${random_id.bucket_suffix.hex}"
  location      = var.region
  project       = var.project_id
  force_destroy = var.environment != "prod"

  uniform_bucket_level_access = true

  versioning {
    enabled = false
  }

  lifecycle_rule {
    condition {
      age = var.environment == "prod" ? 365 : 90
    }
    action {
      type = "Delete"
    }
  }

  cors {
    origin          = ["*"]
    method          = ["GET", "HEAD", "PUT", "POST", "DELETE"]
    response_header = ["*"]
    max_age_seconds = 3600
  }

  labels = var.labels
}

# Backup bucket
resource "google_storage_bucket" "backups" {
  name          = "${var.app_name}-${var.environment}-backups-${random_id.bucket_suffix.hex}"
  location      = var.region
  project       = var.project_id
  force_destroy = var.environment != "prod"

  uniform_bucket_level_access = true

  versioning {
    enabled = true
  }

  lifecycle_rule {
    condition {
      age = var.environment == "prod" ? 2555 : 30  # 7 years for prod, 30 days for dev
    }
    action {
      type = "Delete"
    }
  }

  labels = var.labels
}

# Random suffix for bucket names
resource "random_id" "bucket_suffix" {
  byte_length = 4
}

# IAM resources moved to separate storage_iam module to handle Cloud Run dependency