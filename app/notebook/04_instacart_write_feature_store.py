# Databricks notebook source
# MAGIC %md 
# MAGIC # Write features to Feature Store 
# MAGIC As the final step in our workflow, we write our table containing our features into a Feature Store table

# COMMAND ----------

from databricks.feature_store import FeatureStoreClient

# COMMAND ----------

# MAGIC %sql 
# MAGIC CREATE DATABASE IF NOT EXISTS instacart_features

# COMMAND ----------

user_features = spark.table("feature_store_data_quality_db.user_features")

# COMMAND ----------

fs = FeatureStoreClient()
fs.create_table(
  name="instacart_features.user_features",
  df=user_features,
  primary_keys="user_id",
  schema=user_features.schema,
  description="user level features for Instacart Market Basket Analysis"
)
