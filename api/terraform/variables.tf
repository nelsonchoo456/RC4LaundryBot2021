# These are to be manually passed in, or defined in a separate
# `terraform.tfvars` file.

variable "gcp_project_id" {
  description = "GCP Project ID"
  type        = string
}

variable "gcp_project_num" {
  description = "GCP Project number"
  type        = string
}

variable "cdb_uri" {
  description = "URI of the Cockroach DB cluster used for the api."
  type        = string
  sensitive   = true
}

# These variables already have defaults.

variable "gcp_service_list" {
  description = "A list of APIs to enable for this project."
  type        = list(string)
  default = [
    "cloudbuild.googleapis.com",
    "run.googleapis.com",
    "sourcerepo.googleapis.com",
    "serviceusage.googleapis.com",
    "containerregistry.googleapis.com"
  ]
}

variable "gcr_region" {
  description = "Selected region for Cloud Run service."
  type        = string
  default     = "asia-east1"
}

variable "registry_location" {
  description = "Selected location for Cloud Registry."
  type        = string
  default     = "asia"
}

variable "gcp_repo_name" {
  description = "Repository name for GCP source repo."
  type        = string
  default     = "rc4laundry/api"
}

variable "gcp_repo_branch" {
  description = "Branch used for triggering Cloud Builds."
  type        = string
  default     = "prod"
}

variable "gcp_service_name" {
  description = "Name of the Cloud Run service."
  type        = string
  default     = "rc4laundry-api"
}
