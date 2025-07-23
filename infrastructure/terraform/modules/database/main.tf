# Database Module for Green PM

# Random password for database
resource "random_password" "db_password" {
  length  = 16
  special = true
}

# Cloud SQL Instance
resource "google_sql_database_instance" "main" {
  name             = "${var.app_name}-${var.environment}-db"
  database_version = "POSTGRES_15"
  region           = var.region
  project          = var.project_id

  deletion_protection = var.environment == "prod" ? true : false

  settings {
    tier                        = var.database_tier
    availability_type           = var.environment == "prod" ? "REGIONAL" : "ZONAL"
    disk_type                   = "PD_SSD"
    disk_size                   = var.environment == "prod" ? 100 : 20
    disk_autoresize             = true
    disk_autoresize_limit       = var.environment == "prod" ? 500 : 100

    backup_configuration {
      enabled                        = true
      start_time                     = "03:00"
      point_in_time_recovery_enabled = true
      backup_retention_settings {
        retained_backups = var.environment == "prod" ? 30 : 7
      }
    }

    ip_configuration {
      ipv4_enabled                                  = var.environment == "dev" ? true : false
      private_network                               = var.vpc_network
      enable_private_path_for_google_cloud_services = true
      
      # Allow access from anywhere for dev environment (restrict in production)
      dynamic "authorized_networks" {
        for_each = var.environment == "dev" ? [1] : []
        content {
          name  = "allow-all-dev"
          value = "0.0.0.0/0"
        }
      }
    }

    database_flags {
      name  = "log_checkpoints"
      value = "on"
    }

    database_flags {
      name  = "log_connections"
      value = "on"
    }

    database_flags {
      name  = "log_disconnections"
      value = "on"
    }

    database_flags {
      name  = "log_lock_waits"
      value = "on"
    }

    user_labels = var.labels
  }

  depends_on = [var.vpc_network]
}

# Database
resource "google_sql_database" "database" {
  name     = "${var.app_name}_${var.environment}"
  instance = google_sql_database_instance.main.name
  project  = var.project_id
}

# Database user
resource "google_sql_user" "user" {
  name     = "${var.app_name}_user"
  instance = google_sql_database_instance.main.name
  password = random_password.db_password.result
  project  = var.project_id
}

# Store database credentials in Secret Manager
resource "google_secret_manager_secret" "db_password" {
  secret_id = "${var.app_name}-${var.environment}-db-password"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db_password.result
}

resource "google_secret_manager_secret" "db_url" {
  secret_id = "${var.app_name}-${var.environment}-db-url"
  project   = var.project_id

  replication {
    auto {}
  }

  labels = var.labels
}

resource "google_secret_manager_secret_version" "db_url" {
  secret = google_secret_manager_secret.db_url.id
  secret_data = "postgresql://${google_sql_user.user.name}:${random_password.db_password.result}@${google_sql_database_instance.main.private_ip_address}:5432/${google_sql_database.database.name}"
}