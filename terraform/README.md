# Terraform Walkthrough
For more information on Terrafrom Databricks provider, please refer to this link [here](https://registry.terraform.io/providers/databricks/databricks/latest/docs).

## Main Module
The Terraform project's structure is quite straightforward. The structure is as follow:

```terraform
terraform
 ┣ modules
 ┃ ┣ dlt
 ┃ ┃ ┣ main.tf
 ┃ ┃ ┣ outputs.tf
 ┃ ┃ ┗ vars.tf
 ┃ ┗ job
 ┃ ┃ ┣ main.tf
 ┃ ┃ ┗ vars.tf
 ┣ init.tf
 ┣ main.tf
 ┣ outputs.tf
 ┗ vars.tf
 ```
 
The [main.tf](main.tf) file is where Databricks resources are defined. The script is doing the following:
* Obtaining the list of notebooks that are found in the folder of app/notebooks
* Calling the DLT module to create DLT pipelines based on the notebooks found in app/dlt
* With these, create a Databricks Jobs that will execute these notebooks and DLT pipelines

The [vars.tf](vars.tf) file is a typical Terraform variables file. Most variables are quite self-explanatory. A special case will be the variable *"task_dependency"*, where each key represents a Databricks Job task and the value represents the dependent task. The first task will have no dependency, hence the value will be defined as an empty string.

*00_instacart_get_data is the first task, hence it has no dependency. 01_instacart_ingest_bronze is dependent on 00_instacart_get_data*.

   ```terraform
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
   ```

## Modules
There are 2 modules used in this project: dlt and job.

### DLT Module
The dlt module is where a DLT resource is defined. The output of this module consists of:
* task_resource_id: DLT pipeline ID created
* task_resource_name: Name of DLT pipeline created
* task_type: Type of task created (in this case DLT)

These output will be used by the main module for creating a Databricks Job

### Job Module
The job module is where a Databricks Job resource is defined. Based on the variable *task_lists*, this module attempts to dynamically create tasks of various kind (for now, either DLT or notebook). Task dependency will be determined by the variable *"task_dependency"*.
