variable "project_id" {
  description = "GCP project ID in which to create the VPC and subnet."
  type        = string
}

variable "region" {
  description = "Region for the subnet."
  type        = string
}

variable "network_name" {
  description = "Name of the VPC network to create."
  type        = string
  default     = "mynance-vpc"
}

variable "subnet_name" {
  description = "Name of the subnet to create."
  type        = string
  default     = "mynance-subnet"
}

variable "subnet_cidr" {
  description = "Primary IPv4 CIDR range for the subnet (used by Direct VPC egress and the PSC endpoint)."
  type        = string
  default     = "10.10.0.0/24"
}
