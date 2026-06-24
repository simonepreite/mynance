###############################################################################
# Root wiring for the mynance stack.
###############################################################################

locals {
  #############################################################################
  # CREATE-OR-REFERENCE NETWORK
  #
  # If no existing network self_link was provided, we CREATE a VPC + subnet via
  # modules/network. Otherwise we REFERENCE the passed-in self_links (the
  # Shared VPC / host-project case). `create_network` drives the module's
  # count, and the `*_self_link` locals below resolve to EITHER the module
  # output (when created) OR the input variable (when referenced) so that every
  # downstream consumer is agnostic to which path was taken.
  #############################################################################
  create_network = var.network_self_link == ""

  network_self_link = local.create_network ? module.network[0].network_self_link : var.network_self_link
  subnet_self_link  = local.create_network ? module.network[0].subnet_self_link : var.subnet_self_link

  #############################################################################
  # HTTPS-OR-HTTP LOAD BALANCER
  #
  # When a domain is configured we provision a managed certificate + HTTPS
  # listener; when it is empty the LB comes up HTTP-only so the static IP and
  # routing can be smoke-tested before DNS/cert exist.
  #############################################################################
  enable_https = var.domain != ""

  #############################################################################
  # OPTIONAL GCS FUSE PERSISTENCE (DEFAULT OFF, per service)
  #
  # The app is stateless, so buckets default to disabled. When a bucket name is
  # not explicitly given, derive a parametric one from project + service.
  # These locals are only consumed when the corresponding *_bucket_enabled
  # toggle is true (the module ignores the name otherwise).
  #############################################################################
  backend_bucket_name  = var.backend_bucket_name != "" ? var.backend_bucket_name : "${var.project_id}-${var.name_prefix}-backend"
  frontend_bucket_name = var.frontend_bucket_name != "" ? var.frontend_bucket_name : "${var.project_id}-${var.name_prefix}-frontend"

  # Required Google APIs. Enabled when var.enable_apis is true.
  required_apis = var.enable_apis ? toset([
    "run.googleapis.com",
    "sqladmin.googleapis.com",
    "compute.googleapis.com",
    "certificatemanager.googleapis.com",
    "secretmanager.googleapis.com",
    "storage.googleapis.com", # only used when an optional GCS bucket is enabled
    "servicenetworking.googleapis.com",
    "dns.googleapis.com", # optional but harmless; used if managing DNS in-project
    "iam.googleapis.com",
    "serviceusage.googleapis.com",
  ]) : toset([])
}

# --- Enable required APIs ----------------------------------------------------
resource "google_project_service" "apis" {
  for_each           = local.required_apis
  project            = var.project_id
  service            = each.value
  disable_on_destroy = false
}

# --- Network (created only when no existing self_link is passed) -------------
module "network" {
  source = "./modules/network"
  count  = local.create_network ? 1 : 0

  project_id   = var.project_id
  region       = var.region
  network_name = var.network_name
  subnet_name  = var.subnet_name
  subnet_cidr  = var.subnet_cidr

  depends_on = [google_project_service.apis]
}

# --- Cloud SQL (PSC) + secret ------------------------------------------------
module "cloudsql" {
  source = "./modules/cloudsql"

  project_id                = var.project_id
  region                    = var.region
  instance_name             = var.db_instance_name
  database_version          = var.db_version
  tier                      = var.db_tier
  disk_size                 = var.db_disk_size
  database_name             = var.db_name
  database_user             = var.db_user
  db_password_secret_id     = var.db_password_secret_id
  deletion_protection       = var.db_deletion_protection
  backups_enabled           = var.db_backups_enabled
  allowed_consumer_projects = [var.project_id]

  # Resolved by the create-or-reference locals above.
  network_self_link = local.network_self_link
  subnet_self_link  = local.subnet_self_link

  depends_on = [google_project_service.apis]
}

# --- IAM: backend SA can read the DB password secret (+ cloudsql.client) -----
resource "google_secret_manager_secret_iam_member" "backend_db_password" {
  project   = var.project_id
  secret_id = module.cloudsql.db_password_secret_id
  role      = "roles/secretmanager.secretAccessor"
  member    = "serviceAccount:${module.backend.service_account_email}"
}

