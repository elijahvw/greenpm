# CI/CD Module Outputs

output "cloudbuild_service_account" {
  description = "Cloud Build service account email"
  value       = google_service_account.cloudbuild.email
}

output "trigger_ids" {
  description = "Cloud Build trigger IDs"
  value = {
    backend_dev   = var.enable_triggers && var.environment == "dev" && length(google_cloudbuild_trigger.backend_dev) > 0 ? google_cloudbuild_trigger.backend_dev[0].id : null
    frontend_dev  = var.enable_triggers && var.environment == "dev" && length(google_cloudbuild_trigger.frontend_dev) > 0 ? google_cloudbuild_trigger.frontend_dev[0].id : null
    backend_prod  = var.enable_triggers && var.environment == "prod" && length(google_cloudbuild_trigger.backend_prod) > 0 ? google_cloudbuild_trigger.backend_prod[0].id : null
    frontend_prod = var.enable_triggers && var.environment == "prod" && length(google_cloudbuild_trigger.frontend_prod) > 0 ? google_cloudbuild_trigger.frontend_prod[0].id : null
  }
}