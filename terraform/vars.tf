variable "repo_path" {
  default     = "/Repos/Feature-Store-Data-Quality/code-repo"
  description = "Path where repo is created"
  type        = string
}

variable "dlt_target_db" {
  default     = "feature_store_data_quality_db"
  description = "Name of a database for persisting the pipeline output data"
  type        = string
}

variable "task_dependency" {
  default = {
    "00_instacart_get_data"            = "",
    "01_instacart_ingest_bronze"       = "00_instacart_get_data",
    "02_instacart_bronze_to_silver"    = "01_instacart_ingest_bronze",
    "03_feature-engineering"           = "02_instacart_bronze_to_silver",
    "04_instacart_write_feature_store" = "03_feature-engineering",
  }
  description = "Databricks Job task dependency"
}

variable "job_name" {
  default     = "feature-store-data-quality-job"
  description = "Name for the Databricks job"
  type        = string
}

variable "job_cluster_key" {
  default     = "Feature-Store-Data-Quality-Cluster"
  description = "Name for job cluster"
  type        = string
}