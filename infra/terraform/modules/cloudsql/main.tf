###############################################################################
# modules/cloudsql — Cloud SQL for PostgreSQL reachable ONLY via Private
# Service Connect (PSC), plus the consumer-side PSC endpoint inside the VPC,
# a database, a SQL user with a random password, and that password stored in
# Secret Manager.
#
# Connectivity model:
#   - The instance has ipv4_enabled = false and psc_config.psc_enabled = true,
#     so it exposes a PSC *service attachment* instead of a public/private IP.
#   - We then create a consumer PSC endpoint (internal address + forwarding
#     rule) in the caller's subnet that targets that service attachment.
#   - The backend connects to the endpoint's INTERNAL IP (output: psc_ip).
###############################################################################

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }
}

# --- Cloud SQL Postgres instance (PSC, cost-minimal) -------------------------
resource "google_sql_database_instance" "this" {
  project          = var.project_id
  name             = var.instance_name
  region           = var.region
  database_version = var.database_version

  # f1-micro is the cheapest tier but has ~0.6 GB RAM — see README caveat.
  # deletion_protection at the API level is governed by the setting below; the
  # resource-level guard is kept off so non-prod stacks can be torn down.
  deletion_protection = var.deletion_protection

  settings {
    tier              = var.tier
    availability_type = "ZONAL"
    disk_type         = "PD_HDD"
    disk_size         = var.disk_size
    disk_autoresize   = false

    ip_configuration {
      # No public IPv4 and no traditional private IP: access is PSC-only.
      ipv4_enabled = false

      psc_config {
        psc_enabled               = true
        allowed_consumer_projects = var.allowed_consumer_projects
      }
    }

    backup_configuration {
      # Minimal/disabled backups to keep cost down (toggle via var for prod).
      enabled = var.backups_enabled
    }

    # Guard against the instance being deleted out from under the stack.
    deletion_protection_enabled = var.deletion_protection
  }
}

# --- Application database ----------------------------------------------------
resource "google_sql_database" "app" {
  project   = var.project_id
  name      = var.database_name
  instance  = google_sql_database_instance.this.name
  charset   = "UTF8"
  collation = "en_US.UTF8"
}

# --- SQL user with a generated password -------------------------------------
resource "random_password" "db" {
  length  = 32
  special = true
  # Avoid characters that complicate URL-encoding of the DB connection string.
  override_special = "!#%*-_=+"
}

resource "google_sql_user" "app" {
  project  = var.project_id
  name     = var.database_user
  instance = google_sql_database_instance.this.name
  password = random_password.db.result
}

# --- Secret Manager: store the DB password (never plaintext in Cloud Run) ----
resource "google_secret_manager_secret" "db_password" {
  project   = var.project_id
  secret_id = var.db_password_secret_id

  replication {
    auto {}
  }
}

resource "google_secret_manager_secret_version" "db_password" {
  secret      = google_secret_manager_secret.db_password.id
  secret_data = random_password.db.result
}

# --- Consumer-side PSC endpoint in the caller's subnet -----------------------
# Internal IP that the forwarding rule will own.
resource "google_compute_address" "psc" {
  project      = var.project_id
  name         = "${var.instance_name}-psc-ip"
  region       = var.region
  subnetwork   = var.subnet_self_link
  address_type = "INTERNAL"
}

# PSC forwarding rule targeting the instance's service attachment. This is what
# makes the Cloud SQL instance reachable from inside the VPC.
resource "google_compute_forwarding_rule" "psc" {
  project               = var.project_id
  name                  = "${var.instance_name}-psc-fr"
  region                = var.region
  network               = var.network_self_link
  ip_address            = google_compute_address.psc.id
  load_balancing_scheme = "" # required to be empty for PSC consumer endpoints
  target                = google_sql_database_instance.this.psc_service_attachment_link
}
