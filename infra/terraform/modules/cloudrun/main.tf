###############################################################################
# modules/cloudrun — one reusable Cloud Run v2 service.
#
# Instantiated TWICE by the root config (frontend + backend). Each instance
# gets its own dedicated service account. Common traits:
#   - Direct VPC egress into the given subnet (NOT a Serverless VPC connector).
#   - Ingress restricted to the internal HTTP(S) load balancer.
#   - Cost-minimal scaling (scale to zero) and a 1 vCPU / 512Mi container.
#   - Plain env vars + (optionally) secret-backed env vars from Secret Manager.
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

# Dedicated runtime service account for this service.
resource "google_service_account" "this" {
  project      = var.project_id
  account_id   = var.service_account_id
  display_name = "Runtime SA for Cloud Run service ${var.service_name}"
}

# --- Optional GCS bucket (DEFAULT OFF) ---------------------------------------
# Gated entirely on var.bucket_enabled. When false: zero resources created.
locals {
  bucket_enabled = var.bucket_enabled
  # Stable internal name for the Cloud Run volume <-> mount pairing.
  bucket_volume_name = "gcs-data"
}

resource "google_storage_bucket" "this" {
  count = local.bucket_enabled ? 1 : 0

  project                     = var.project_id
  name                        = var.bucket_name
  location                    = var.region
  uniform_bucket_level_access = true
  force_destroy               = var.bucket_force_destroy

  versioning {
    enabled = var.bucket_versioning
  }
}

# Runtime SA gets object-level admin on its own bucket (read/write objects).
resource "google_storage_bucket_iam_member" "this" {
  count = local.bucket_enabled ? 1 : 0

  bucket = google_storage_bucket.this[0].name
  role   = "roles/storage.objectAdmin"
  member = "serviceAccount:${google_service_account.this.email}"
}

resource "google_cloud_run_v2_service" "this" {
  project  = var.project_id
  name     = var.service_name
  location = var.region

  # Reachable only through the internal/external HTTP(S) load balancer.
  ingress = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  deletion_protection = false

  template {
    service_account = google_service_account.this.email

    # GCS FUSE volume mounts require the gen2 execution environment. Only set
    # it when a bucket is actually mounted; otherwise leave it to the Cloud Run
    # default (unset) so disabled services are byte-identical to before.
    execution_environment = local.bucket_enabled ? "EXECUTION_ENVIRONMENT_GEN2" : null

    scaling {
      min_instance_count = var.min_instances
      max_instance_count = var.max_instances
    }

    # Direct VPC egress: attach the service ENI directly to the subnet. No
    # Serverless VPC Access connector is provisioned.
    vpc_access {
      network_interfaces {
        network    = var.network_self_link
        subnetwork = var.subnet_self_link
      }
      # PRIVATE_RANGES_ONLY keeps public traffic off the VPC path (cheaper,
      # and the only private destinations are the PSC endpoint / Google APIs).
      egress = var.vpc_egress
    }

    containers {
      image = var.image

      resources {
        cpu_idle = true
        limits = {
          cpu    = var.cpu
          memory = var.memory
        }
      }

      ports {
        container_port = var.container_port
      }

      # Plain (non-secret) environment variables.
      dynamic "env" {
        for_each = var.env
        content {
          name  = env.key
          value = env.value
        }
      }

      # Secret-backed environment variables sourced from Secret Manager.
      dynamic "env" {
        for_each = var.secret_env
        content {
          name = env.key
          value_source {
            secret_key_ref {
              secret  = env.value.secret
              version = env.value.version
            }
          }
        }
      }

      # Mount the GCS FUSE volume into the container (only when enabled).
      dynamic "volume_mounts" {
        for_each = local.bucket_enabled ? [1] : []
        content {
          name       = local.bucket_volume_name
          mount_path = var.bucket_mount_path
        }
      }
    }

    # Cloud Storage FUSE volume backed by the bucket (only when enabled).
    dynamic "volumes" {
      for_each = local.bucket_enabled ? [1] : []
      content {
        name = local.bucket_volume_name
        gcs {
          bucket    = google_storage_bucket.this[0].name
          read_only = false
        }
      }
    }
  }

  lifecycle {
    # The image is typically rolled by CI/CD outside Terraform; uncomment to
    # let Terraform stop fighting external image updates:
    # ignore_changes = [template[0].containers[0].image]
  }
}
