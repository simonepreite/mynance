output "state_bucket_name" {
  description = "Name of the GCS bucket holding root Terraform state. Pass this to the root `terraform init -backend-config=\"bucket=...\"`."
  value       = google_storage_bucket.tf_state.name
}

output "state_bucket_url" {
  description = "gs:// URL of the state bucket."
  value       = google_storage_bucket.tf_state.url
}
