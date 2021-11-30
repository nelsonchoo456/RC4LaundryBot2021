terraform {
  required_providers {
    google = ">= 4.1"
  }
}

provider "google" {
  project = var.gcp_project_id
}

# Enable the all APIs needed.
resource "google_project_service" "gcp_services" {
  for_each = toset(var.gcp_service_list)
  project  = var.gcp_project_id
  service  = each.key
}

# TODO Check if this block is really needed.
resource "google_project_iam_binding" "gcp_iam_bindings" {
  project = var.gcp_project_id

  role = "roles/iam.serviceAccountUser"
  members = [
    local.cloud_build_service_account,
  ]
}

# Provision Cloud Source Repository.
resource "google_sourcerepo_repository" "gcp_repo" {
  name = var.gcp_repo_name
}

# Create a Cloud Build trigger for each push to the `prod` branch
# of the GCP Source Repo.
resource "google_cloudbuild_trigger" "cloud_build_trigger" {
  trigger_template {
    branch_name = var.gcp_repo_branch
    repo_name   = var.gcp_repo_name
  }

  # These variables will be passed into the build steps.
  substitutions = {
    _DB_URI       = var.cdb_uri
    _LOCATION     = var.registry_location
    _GCR_REGION   = var.gcr_region
    _SERVICE_NAME = var.gcp_service_name
  }

  filename = "api/cloudbuild.yaml"
}

# Provision Container Registry.
resource "google_container_registry" "registry" {
  project  = var.gcp_project_id
  location = "asia"
}

# Provision Cloud Run.
resource "google_cloud_run_service" "cloud_run" {
  name     = var.gcp_service_name
  location = var.gcr_region

  metadata {
    annotations = {
      "client.knative.dev/user-image" = local.image_name
    }
  }

  template {
    spec {
      containers {
        # This points to the image built and pushed to the
        # Container Registry.
        image = local.image_name
      }
    }
  }

  traffic {
    percent         = 100
    latest_revision = true
  }
}

# Allows Cloud Build to deploy to cloud run after each
# successful build.
resource "google_cloud_run_service_iam_binding" "gcr_iam_bindings" {
  location = google_cloud_run_service.cloud_run.location
  project  = google_cloud_run_service.cloud_run.project
  service  = google_cloud_run_service.cloud_run.name

  role = "roles/run.admin"
  members = [
    local.cloud_build_service_account,
  ]
}

# Allows anyone to call the API.
resource "google_cloud_run_service_iam_member" "allUsers" {
  service  = google_cloud_run_service.cloud_run.name
  location = google_cloud_run_service.cloud_run.location
  role     = "roles/run.invoker"
  member   = "allUsers"
}

locals {
  image_name                  = "${var.registry_location}.gcr.io/${var.gcp_project_id}/${var.gcp_service_name}:latest"
  cloud_build_service_account = "serviceAccount:${var.gcp_project_num}@cloudbuild.gserviceaccount.com"
}
