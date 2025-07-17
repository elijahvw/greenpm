# Green PM - Main Terraform Configuration
terraform {
  required_version = ">= 1.0"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 5.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 5.0"
    }
  }
}

# Configure the Google Cloud Provider
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}

# Local values
locals {
  app_name = "greenpm"
  common_labels = {
    app         = local.app_name
    environment = var.environment
    managed_by  = "terraform"
  }
}

# Enable required APIs
resource "google_project_service" "required_apis" {
  for_each = toset([
    "compute.googleapis.com",
    "run.googleapis.com",
    "sql-component.googleapis.com",
    "sqladmin.googleapis.com",
    "storage.googleapis.com",
    "secretmanager.googleapis.com",
    "cloudbuild.googleapis.com",
    "firebase.googleapis.com",
    "identitytoolkit.googleapis.com",
    "cloudresourcemanager.googleapis.com",
    "iam.googleapis.com",
    "servicenetworking.googleapis.com"
  ])

  service = each.value
  project = var.project_id

  disable_dependent_services = true
}

# VPC Network
module "vpc" {
  source = "./modules/vpc"
  
  project_id   = var.project_id
  region       = var.region
  environment  = var.environment
  app_name     = local.app_name
  labels       = local.common_labels
  
  depends_on = [google_project_service.required_apis]
}

# Cloud SQL
module "database" {
  source = "./modules/database"
  
  project_id   = var.project_id
  region       = var.region
  environment  = var.environment
  app_name     = local.app_name
  labels       = local.common_labels
  vpc_network  = module.vpc.network_self_link
  
  depends_on = [google_project_service.required_apis, module.vpc]
}

# Cloud Storage
module "storage" {
  source = "./modules/storage"
  
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  app_name    = local.app_name
  labels      = local.common_labels
  
  depends_on = [google_project_service.required_apis]
}

# Secret Manager
module "secrets" {
  source = "./modules/secrets"
  
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  app_name    = local.app_name
  labels      = local.common_labels
  
  depends_on = [google_project_service.required_apis]
}

# Cloud Run Services
module "cloud_run" {
  source = "./modules/cloud_run"
  
  project_id     = var.project_id
  region         = var.region
  environment    = var.environment
  app_name       = local.app_name
  labels         = local.common_labels
  vpc_connector  = module.vpc.vpc_connector_id
  database_url   = module.database.connection_name
  
  depends_on = [
    google_project_service.required_apis,
    module.vpc,
    module.database,
    module.secrets
  ]
}

# Storage IAM - separate module to handle Cloud Run dependency
module "storage_iam" {
  source = "./modules/storage_iam"
  
  project_id                    = var.project_id
  backend_service_account_email = module.cloud_run.backend_service_account
  storage_buckets = {
    documents          = module.storage.documents_bucket_name
    property_images    = module.storage.property_images_bucket_name
    maintenance_images = module.storage.maintenance_images_bucket_name
    backups           = module.storage.backups_bucket_name
  }
  
  depends_on = [module.cloud_run, module.storage]
}

# Load Balancer
module "load_balancer" {
  source = "./modules/load_balancer"
  
  project_id          = var.project_id
  region              = var.region
  environment         = var.environment
  app_name            = local.app_name
  labels              = local.common_labels
  backend_service_url = module.cloud_run.backend_url
  frontend_service_url = module.cloud_run.frontend_url
  
  depends_on = [google_project_service.required_apis, module.cloud_run]
}

# CI/CD
module "cicd" {
  source = "./modules/cicd"
  
  project_id  = var.project_id
  region      = var.region
  environment = var.environment
  app_name    = local.app_name
  labels      = local.common_labels
  
  depends_on = [google_project_service.required_apis]
}