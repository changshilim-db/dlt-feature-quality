output "tasks_list" {
  value = merge(local.notebook_task_paths, module.dlt_pipelines)
}