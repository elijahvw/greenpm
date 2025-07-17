# Green PM - Production Environment

terraform {
  backend "gcs" {
    bucket = "greenpm-prod-terraform-state"
    prefix = "terraform/state"
  }
}

module "greenpm_prod" {
  source = "../../"

  project_id   = "greenpm"
  region       = "us-central1"
  environment  = "prod"
  domain_name  = ""  # Will be updated when domain is available

  # Production-specific settings
  database_tier  = "db-custom-2-4096"
  min_instances  = 1
  max_instances  = 20
  cpu_limit      = "2000m"
  memory_limit   = "1Gi"
  enable_ssl     = true
}