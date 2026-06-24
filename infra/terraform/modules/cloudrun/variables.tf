variable "project_id" {
  description = "GCP project ID for the Cloud Run service."
  type        = string
}

variable "region" {
  description = "Region for the Cloud Run service."
  type        = string
}

variable "service_name" {
  description = "Name of the Cloud Run service."
  type        = string
}

variable "service_account_id" {
  description = "account_id (left part of the email) for this service's dedicated SA."
  type        = string
}

variable "image" {
  description = "Container image to deploy."
  type        = string
  default     = "us-docker.pkg.dev/cloudrun/container/hello"
}

variable "container_port" {
  description = "Port the container listens on."
  type        = number
  default     = 8080
}

variable "cpu" {
  description = "CPU limit per container."
  type        = string
  default     = "1"
}

variable "memory" {
  description = "Memory limit per container."
  type        = string
  default     = "512Mi"
}

variable "min_instances" {
  description = "Minimum instances (0 = scale to zero, cheapest)."
  type        = number
  default     = 0
}

variable "max_instances" {
  description = "Maximum instances."
  type        = number
  default     = 2
}

variable "vpc_egress" {
  description = "Direct VPC egress mode: PRIVATE_RANGES_ONLY or ALL_TRAFFIC."
  type        = string
  default     = "PRIVATE_RANGES_ONLY"
}

variable "network_self_link" {
  description = "Self link of the VPC network for direct VPC egress."
  type        = string
}

variable "subnet_self_link" {
  description = "Self link of the subnet for direct VPC egress."
  type        = string
}

variable "env" {
  description = "Map of plain (non-secret) environment variables."
  type        = map(string)
  default     = {}
}

variable "secret_env" {
  description = "Map of secret-backed env vars. Key = env name; value = { secret, version }."
  type = map(object({
    secret  = string
    version = string
  }))
  default = {}
}

# --- Optional GCS FUSE bucket persistence (DEFAULT OFF) ----------------------
# The mynance app is stateless (state in Cloud SQL; no file uploads), so this
# is OFF by default. When `bucket_enabled = false` the module provisions NO
# bucket, NO volume, NO mount and keeps the gen1 execution environment — i.e.
# byte-identical to the no-bucket behavior. Enable per service only if a
# persistent file mount is ever needed. See README for GCS-FUSE caveats
# (not POSIX: eventual consistency, no file locking, higher latency).
variable "bucket_enabled" {
  description = "Enable a GCS bucket + Cloud Storage FUSE volume mount for this service. Default OFF (app is stateless)."
  type        = bool
  default     = false
}

variable "bucket_name" {
  description = "Name of the GCS bucket to create when bucket_enabled = true. Globally unique."
  type        = string
  default     = ""
}

variable "bucket_mount_path" {
  description = "Container path where the bucket is mounted (only when bucket_enabled = true)."
  type        = string
  default     = "/mnt/data"
}

variable "bucket_force_destroy" {
  description = "Allow Terraform to destroy a non-empty bucket (only when bucket_enabled = true)."
  type        = bool
  default     = false
}

variable "bucket_versioning" {
  description = "Enable object versioning on the bucket (only when bucket_enabled = true)."
  type        = bool
  default     = false
}
