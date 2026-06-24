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

resource "google_cloud_run_v2_service" "this" {
  project  = var.project_id
  name     = var.service_name
  location = var.region

  # Reachable only through the internal/external HTTP(S) load balancer.
  ingress = "INGRESS_TRAFFIC_INTERNAL_LOAD_BALANCER"

  deletion_protection = false

  template {
    service_account = google_service_account.this.email

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
    }
  }

  lifecycle {
    # The image is typically rolled by CI/CD outside Terraform; uncomment to
    # let Terraform stop fighting external image updates:
    # ignore_changes = [template[0].containers[0].image]
  }
}
