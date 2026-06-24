variable "project_id" {
  description = "GCP project ID for the Cloud SQL instance and related resources."
  type        = string
}

variable "region" {
  description = "Region for the Cloud SQL instance and PSC endpoint."
  type        = string
}

variable "instance_name" {
  description = "Name of the Cloud SQL instance."
  type        = string
  default     = "mynance-pg"
}

variable "database_version" {
  description = "Postgres engine version (e.g. POSTGRES_16)."
  type        = string
  default     = "POSTGRES_16"
}

variable "tier" {
  description = "Machine tier for the instance. db-f1-micro is cheapest (shared core, ~0.6GB RAM)."
  type        = string
  default     = "db-f1-micro"
}

variable "disk_size" {
  description = "Data disk size in GB."
  type        = number
  default     = 10
}

variable "database_name" {
  description = "Name of the application database to create."
  type        = string
  default     = "app"
}

variable "database_user" {
  description = "Name of the SQL user to create."
  type        = string
  default     = "mynance"
}

variable "db_password_secret_id" {
  description = "Secret Manager secret_id under which the DB password is stored."
  type        = string
  default     = "mynance-db-password"
}

variable "deletion_protection" {
  description = "Whether deletion protection is enabled on the instance."
  type        = bool
  default     = false
}

variable "backups_enabled" {
  description = "Whether automated backups are enabled (off by default to minimize cost)."
  type        = bool
  default     = false
}

variable "allowed_consumer_projects" {
  description = "Projects allowed to create PSC endpoints to this instance (usually [project_id])."
  type        = list(string)
}

# --- Network wiring (from the create-or-reference root locals) ---------------
variable "network_self_link" {
  description = "Self link of the VPC network hosting the PSC endpoint."
  type        = string
}

variable "subnet_self_link" {
  description = "Self link of the subnet in which the PSC internal IP is allocated."
  type        = string
}
