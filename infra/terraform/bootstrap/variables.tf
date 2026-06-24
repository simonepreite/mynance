variable "project_id" {
  description = "GCP project ID that will own the Terraform state bucket."
  type        = string
}

variable "region" {
  description = "Default region for the bootstrap provider (does not affect bucket location)."
  type        = string
  default     = "europe-west1"
}

variable "state_bucket_name" {
  description = "Globally-unique name for the GCS bucket that stores the root config's Terraform state."
  type        = string
}

variable "state_bucket_location" {
  description = "Location for the state bucket (region or multi-region, e.g. EU, US, europe-west1)."
  type        = string
  default     = "EU"
}

variable "state_version_retention" {
  description = "How many older (non-current) state object versions to keep before deletion."
  type        = number
  default     = 10
}

variable "enable_apis" {
  description = "Whether to enable the storage API on the project (set false if managed elsewhere)."
  type        = bool
  default     = true
}
