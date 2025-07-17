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

# IAM for Cloud Run to access buckets
resource "google_storage_bucket_iam_member" "documents_object_admin" {
  bucket = google_storage_bucket.documents.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.app_name}-${var.environment}-backend@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_storage_bucket_iam_member" "property_images_object_admin" {
  bucket = google_storage_bucket.property_images.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.app_name}-${var.environment}-backend@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_storage_bucket_iam_member" "maintenance_images_object_admin" {
  bucket = google_storage_bucket.maintenance_images.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.app_name}-${var.environment}-backend@${var.project_id}.iam.gserviceaccount.com"
}

resource "google_storage_bucket_iam_member" "backups_object_admin" {
  bucket = google_storage_bucket.backups.name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.app_name}-${var.environment}-backend@${var.project_id}.iam.gserviceaccount.com"
}