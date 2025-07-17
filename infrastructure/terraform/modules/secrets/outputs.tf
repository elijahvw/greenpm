# Secrets Module Outputs

output "secret_names" {
  description = "All secret names"
  value = {
    jwt_secret            = google_secret_manager_secret.jwt_secret.secret_id
    firebase_config       = google_secret_manager_secret.firebase_config.secret_id
    stripe_secret_key     = google_secret_manager_secret.stripe_secret_key.secret_id
    stripe_publishable_key = google_secret_manager_secret.stripe_publishable_key.secret_id
    stripe_webhook_secret = google_secret_manager_secret.stripe_webhook_secret.secret_id
    twilio_account_sid    = google_secret_manager_secret.twilio_account_sid.secret_id
    twilio_auth_token     = google_secret_manager_secret.twilio_auth_token.secret_id
    twilio_phone_number   = google_secret_manager_secret.twilio_phone_number.secret_id
    sendgrid_api_key      = google_secret_manager_secret.sendgrid_api_key.secret_id
    app_secret_key        = google_secret_manager_secret.app_secret_key.secret_id
    encryption_key        = google_secret_manager_secret.encryption_key.secret_id
  }
}