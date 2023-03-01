terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

locals {
  notebook_task_paths = tomap({
    for notebook_file in fileset("../app/notebook", "*.py") :
    notebook_file => {
      "task_resource_id"   = "${var.repo_path}/app/notebook/${element(split(".", notebook_file),0)}",
      "task_resource_name" = element(split(".", notebook_file), 0),
      "task_type"          = "notebook"
    }
  })
}

provider "databricks" {
  alias = "my-databricks-workspace"
}

module "dlt_pipelines" {
  source = "./modules/dlt"
  for_each = fileset("../app/dlt", "*.py")
  dlt_name      = element(split(".", each.value), 0)
  dlt_target_db = var.dlt_target_db
  notebook_path = "${var.repo_path}/app/dlt/${element(split(".", each.value),0)}"
}

module "workflow_job" {
  source   = "./modules/job"
  job_name = var.job_name
  job_cluster_key = var.job_cluster_key
  task_dependency   = var.task_dependency
  task_lists = merge(local.notebook_task_paths, module.dlt_pipelines)
}