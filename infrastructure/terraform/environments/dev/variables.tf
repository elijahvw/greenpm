# Green PM - Development Environment Variables

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "dev"
}

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