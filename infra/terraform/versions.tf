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
    random = {
      source  = "hashicorp/random"
      version = "~> 3.0"
    }
  }

  # Remote state in GCS. The bucket is created by ../bootstrap and the values
  # below are supplied at init time, e.g.:
  #   terraform init \
  #     -backend-config="bucket=<state_bucket_name>" \
  #     -backend-config="prefix=mynance/root"
  backend "gcs" {}
}
