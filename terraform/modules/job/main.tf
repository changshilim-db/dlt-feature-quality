terraform {
  required_providers {
    databricks = {
      source = "databricks/databricks"
    }
  }
}

data "databricks_node_type" "smallest" {
  local_disk = true
  min_memory_gb = 8
}

data "databricks_spark_version" "latest_lts" {
  long_term_support = true
  ml = true
}

resource "databricks_job" "sample_databricks_job" {
  name = var.job_name

  dynamic "task" {
    for_each = var.task_lists

    content {
        task_key = task.value.task_resource_name
        
        dynamic "pipeline_task" {
          for_each = task.value.task_type == "dlt" ? [1]: []
          content{
            pipeline_id = task.value.task_resource_id
          }
        }

        dynamic "notebook_task"{
          for_each = task.value.task_type == "notebook" ? [1]: []
          content{
            notebook_path = task.value.task_resource_id
          }
        }

        dynamic "depends_on" {
          for_each = var.task_dependency[task.value.task_resource_name] == "" ? [] : [var.task_dependency[task.value.task_resource_name]]
          content{
            task_key = var.task_dependency[task.value.task_resource_name]
          }
        }

        job_cluster_key = task.value.task_type == "notebook" ?  var.job_cluster_key : null
    }
  }

  job_cluster {
    job_cluster_key = var.job_cluster_key
    new_cluster {
      num_workers   = 2
      spark_version = data.databricks_spark_version.latest_lts.id
      node_type_id  = data.databricks_node_type.smallest.id
    }
  }
}