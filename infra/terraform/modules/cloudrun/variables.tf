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
