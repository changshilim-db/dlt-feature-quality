# Databricks notebook source
# MAGIC %md
# MAGIC ## Download sample data

# COMMAND ----------

# MAGIC %fs mkdirs /FileStore/feature_store_data_quality/instacart_data

# COMMAND ----------

# MAGIC %sh 
# MAGIC wget -O /dbfs/FileStore/feature_store_data_quality/instacart_data/aisles.csv https://raw.githubusercontent.com/jeannefukumaru/instacart-data/main/aisles.csv
# MAGIC wget -O /dbfs/FileStore/feature_store_data_quality/instacart_data/products.csv https://raw.githubusercontent.com/jeannefukumaru/instacart-data/main/products.csv
# MAGIC wget -O /dbfs/FileStore/feature_store_data_quality/instacart_data/departments.csv https://raw.githubusercontent.com/jeannefukumaru/instacart-data/main/departments.csv
# MAGIC wget -O /dbfs/FileStore/feature_store_data_quality/instacart_data/order_products__prior.csv https://raw.githubusercontent.com/jeannefukumaru/instacart-data/main/order_products__prior.csv
# MAGIC wget -O /dbfs/FileStore/feature_store_data_quality/instacart_data/order_products__train.csv https://raw.githubusercontent.com/jeannefukumaru/instacart-data/main/order_products__train.csv
# MAGIC wget -O /dbfs/FileStore/feature_store_data_quality/instacart_data/orders.csv https://raw.githubusercontent.com/jeannefukumaru/instacart-data/main/orders.csv
# MAGIC wget -O /dbfs/FileStore/feature_store_data_quality/instacart_data/instacart_dlt_constraints.csv https://raw.githubusercontent.com/jeannefukumaru/instacart-data/main/instacart_dlt_constraints.csv

# COMMAND ----------

# MAGIC %fs ls /FileStore/feature_store_data_quality/instacart_data

# COMMAND ----------

# MAGIC %md
# MAGIC 
# MAGIC ## Create Database for DLT outputs

# COMMAND ----------

# MAGIC %sql
# MAGIC CREATE DATABASE IF NOT EXISTS feature_store_data_quality_db

# COMMAND ----------


