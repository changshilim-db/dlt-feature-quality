# Databricks notebook source
# MAGIC %md 
# MAGIC # Ingestion from bronze to silver 
# MAGIC 
# MAGIC After ingesting raw data into our bronze layer, we can start cleaning our data and performing quality control as we move data from the bronze to silver layer. 
# MAGIC 
# MAGIC At this stage, DLT's [expectations](https://docs.databricks.com/workflows/delta-live-tables/delta-live-tables-expectations.html) can help us perform basic quality checks. DLT does this by allowing us to specify contraints on our dataset, for example stating that a column should not contain `NULL` values. 
# MAGIC 
# MAGIC Later, when moving data from bronze to silver layer, we will cover how column level checks and summary statistics on a dataset can be generated. 
# MAGIC 
# MAGIC [As best practice](https://docs.databricks.com/workflows/delta-live-tables/delta-live-tables-cookbook.html#make-expectations-portable-and-reusable), we can make our expectations portable and reusable by storing our rules externally in CSV format, and then reading in this file when we want to apply our expectations. 
# MAGIC 
# MAGIC Later, when moving data from bronze to silver layer, column level checks can be conducted

# COMMAND ----------

import dlt

# COMMAND ----------

import pyspark.sql.functions as F
from pyspark.sql.functions import pandas_udf
from pyspark.sql.types import *

# COMMAND ----------

# make expectations portable and reusable
expectations_filepath = "dbfs:/FileStore/feature_store_data_quality/instacart_data/instacart_dlt_constraints.csv"
expectations_df = spark.read.option("header", True).csv(expectations_filepath)

# source: https://docs.databricks.com/workflows/delta-live-tables/delta-live-tables-cookbook.html#make-expectations-portable-and-reusable
def get_rules(tag, expectations_df):
  """
    loads data quality rules from dataframe and applies to raw data
    :param tag: tag to match
    :param expectations_df: dataframe specifying expectations
    :return: dictionary of rules that matched the tag
  """
  rules = {}
  for row in expectations_df.filter(F.col("tag") == tag).collect():
    rules[row['name']] = row['constraint']
  return rules

# COMMAND ----------

# MAGIC %md 
# MAGIC View the expectations that we loaded from CSV

# COMMAND ----------

display(expectations_df)

# COMMAND ----------

# MAGIC %md 
# MAGIC Register any UDFs in our expectations

# COMMAND ----------

spark.udf.register("order_hour_check", lambda x: True if x >= 0 and x < 24 else False, "boolean")

# COMMAND ----------

# MAGIC %md 
# MAGIC Included expectations into our DLT pipeline

# COMMAND ----------

# read data from bronze
@dlt.view
@dlt.expect_all(get_rules("aisle_validity_check", expectations_df))
# @dlt.expect_all({"aisle_validity_check":"aisle IS NOT NULL", "aisle_id_validity_check": "aisle_id IS NOT NULL"})
def aisle_bronze():
  return spark.table("feature_store_data_quality_db.aisle_raw")

@dlt.view
@dlt.expect_all(get_rules("dept_validity_check", expectations_df))
def dept_bronze():
  return spark.table("feature_store_data_quality_db.department_raw")

@dlt.view
@dlt.expect_all(get_rules("product_validity_check", expectations_df))
def product_bronze():
  return spark.table("feature_store_data_quality_db.product_raw")

@dlt.view
@dlt.expect_all(get_rules("order_validity_check", expectations_df))
def order_bronze():
  return spark.table("feature_store_data_quality_db.order_raw")

@dlt.view
def order_product_bronze():
   return spark.table("feature_store_data_quality_db.order_product_raw")

# COMMAND ----------

# MAGIC %md 
# MAGIC Output final dataframe into a silver table

# COMMAND ----------

@dlt.table(name="orders_joined_silver")
def orders_joined_silver():
  order = dlt.read("order_bronze")
  order_product = dlt.read("order_product_bronze")
  product = dlt.read("product_bronze")
  return (order
      .join(order_product, how="inner", on="order_id") 
      .join(product, how="inner", on="product_id"))
