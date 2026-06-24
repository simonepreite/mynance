variable "project_id" {
  description = "GCP project ID for the load balancer resources."
  type        = string
}

variable "region" {
  description = "Region where the Cloud Run services (and thus the serverless NEGs) live."
  type        = string
}

variable "name_prefix" {
  description = "Prefix for all LB resource names."
  type        = string
  default     = "mynance"
}

variable "domain" {
  description = "Base domain; subdomains app.<domain> and api.<domain> are routed. Empty => HTTP-only."
  type        = string
  default     = ""
}

variable "enable_https" {
  description = "Whether to provision Certificate Manager + HTTPS listener. Set from local.enable_https in the root."
  type        = bool
}

variable "frontend_service_name" {
  description = "Name of the frontend Cloud Run service (for the serverless NEG)."
  type        = string
}

variable "backend_service_name" {
  description = "Name of the backend Cloud Run service (for the serverless NEG)."
  type        = string
}
