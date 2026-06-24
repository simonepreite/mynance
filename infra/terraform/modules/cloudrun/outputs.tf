output "service_name" {
  description = "Name of the Cloud Run service."
  value       = google_cloud_run_v2_service.this.name
}

output "service_id" {
  description = "Full resource ID of the Cloud Run service."
  value       = google_cloud_run_v2_service.this.id
}

output "service_uri" {
  description = "Default run.app URI (note: not reachable directly due to internal-LB ingress)."
  value       = google_cloud_run_v2_service.this.uri
}

output "service_account_email" {
  description = "Email of the dedicated runtime service account."
  value       = google_service_account.this.email
}

output "location" {
  description = "Region of the service (used to build the serverless NEG)."
  value       = google_cloud_run_v2_service.this.location
}

output "bucket_name" {
  description = "Name of the GCS bucket mounted into this service, or null when bucket_enabled = false."
  value       = local.bucket_enabled ? google_storage_bucket.this[0].name : null
}
