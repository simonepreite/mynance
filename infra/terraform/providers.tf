# Both providers default to the same project/region. google-beta is required by
# some Certificate Manager / advanced resources in the loadbalancer module.
provider "google" {
  project = var.project_id
  region  = var.region
}

provider "google-beta" {
  project = var.project_id
  region  = var.region
}
