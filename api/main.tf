terraform {
  required_providers {
    google = ">= 4.1"
  }
}

provider "google" {
  project = var.gcp_project_id
}

resource "google_project_service" "gcp_services" {
  for_each = toset(var.gcp_service_list)
  project  = var.gcp_project_id
  service  = each.key
}

resource "google_project_iam_binding" "gcp_iam_bindings" {
  project = var.gcp_project_id

  role = "roles/iam.serviceAccountUser"
  members = [
    "serviceAccount:${var.gcp_project_num}@cloudbuild.gserviceaccount.com",
  ]
}

# resource "google_cloud_run_service_iam_binding" "gcr_iam_bindings" {
#   location = google_cloud_run_service.cloud_run.location
#   project  = google_cloud_run_service.cloud_run.project
#   service  = google_cloud_run_service.cloud_run.name

#   role = "roles/editor"
#   members = [
#     "serviceAccount:${var.gcp_project_num}@cloudbuild.gserviceaccount.com",
#   ]

# }

resource "google_sourcerepo_repository" "gcp_repo" {
  name = var.gcp_repo_name
}

resource "google_cloudbuild_trigger" "cloud_build_trigger" {
  trigger_template {
    branch_name = var.gcp_repo_branch
    repo_name   = var.gcp_repo_name
  }

  substitutions = {
    _DB_URI       = var.cdb_uri
    _GCR_REGION   = var.gcr_region
    _SERVICE_NAME = "rc4laundry-api"
  }

  filename = "api/cloudbuild.yaml"
}

# resource "google_cloud_run_service" "cloud_run" {
#   name     = "rc4laundry-api-cloud-run"
#   location = var.gcr_region
# }
