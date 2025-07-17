# Green PM - Terraform Outputs

output "project_id" {
  description = "GCP Project ID"
  value       = var.project_id
}

output "region" {
  description = "GCP Region"
  value       = var.region
}

output "environment" {
  description = "Environment"
  value       = var.environment
}

output "vpc_network_name" {
  description = "VPC network name"
  value       = module.vpc.network_name
}

output "database_connection_name" {
  description = "Cloud SQL connection name"
  value       = module.database.connection_name
}

output "database_private_ip" {
  description = "Cloud SQL private IP"
  value       = module.database.private_ip
  sensitive   = true
}

output "storage_bucket_names" {
  description = "Cloud Storage bucket names"
  value       = module.storage.bucket_names
}

output "backend_service_url" {
  description = "Backend Cloud Run service URL"
  value       = module.cloud_run.backend_url
}

output "frontend_service_url" {
  description = "Frontend Cloud Run service URL"
  value       = module.cloud_run.frontend_url
}

output "load_balancer_ip" {
  description = "Load balancer IP address"
  value       = module.load_balancer.ip_address
}

output "ssl_certificate_name" {
  description = "SSL certificate name"
  value       = module.load_balancer.ssl_certificate_name
}

output "cloud_build_trigger_ids" {
  description = "Cloud Build trigger IDs"
  value       = module.cicd.trigger_ids
}