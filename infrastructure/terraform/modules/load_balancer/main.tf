# Load Balancer Module for Green PM

# Global IP address
resource "google_compute_global_address" "default" {
  name    = "${var.app_name}-${var.environment}-ip"
  project = var.project_id
}

# SSL Certificate (managed)
resource "google_compute_managed_ssl_certificate" "default" {
  count   = var.domain_name != "" ? 1 : 0
  name    = "${var.app_name}-${var.environment}-ssl-cert"
  project = var.project_id

  managed {
    domains = [var.domain_name, "www.${var.domain_name}"]
  }
}

# Self-signed SSL certificate for development
resource "google_compute_ssl_certificate" "self_signed" {
  count       = var.domain_name == "" ? 1 : 0
  name        = "${var.app_name}-${var.environment}-self-signed-cert"
  project     = var.project_id
  private_key = tls_private_key.default[0].private_key_pem
  certificate = tls_self_signed_cert.default[0].cert_pem
}

resource "tls_private_key" "default" {
  count     = var.domain_name == "" ? 1 : 0
  algorithm = "RSA"
  rsa_bits  = 2048
}

resource "tls_self_signed_cert" "default" {
  count           = var.domain_name == "" ? 1 : 0
  private_key_pem = tls_private_key.default[0].private_key_pem

  subject {
    common_name  = "${var.app_name}-${var.environment}.example.com"
    organization = "Green PM"
  }

  validity_period_hours = 8760 # 1 year

  allowed_uses = [
    "key_encipherment",
    "digital_signature",
    "server_auth",
  ]
}

# Backend service for API
resource "google_compute_backend_service" "api" {
  name        = "${var.app_name}-${var.environment}-api-backend"
  project     = var.project_id
  protocol    = "HTTP"
  timeout_sec = 30

  backend {
    group = google_compute_region_network_endpoint_group.api.id
  }

  health_checks = [google_compute_health_check.api.id]
}

# Backend service for frontend
resource "google_compute_backend_service" "frontend" {
  name        = "${var.app_name}-${var.environment}-frontend-backend"
  project     = var.project_id
  protocol    = "HTTP"
  timeout_sec = 30

  backend {
    group = google_compute_region_network_endpoint_group.frontend.id
  }

  health_checks = [google_compute_health_check.frontend.id]
}

# Network Endpoint Groups
resource "google_compute_region_network_endpoint_group" "api" {
  name                  = "${var.app_name}-${var.environment}-api-neg"
  project               = var.project_id
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = replace(var.backend_service_url, "https://", "")
  }
}

resource "google_compute_region_network_endpoint_group" "frontend" {
  name                  = "${var.app_name}-${var.environment}-frontend-neg"
  project               = var.project_id
  network_endpoint_type = "SERVERLESS"
  region                = var.region

  cloud_run {
    service = replace(var.frontend_service_url, "https://", "")
  }
}

# Health checks
resource "google_compute_health_check" "api" {
  name    = "${var.app_name}-${var.environment}-api-health-check"
  project = var.project_id

  http_health_check {
    request_path = "/health"
    port         = 8000
  }

  check_interval_sec  = 30
  timeout_sec         = 5
  healthy_threshold   = 2
  unhealthy_threshold = 3
}

resource "google_compute_health_check" "frontend" {
  name    = "${var.app_name}-${var.environment}-frontend-health-check"
  project = var.project_id

  http_health_check {
    request_path = "/"
    port         = 3000
  }

  check_interval_sec  = 30
  timeout_sec         = 5
  healthy_threshold   = 2
  unhealthy_threshold = 3
}

# URL Map
resource "google_compute_url_map" "default" {
  name            = "${var.app_name}-${var.environment}-url-map"
  project         = var.project_id
  default_service = google_compute_backend_service.frontend.id

  host_rule {
    hosts        = ["*"]
    path_matcher = "allpaths"
  }

  path_matcher {
    name            = "allpaths"
    default_service = google_compute_backend_service.frontend.id

    path_rule {
      paths   = ["/api/*", "/docs", "/redoc", "/openapi.json"]
      service = google_compute_backend_service.api.id
    }
  }
}

# HTTPS Proxy
resource "google_compute_target_https_proxy" "default" {
  name    = "${var.app_name}-${var.environment}-https-proxy"
  project = var.project_id
  url_map = google_compute_url_map.default.id

  ssl_certificates = var.domain_name != "" ? [
    google_compute_managed_ssl_certificate.default[0].id
  ] : [
    google_compute_ssl_certificate.self_signed[0].id
  ]
}

# HTTP Proxy (redirect to HTTPS)
resource "google_compute_target_http_proxy" "default" {
  name    = "${var.app_name}-${var.environment}-http-proxy"
  project = var.project_id
  url_map = google_compute_url_map.redirect_https.id
}

# URL Map for HTTP to HTTPS redirect
resource "google_compute_url_map" "redirect_https" {
  name    = "${var.app_name}-${var.environment}-redirect-https"
  project = var.project_id

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

# Global forwarding rules
resource "google_compute_global_forwarding_rule" "https" {
  name       = "${var.app_name}-${var.environment}-https-forwarding-rule"
  project    = var.project_id
  target     = google_compute_target_https_proxy.default.id
  port_range = "443"
  ip_address = google_compute_global_address.default.address
}

resource "google_compute_global_forwarding_rule" "http" {
  name       = "${var.app_name}-${var.environment}-http-forwarding-rule"
  project    = var.project_id
  target     = google_compute_target_http_proxy.default.id
  port_range = "80"
  ip_address = google_compute_global_address.default.address
}