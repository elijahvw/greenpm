# Storage Module Outputs

output "documents_bucket_name" {
  description = "Documents bucket name"
  value       = google_storage_bucket.documents.name
}

output "property_images_bucket_name" {
  description = "Property images bucket name"
  value       = google_storage_bucket.property_images.name
}

output "maintenance_images_bucket_name" {
  description = "Maintenance images bucket name"
  value       = google_storage_bucket.maintenance_images.name
}

output "backups_bucket_name" {
  description = "Backups bucket name"
  value       = google_storage_bucket.backups.name
}

output "bucket_names" {
  description = "All bucket names"
  value = {
    documents          = google_storage_bucket.documents.name
    property_images    = google_storage_bucket.property_images.name
    maintenance_images = google_storage_bucket.maintenance_images.name
    backups           = google_storage_bucket.backups.name
  }
}