terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

resource "databricks_pipeline" "feature_dlt" {
  name        = var.dlt_name
  target      = var.dlt_target_db
  development = true

  cluster {
    label       = "default"
    num_workers = 3
  }

  library {
    notebook {
      path = var.notebook_path
    }
  }
  continuous = false
}