###############################################################################
# Root variables — everything is parametric with cost-minimal defaults.
###############################################################################

# --- Core --------------------------------------------------------------------
variable "project_id" {
  description = "GCP project ID where the stack is deployed."
  type        = string
}

variable "region" {
  description = "Primary region for all regional resources (Cloud Run, Cloud SQL, subnet, NEGs)."
  type        = string
  default     = "europe-west1"
}

variable "name_prefix" {
  description = "Prefix used to name resources (LB, IPs, etc.)."
  type        = string
  default     = "mynance"
}

variable "enable_apis" {
  description = "Whether to enable the required Google APIs via google_project_service."
  type        = bool
  default     = true
}

# --- Networking: create-or-reference -----------------------------------------
# Leave both empty to CREATE a VPC + subnet (via modules/network). Provide both
# self_links to REFERENCE an existing network (e.g. a Shared VPC on a host
# project). host_project_id is informational/Shared-VPC context.
variable "network_self_link" {
  description = "Existing VPC self link. Empty => create a new VPC."
  type        = string
  default     = ""
}

variable "subnet_self_link" {
  description = "Existing subnet self link. Empty => create a new subnet."
  type        = string
  default     = ""
}

variable "host_project_id" {
  description = "Host project ID when using a Shared VPC (informational; networks live there)."
  type        = string
  default     = ""
}

variable "network_name" {
  description = "Name for the VPC to create (only used when creating)."
  type        = string
  default     = "mynance-vpc"
}

variable "subnet_name" {
  description = "Name for the subnet to create (only used when creating)."
  type        = string
  default     = "mynance-subnet"
}

variable "subnet_cidr" {
  description = "CIDR for the subnet to create (only used when creating)."
  type        = string
  default     = "10.10.0.0/24"
}

# --- Cloud SQL ---------------------------------------------------------------
variable "db_instance_name" {
  description = "Cloud SQL instance name."
  type        = string
  default     = "mynance-pg"
}

variable "db_version" {
  description = "Postgres version."
  type        = string
  default     = "POSTGRES_16"
}

variable "db_tier" {
  description = "Cloud SQL tier (db-f1-micro is cheapest; ~0.6GB RAM — see README caveat)."
  type        = string
  default     = "db-f1-micro"
}

variable "db_disk_size" {
  description = "Cloud SQL data disk size in GB."
  type        = number
  default     = 10
}

variable "db_name" {
  description = "Application database name (becomes POSTGRES_DB)."
  type        = string
  default     = "app"
}

variable "db_user" {
  description = "Application SQL user (becomes POSTGRES_USER)."
  type        = string
  default     = "mynance"
}

variable "db_password_secret_id" {
  description = "Secret Manager secret_id for the DB password."
  type        = string
  default     = "mynance-db-password"
}

variable "db_deletion_protection" {
  description = "Enable deletion protection on the SQL instance."
  type        = bool
  default     = false
}

variable "db_backups_enabled" {
  description = "Enable automated backups (off by default to minimize cost)."
  type        = bool
  default     = false
}

variable "db_port" {
  description = "Postgres port exposed to the backend (POSTGRES_PORT)."
  type        = number
  default     = 5432
}

# --- Cloud Run (shared) ------------------------------------------------------
variable "cloudrun_min_instances" {
  description = "Min instances for both services (0 = scale to zero)."
  type        = number
  default     = 0
}

variable "cloudrun_max_instances" {
  description = "Max instances for both services."
  type        = number
  default     = 2
}

variable "cloudrun_cpu" {
  description = "CPU limit per container."
  type        = string
  default     = "1"
}

variable "cloudrun_memory" {
  description = "Memory limit per container."
  type        = string
  default     = "512Mi"
}

# --- Cloud Run images (per service) ------------------------------------------
variable "backend_image" {
  description = "Backend container image."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "frontend_image" {
  description = "Frontend container image (built WITH VITE_API_URL baked in — see README)."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "backend_container_port" {
  description = "Port the backend container listens on."
  type        = number
  default     = 8080
}

variable "frontend_container_port" {
  description = "Port the frontend container listens on."
  type        = number
  default     = 8080
}

# --- App / domain ------------------------------------------------------------
variable "domain" {
  description = "Base domain. app.<domain> -> FE, api.<domain> -> BE. Empty => HTTP-only LB (no cert)."
  type        = string
  default     = ""
}

variable "environment" {
  description = "App ENVIRONMENT value (local|staging|production)."
  type        = string
  default     = "production"
}

variable "project_name" {
  description = "App PROJECT_NAME value."
  type        = string
  default     = "mynance"
}

variable "extra_backend_env" {
  description = "Additional plain env vars merged into the backend service (e.g. SECRET_KEY via your own secret pipeline, SENTRY_DSN)."
  type        = map(string)
  default     = {}
}

variable "extra_frontend_env" {
  description = "Additional plain env vars merged into the frontend service."
  type        = map(string)
  default     = {}
}

# --- Optional GCS FUSE persistence (DEFAULT OFF, per service) ----------------
# The app is stateless (state in Cloud SQL; no file uploads), so these default
# to false and provision NOTHING. Enable a bucket per service ONLY if a
# persistent file mount is ever needed. See README for the GCS-FUSE caveats
# (not a POSIX filesystem; not for databases/SQLite).
variable "backend_bucket_enabled" {
  description = "Provision a GCS bucket + FUSE mount for the backend service. Default OFF."
  type        = bool
  default     = false
}

variable "backend_bucket_name" {
  description = "Name of the backend GCS bucket. Empty => derived from project + service. Globally unique."
  type        = string
  default     = ""
}

variable "backend_bucket_mount_path" {
  description = "Container mount path for the backend bucket (only when enabled)."
  type        = string
  default     = "/mnt/data"
}

variable "backend_bucket_force_destroy" {
  description = "Allow Terraform to destroy a non-empty backend bucket (only when enabled)."
  type        = bool
  default     = false
}

variable "backend_bucket_versioning" {
  description = "Enable object versioning on the backend bucket (only when enabled)."
  type        = bool
  default     = false
}

variable "frontend_bucket_enabled" {
  description = "Provision a GCS bucket + FUSE mount for the frontend service. Default OFF."
  type        = bool
  default     = false
}

variable "frontend_bucket_name" {
  description = "Name of the frontend GCS bucket. Empty => derived from project + service. Globally unique."
  type        = string
  default     = ""
}

variable "frontend_bucket_mount_path" {
  description = "Container mount path for the frontend bucket (only when enabled)."
  type        = string
  default     = "/mnt/data"
}

variable "frontend_bucket_force_destroy" {
  description = "Allow Terraform to destroy a non-empty frontend bucket (only when enabled)."
  type        = bool
  default     = false
}

variable "frontend_bucket_versioning" {
  description = "Enable object versioning on the frontend bucket (only when enabled)."
  type        = bool
  default     = false
}
