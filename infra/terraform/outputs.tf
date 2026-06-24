output "lb_ip" {
  description = "Global static external IP of the load balancer. Create DNS A records app.<domain> and api.<domain> pointing here."
  value       = module.loadbalancer.lb_ip
}

output "https_enabled" {
  description = "Whether the HTTPS listener / managed certificate was provisioned (true once `domain` is set)."
  value       = module.loadbalancer.https_enabled
}

output "dns_authorization_record" {
  description = "CNAME record required by Certificate Manager to validate the domain (null until `domain` is set)."
  value       = module.loadbalancer.dns_authorization_record
}

output "network_self_link" {
  description = "Self link of the network in use (created or referenced)."
  value       = local.network_self_link
}

output "subnet_self_link" {
  description = "Self link of the subnet in use (created or referenced)."
  value       = local.subnet_self_link
}

output "network_created" {
  description = "True if this stack created the VPC/subnet; false if referencing an existing one."
  value       = local.create_network
}

output "cloudsql_instance_name" {
  description = "Cloud SQL instance name."
  value       = module.cloudsql.instance_name
}

output "cloudsql_connection_name" {
  description = "Cloud SQL connection name (project:region:instance)."
  value       = module.cloudsql.instance_connection_name
}

output "cloudsql_psc_ip" {
  description = "Internal PSC endpoint IP for the DB (backend POSTGRES_SERVER)."
  value       = module.cloudsql.psc_ip
}

output "db_password_secret_id" {
  description = "Secret Manager secret_id holding the DB password."
  value       = module.cloudsql.db_password_secret_id
}

output "backend_service_uri" {
  description = "Backend Cloud Run default URI (not directly reachable; ingress is internal LB only)."
  value       = module.backend.service_uri
}

output "frontend_service_uri" {
  description = "Frontend Cloud Run default URI (not directly reachable; ingress is internal LB only)."
  value       = module.frontend.service_uri
}

output "backend_service_account" {
  description = "Backend runtime service account email."
  value       = module.backend.service_account_email
}

output "frontend_service_account" {
  description = "Frontend runtime service account email."
  value       = module.frontend.service_account_email
}

output "backend_bucket_name" {
  description = "Name of the backend GCS bucket, or null when backend_bucket_enabled = false."
  value       = module.backend.bucket_name
}

output "frontend_bucket_name" {
  description = "Name of the frontend GCS bucket, or null when frontend_bucket_enabled = false."
  value       = module.frontend.bucket_name
}
