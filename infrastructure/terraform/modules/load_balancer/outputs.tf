# Load Balancer Module Outputs

output "ip_address" {
  description = "Load balancer IP address"
  value       = google_compute_global_address.default.address
}

output "ssl_certificate_name" {
  description = "SSL certificate name"
  value       = var.domain_name != "" ? google_compute_managed_ssl_certificate.default[0].name : google_compute_ssl_certificate.self_signed[0].name
}

output "url_map_name" {
  description = "URL map name"
  value       = google_compute_url_map.default.name
}

output "backend_service_names" {
  description = "Backend service names"
  value = {
    api      = google_compute_backend_service.api.name
    frontend = google_compute_backend_service.frontend.name
  }
}