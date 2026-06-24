output "instance_name" {
  description = "Name of the Cloud SQL instance."
  value       = google_sql_database_instance.this.name
}

output "instance_connection_name" {
  description = "Cloud SQL connection name (project:region:instance), useful for the SQL Auth Proxy / cloudsql.client flows."
  value       = google_sql_database_instance.this.connection_name
}

output "psc_service_attachment_link" {
  description = "The instance's PSC service attachment link."
  value       = google_sql_database_instance.this.psc_service_attachment_link
}

output "psc_ip" {
  description = "Internal IP of the consumer PSC endpoint. Use as POSTGRES_SERVER for the backend."
  value       = google_compute_address.psc.address
}

output "database_name" {
  description = "Name of the created application database."
  value       = google_sql_database.app.name
}

output "database_user" {
  description = "Name of the created SQL user."
  value       = google_sql_user.app.name
}

output "db_password_secret_id" {
  description = "Secret Manager secret_id holding the DB password."
  value       = google_secret_manager_secret.db_password.secret_id
}

output "db_password_secret_name" {
  description = "Fully-qualified Secret Manager secret name (projects/.../secrets/...). Used by Cloud Run secret refs."
  value       = google_secret_manager_secret.db_password.name
}

output "db_password_secret_version" {
  description = "Resource name of the latest secret version."
  value       = google_secret_manager_secret_version.db_password.name
}
