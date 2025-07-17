# Cloud Run Module Outputs

output "backend_service_name" {
  description = "Backend service name"
  value       = google_cloud_run_v2_service.backend.name
}

output "frontend_service_name" {
  description = "Frontend service name"
  value       = google_cloud_run_v2_service.frontend.name
}

output "backend_url" {
  description = "Backend service URL"
  value       = google_cloud_run_v2_service.backend.uri
}

output "frontend_url" {
  description = "Frontend service URL"
  value       = google_cloud_run_v2_service.frontend.uri
}

output "backend_service_account" {
  description = "Backend service account email"
  value       = google_service_account.backend.email
}

output "frontend_service_account" {
  description = "Frontend service account email"
  value       = google_service_account.frontend.email
}