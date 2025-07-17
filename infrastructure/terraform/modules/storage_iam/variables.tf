# Storage IAM Module Variables

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "backend_service_account_email" {
  description = "Backend service account email"
  type        = string
}

variable "storage_buckets" {
  description = "Storage bucket names"
  type = object({
    documents          = string
    property_images    = string
    maintenance_images = string
    backups           = string
  })
}