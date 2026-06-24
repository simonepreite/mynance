###############################################################################
# modules/loadbalancer — single GLOBAL external HTTP(S) load balancer fronting
# the two Cloud Run services, with HOST-based routing across two subdomains:
#
#     app.<domain>  -> frontend backend service
#     api.<domain>  -> backend  backend service
#
# A global static external IP is ALWAYS reserved and exported, so DNS can be
# pointed at it before a domain/cert exists.
#
# HTTPS-vs-HTTP conditional (var.enable_https):
#   - enable_https = true  : Certificate Manager managed cert (DNS-authorized)
#       + certificate map + HTTPS target proxy + :443 forwarding rule.
#   - enable_https = false : ONLY an HTTP target proxy + :80 forwarding rule so
#       the LB stands up for smoke testing before the domain is known.
# All HTTPS-only resources are gated with `count = var.enable_https ? 1 : 0`.
###############################################################################

terraform {
  required_version = ">= 1.5"
  required_providers {
    google = {
      source  = "hashicorp/google"
      version = "~> 6.0"
    }
    google-beta = {
      source  = "hashicorp/google-beta"
      version = "~> 6.0"
    }
  }
}

locals {
  app_host = "app.${var.domain}"
  api_host = "api.${var.domain}"
}

# --- Global static external IP (always reserved) -----------------------------
resource "google_compute_global_address" "lb" {
  project = var.project_id
  name    = "${var.name_prefix}-ip"
}

# --- Serverless NEGs (one per Cloud Run service) -----------------------------
resource "google_compute_region_network_endpoint_group" "frontend" {
  project               = var.project_id
  name                  = "${var.name_prefix}-fe-neg"
  region                = var.region
  network_endpoint_type = "SERVERLESS"
  cloud_run {
    service = var.frontend_service_name
  }
}

resource "google_compute_region_network_endpoint_group" "backend" {
  project               = var.project_id
  name                  = "${var.name_prefix}-be-neg"
  region                = var.region
  network_endpoint_type = "SERVERLESS"
  cloud_run {
    service = var.backend_service_name
  }
}

# --- Backend services --------------------------------------------------------
resource "google_compute_backend_service" "frontend" {
  project               = var.project_id
  name                  = "${var.name_prefix}-fe-bes"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  protocol              = "HTTPS"

  backend {
    group = google_compute_region_network_endpoint_group.frontend.id
  }
}

resource "google_compute_backend_service" "backend" {
  project               = var.project_id
  name                  = "${var.name_prefix}-be-bes"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  protocol              = "HTTPS"

  backend {
    group = google_compute_region_network_endpoint_group.backend.id
  }
}

# --- URL map: host-based routing --------------------------------------------
# Default traffic (and the HTTP listener) goes to the frontend service.
resource "google_compute_url_map" "this" {
  project         = var.project_id
  name            = "${var.name_prefix}-urlmap"
  default_service = google_compute_backend_service.frontend.id

  # Host rules are only meaningful once a domain exists; harmless otherwise.
  host_rule {
    hosts        = [local.app_host]
    path_matcher = "fe"
  }

  host_rule {
    hosts        = [local.api_host]
    path_matcher = "be"
  }

  path_matcher {
    name            = "fe"
    default_service = google_compute_backend_service.frontend.id
  }

  path_matcher {
    name            = "be"
    default_service = google_compute_backend_service.backend.id
  }
}

###############################################################################
# HTTPS path (enable_https = true) — Certificate Manager, not the legacy
# google_compute_managed_ssl_certificate.
###############################################################################

# DNS authorization proves domain ownership for the managed cert. The DNS
# record it asks for is exported so the operator can create it.
resource "google_certificate_manager_dns_authorization" "this" {
  count       = var.enable_https ? 1 : 0
  project     = var.project_id
  name        = "${var.name_prefix}-dnsauth"
  domain      = var.domain
  description = "DNS authorization for ${var.domain} (mynance LB)"
}

# Managed certificate covering both subdomains via wildcard + apex authz.
resource "google_certificate_manager_certificate" "this" {
  count   = var.enable_https ? 1 : 0
  project = var.project_id
  name    = "${var.name_prefix}-cert"

  managed {
    domains = [local.app_host, local.api_host]
    dns_authorizations = [
      google_certificate_manager_dns_authorization.this[0].id,
    ]
  }
}

resource "google_certificate_manager_certificate_map" "this" {
  count   = var.enable_https ? 1 : 0
  project = var.project_id
  name    = "${var.name_prefix}-certmap"
}

resource "google_certificate_manager_certificate_map_entry" "app" {
  count        = var.enable_https ? 1 : 0
  project      = var.project_id
  name         = "${var.name_prefix}-certmap-app"
  map          = google_certificate_manager_certificate_map.this[0].name
  certificates = [google_certificate_manager_certificate.this[0].id]
  hostname     = local.app_host
}

resource "google_certificate_manager_certificate_map_entry" "api" {
  count        = var.enable_https ? 1 : 0
  project      = var.project_id
  name         = "${var.name_prefix}-certmap-api"
  map          = google_certificate_manager_certificate_map.this[0].name
  certificates = [google_certificate_manager_certificate.this[0].id]
  hostname     = local.api_host
}

# HTTPS target proxy bound to the certificate map.
resource "google_compute_target_https_proxy" "this" {
  count           = var.enable_https ? 1 : 0
  project         = var.project_id
  name            = "${var.name_prefix}-https-proxy"
  url_map         = google_compute_url_map.this.id
  certificate_map = "//certificatemanager.googleapis.com/${google_certificate_manager_certificate_map.this[0].id}"
}

resource "google_compute_global_forwarding_rule" "https" {
  count                 = var.enable_https ? 1 : 0
  project               = var.project_id
  name                  = "${var.name_prefix}-https-fr"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  ip_address            = google_compute_global_address.lb.id
  port_range            = "443"
  target                = google_compute_target_https_proxy.this[0].id
}

###############################################################################
# HTTP path
#  - enable_https = false : the only listener (so the LB exists for smoke tests)
#  - enable_https = true  : redirect :80 -> :443
###############################################################################

# Redirect URL map used only when HTTPS is enabled.
resource "google_compute_url_map" "https_redirect" {
  count   = var.enable_https ? 1 : 0
  project = var.project_id
  name    = "${var.name_prefix}-http-redirect"

  default_url_redirect {
    https_redirect         = true
    redirect_response_code = "MOVED_PERMANENTLY_DEFAULT"
    strip_query            = false
  }
}

resource "google_compute_target_http_proxy" "this" {
  project = var.project_id
  name    = "${var.name_prefix}-http-proxy"
  # When HTTPS is on, serve the redirect map; otherwise serve the real URL map.
  url_map = var.enable_https ? google_compute_url_map.https_redirect[0].id : google_compute_url_map.this.id
}

resource "google_compute_global_forwarding_rule" "http" {
  project               = var.project_id
  name                  = "${var.name_prefix}-http-fr"
  load_balancing_scheme = "EXTERNAL_MANAGED"
  ip_address            = google_compute_global_address.lb.id
  port_range            = "80"
  target                = google_compute_target_http_proxy.this.id
}
