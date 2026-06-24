output "network_self_link" {
  description = "Self link of the created VPC network."
  value       = google_compute_network.this.self_link
}

output "network_id" {
  description = "ID of the created VPC network."
  value       = google_compute_network.this.id
}

output "subnet_self_link" {
  description = "Self link of the created subnet."
  value       = google_compute_subnetwork.this.self_link
}

output "subnet_id" {
  description = "ID of the created subnet."
  value       = google_compute_subnetwork.this.id
}
