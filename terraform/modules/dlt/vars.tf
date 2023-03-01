variable "dlt_name" {
  description = "Name of DLT pipeline"
  type        = string
}

variable "dlt_target_db" {
  description = "Name of a database for persisting the pipeline output data"
  type        = string
}

variable "notebook_path" {
  description = "Path where DLT notebook resides"
  type        = string
}