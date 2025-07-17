# VPC Module Outputs

output "network_name" {
  description = "VPC network name"
  value       = google_compute_network.vpc.name
}

output "network_self_link" {
  description = "VPC network self link"
  value       = google_compute_network.vpc.self_link
}

output "subnet_name" {
  description = "Subnet name"
  value       = google_compute_subnetwork.subnet.name
}

output "subnet_self_link" {
  description = "Subnet self link"
  value       = google_compute_subnetwork.subnet.self_link
}

output "vpc_connector_name" {
  description = "VPC connector name"
  value       = google_vpc_access_connector.connector.name
}

output "vpc_connector_self_link" {
  description = "VPC connector self link"
  value       = google_vpc_access_connector.connector.self_link
}

output "private_vpc_connection" {
  description = "Private VPC connection"
  value       = google_service_networking_connection.private_vpc_connection.network
}