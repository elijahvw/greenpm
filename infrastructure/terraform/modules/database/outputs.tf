# Database Module Outputs

output "instance_name" {
  description = "Cloud SQL instance name"
  value       = google_sql_database_instance.main.name
}

output "connection_name" {
  description = "Cloud SQL connection name"
  value       = google_sql_database_instance.main.connection_name
}

output "private_ip" {
  description = "Cloud SQL private IP address"
  value       = google_sql_database_instance.main.private_ip_address
  sensitive   = true
}

output "database_name" {
  description = "Database name"
  value       = google_sql_database.database.name
}

output "database_user" {
  description = "Database user"
  value       = google_sql_user.user.name
}

output "db_password_secret_name" {
  description = "Database password secret name"
  value       = google_secret_manager_secret.db_password.secret_id
}

output "db_url_secret_name" {
  description = "Database URL secret name"
  value       = google_secret_manager_secret.db_url.secret_id
}