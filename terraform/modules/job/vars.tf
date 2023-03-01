variable "job_name" {
  description = "Name of job"
  type        = string
}

variable "job_cluster_key" {
  description = "Name for job cluster"
  type        = string
}

variable "task_lists"{
  type = map
}

variable "task_dependency"{
  type = map
}