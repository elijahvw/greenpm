# Green PM - Development Environment

terraform {
  backend "gcs" {
    bucket = "greenpm-dev-terraform-state"
    prefix = "terraform/state"
  }
}

module "greenpm_dev" {
  source = "../../"

  project_id   = "greenpm"
  region       = "us-central1"
  environment  = "dev"
  domain_name  = ""  # Use default domain for dev

  # Development-specific settings
  database_tier  = "db-f1-micro"
  min_instances  = 0
  max_instances  = 5
  cpu_limit      = "1000m"
  memory_limit   = "512Mi"
  enable_ssl     = false
}