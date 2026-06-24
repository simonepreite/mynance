###############################################################################
# modules/network — CREATES a VPC + a single subnet.
#
# This module is only instantiated by the root config when the caller did NOT
# pass an existing network (i.e. var.network_self_link == ""). When the caller
# DOES pass existing self_links (Shared VPC / host project case) this module is
# never created (count = 0 at the call site) and the existing links are used
# verbatim. See ../../main.tf for that create-or-reference conditional.
###############################################################################

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }
}

resource "google_compute_network" "this" {
  project                 = var.project_id
  name                    = var.network_name
  auto_create_subnetworks = false
  routing_mode            = "REGIONAL"
}

resource "google_compute_subnetwork" "this" {
  project       = var.project_id
  name          = var.subnet_name
  region        = var.region
  network       = google_compute_network.this.id
  ip_cidr_range = var.subnet_cidr

  # Required for Direct VPC egress + Private Google Access from Cloud Run.
  private_ip_google_access = true
}
