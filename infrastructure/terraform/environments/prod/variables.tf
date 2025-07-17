# Green PM - Production Environment Variables

variable "environment" {
  description = "Environment name"
  type        = string
  default     = "prod"
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