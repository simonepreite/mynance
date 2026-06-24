output "lb_ip" {
  description = "Reserved global static external IP of the load balancer. Point app/api DNS A records here."
  value       = google_compute_global_address.lb.address
}

output "https_enabled" {
  description = "Whether the HTTPS listener was provisioned."
  value       = var.enable_https
}

# DNS authorization record the operator must create for the managed cert to
# validate. Null when HTTPS is disabled.
output "dns_authorization_record" {
  description = "CNAME record (name/type/data) required by Certificate Manager DNS authorization."
  value = var.enable_https ? {
    name = google_certificate_manager_dns_authorization.this[0].dns_resource_record[0].name
    type = google_certificate_manager_dns_authorization.this[0].dns_resource_record[0].type
    data = google_certificate_manager_dns_authorization.this[0].dns_resource_record[0].data
  } : null
}
