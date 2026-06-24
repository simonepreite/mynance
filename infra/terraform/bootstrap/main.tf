###############################################################################
# bootstrap/ — solves the GCS remote-state chicken-and-egg problem.
#
# The root Terraform config (../) stores its state in a GCS bucket. But that
# bucket must already exist BEFORE `terraform init` can configure the gcs
# backend. This tiny config creates that VERSIONED state bucket and keeps its
# OWN state LOCAL (terraform.tfstate next to these files). Run it exactly once
# per project, then never again unless the bucket settings change.
#
# Order of operations (see ../README.md for full commands):
#   1) terraform -chdir=bootstrap init && apply   -> creates the state bucket
#   2) terraform init -backend-config=...          -> root uses that bucket
#   3) terraform apply                             -> deploys the stack
###############################################################################

terraform {
  required_version = ">= 1.5"

  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
  }

  # Intentionally NO backend block here: bootstrap keeps LOCAL state so it can
  # bring the remote-state bucket into existence in the first place.
}

provider "google" {
  project = var.project_id
  region  = var.region
}

# Enable the APIs strictly required to create the bucket. (The root config
# enables the full set it needs.)
resource "google_project_service" "storage" {
  count              = var.enable_apis ? 1 : 0
  project            = var.project_id
  service            = "storage.googleapis.com"
  disable_on_destroy = false
}

# Versioned, uniform-access GCS bucket that will hold the ROOT config's state.
resource "google_storage_bucket" "tf_state" {
  name     = var.state_bucket_name
  project  = var.project_id
  location = var.state_bucket_location

  # Versioning is mandatory for Terraform state: it lets you recover from a
  # corrupted or accidentally-overwritten state file.
  versioning {
    enabled = true
  }

  uniform_bucket_level_access = true

  # Defense in depth: block any public exposure of the state bucket.
  public_access_prevention = "enforced"

  # Keep a bounded number of old state versions to control cost while still
  # allowing recovery.
  lifecycle_rule {
    condition {
      num_newer_versions = var.state_version_retention
    }
    action {
      type = "Delete"
    }
  }

  # Never let `terraform destroy` of this bootstrap wipe the state bucket while
  # the root stack still depends on it.
  force_destroy = false

  depends_on = [google_project_service.storage]
}
