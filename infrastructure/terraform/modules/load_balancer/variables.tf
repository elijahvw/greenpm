# Load Balancer Module Variables

variable "project_id" {
  description = "GCP project ID"
  type        = string
}

variable "region" {
  description = "GCP region"
  type        = string
}

variable "environment" {
  description = "Environment name"
  type        = string
}

variable "app_name" {
  description = "Application name"
  type        = string
}

variable "labels" {
  description = "Labels to apply to resources"
  type        = map(string)
  default     = {}
}

variable "backend_service_url" {
  description = "Backend Cloud Run service URL"
  type        = string
}

variable "frontend_service_url" {
  description = "Frontend Cloud Run service URL"
  type        = string
}

variable "domain_name" {
  description = "Domain name for SSL certificate"
  type        = string
  default     = ""
}