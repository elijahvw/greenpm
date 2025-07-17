# Green PM - Terraform Variables

variable "project_id" {
  description = "The GCP project ID"
  type        = string
  default     = "greenpm"
}

variable "region" {
  description = "The GCP region"
  type        = string
  default     = "us-central1"
}

variable "zone" {
  description = "The GCP zone"
  type        = string
  default     = "us-central1-a"
}

variable "environment" {
  description = "Environment name (dev, staging, prod)"
  type        = string
  validation {
    condition     = contains(["dev", "staging", "prod"], var.environment)
    error_message = "Environment must be dev, staging, or prod."
  }
}

variable "domain_name" {
  description = "Domain name for the application"
  type        = string
  default     = ""
}

variable "enable_ssl" {
  description = "Enable SSL certificate"
  type        = bool
  default     = true
}

variable "database_tier" {
  description = "Cloud SQL instance tier"
  type        = string
  default     = "db-f1-micro"
}

variable "min_instances" {
  description = "Minimum number of Cloud Run instances"
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum number of Cloud Run instances"
  type        = number
  default     = 10
}

variable "cpu_limit" {
  description = "CPU limit for Cloud Run services"
  type        = string
  default     = "1000m"
}

variable "memory_limit" {
  description = "Memory limit for Cloud Run services"
  type        = string
  default     = "512Mi"
}