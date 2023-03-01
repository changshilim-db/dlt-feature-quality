output "task_resource_id" {
  value = databricks_pipeline.feature_dlt.id
  description = "DLT Pipeline ID that was created"
}

output "task_resource_name" {
  value = databricks_pipeline.feature_dlt.name
  description = "DLT Pipeline name that was created"
}

output "task_type" {
  value = "dlt"
  description = "DLT Pipeline name that was created"
}