# Allows the backend SA to use the Cloud SQL Auth Proxy / connector flows if
# the app ever switches off direct PSC IP connectivity.
resource "google_project_iam_member" "backend_cloudsql_client" {
  project = var.project_id
  role    = "roles/cloudsql.client"
  member  = "serviceAccount:${module.backend.service_account_email}"
}

# --- Backend Cloud Run service ----------------------------------------------
# Plain env mirrors the app's settings (backend/app/core/config.py). The DB
# password is injected from Secret Manager, never as plaintext.
module "backend" {
  source = "./modules/cloudrun"

  project_id         = var.project_id
  region             = var.region
  service_name       = "${var.name_prefix}-backend"
  service_account_id = "${var.name_prefix}-be-sa"
  image              = var.backend_image
  container_port     = var.backend_container_port
  cpu                = var.cloudrun_cpu
  memory             = var.cloudrun_memory
  min_instances      = var.cloudrun_min_instances
  max_instances      = var.cloudrun_max_instances

  network_self_link = local.network_self_link
  subnet_self_link  = local.subnet_self_link

  env = merge({
    PROJECT_NAME    = var.project_name
    ENVIRONMENT     = var.environment
    POSTGRES_SERVER = module.cloudsql.psc_ip
    POSTGRES_PORT   = tostring(var.db_port)
    POSTGRES_DB     = var.db_name
    POSTGRES_USER   = var.db_user
    # CORS is wired to the FE subdomain; when no domain is set this points at
    # the (placeholder) app.<empty> host — adjust once the domain is known.
    BACKEND_CORS_ORIGINS = local.enable_https ? "https://app.${var.domain}" : "http://app.${var.domain}"
    FRONTEND_HOST        = local.enable_https ? "https://app.${var.domain}" : "http://app.${var.domain}"
  }, var.extra_backend_env)

  secret_env = {
    POSTGRES_PASSWORD = {
      secret  = module.cloudsql.db_password_secret_name
      version = "latest"
    }
  }

  # Optional GCS FUSE persistence (default OFF; nothing created when disabled).
  bucket_enabled       = var.backend_bucket_enabled
  bucket_name          = local.backend_bucket_name
  bucket_mount_path    = var.backend_bucket_mount_path
  bucket_force_destroy = var.backend_bucket_force_destroy
  bucket_versioning    = var.backend_bucket_versioning

  depends_on = [google_project_service.apis]
}

# --- Frontend Cloud Run service ---------------------------------------------
# NOTE: Vite's VITE_API_URL is a BUILD-TIME variable baked into the static
# bundle (see frontend/src/main.tsx -> OpenAPI.BASE = import.meta.env.VITE_API_URL).
# The runtime env below is exposed for completeness only; the image MUST be
# built with VITE_API_URL=https://api.<domain> for the SPA to call the API.
module "frontend" {
  source = "./modules/cloudrun"

  project_id         = var.project_id
  region             = var.region
  service_name       = "${var.name_prefix}-frontend"
  service_account_id = "${var.name_prefix}-fe-sa"
  image              = var.frontend_image
  container_port     = var.frontend_container_port
  cpu                = var.cloudrun_cpu
  memory             = var.cloudrun_memory
  min_instances      = var.cloudrun_min_instances
  max_instances      = var.cloudrun_max_instances

  network_self_link = local.network_self_link
  subnet_self_link  = local.subnet_self_link

  env = merge({
    VITE_API_URL = local.enable_https ? "https://api.${var.domain}" : "http://api.${var.domain}"
  }, var.extra_frontend_env)

  # Optional GCS FUSE persistence (default OFF; nothing created when disabled).
  bucket_enabled       = var.frontend_bucket_enabled
  bucket_name          = local.frontend_bucket_name
  bucket_mount_path    = var.frontend_bucket_mount_path
  bucket_force_destroy = var.frontend_bucket_force_destroy
  bucket_versioning    = var.frontend_bucket_versioning

  depends_on = [google_project_service.apis]
}

# --- Load balancer (single global external HTTPS/HTTP LB) --------------------
module "loadbalancer" {
  source = "./modules/loadbalancer"

  project_id            = var.project_id
  region                = var.region
  name_prefix           = var.name_prefix
  domain                = var.domain
  enable_https          = local.enable_https
  frontend_service_name = module.frontend.service_name
  backend_service_name  = module.backend.service_name

  depends_on = [google_project_service.apis]
}
