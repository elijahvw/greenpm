# Storage IAM Module for Green PM

# IAM for Cloud Run to access buckets
resource "google_storage_bucket_iam_member" "documents_object_admin" {
  bucket = var.storage_buckets.documents
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.backend_service_account_email}"
}

resource "google_storage_bucket_iam_member" "property_images_object_admin" {
  bucket = var.storage_buckets.property_images
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.backend_service_account_email}"
}

resource "google_storage_bucket_iam_member" "maintenance_images_object_admin" {
  bucket = var.storage_buckets.maintenance_images
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.backend_service_account_email}"
}

resource "google_storage_bucket_iam_member" "backups_object_admin" {
  bucket = var.storage_buckets.backups
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${var.backend_service_account_email}"
}