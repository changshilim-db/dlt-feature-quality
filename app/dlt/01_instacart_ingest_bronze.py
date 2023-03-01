# Databricks notebook source
# MAGIC %md 
# MAGIC #Overview
# MAGIC ## Why data quality matters 
# MAGIC Data that comes from upstream sources into feature tables can be incomplete and messy. This is particularly the case when the data sources output information in real-time and at high volume. For instance, clickstream data providers might provide a best effort sample of clicks in real-time, and then update the dataset with late-arriving data only a day later. Since machine learning models are made or broken based on the quality of the data they were trained with, Data Engineers and Data Scientists need suitable tools to check the health of their input data pipelines. 
# MAGIC 
# MAGIC Furthermore, data quality issues, when not fixed early in the ETL pipeline, can have escalating consequences for downstream models. For example, inappropriate `day-of-week` values for certain rows may not seem like a make-or-break issues during data ingestion. However, if that corrupt data is used to train many models that are subsequently pushed to production, the downstream effects on business decisions make be severe. 

# COMMAND ----------

# MAGIC %md 
# MAGIC ## What data quality issues do we often encounter during feature engineering?  
# MAGIC 
# MAGIC Our **upstream data sources** can broken eg. an IOT device breaks down and stops sending data, leading to null values. In other cases, if data formats are not standardised between systems, we have the same data represented in different ways, for example `day-of-week` being expressed as `Monday` and `1`.  
# MAGIC 
# MAGIC These errors can lead to data inputs that do not make sense or that have to be reconciled. Usually, these errors, if known upfront, can be mitigated by conducting **row-level assertions** on the dataset, for example specifying that all `day-of-week` values have to be between `0` and `6`. When these errors are detected, we have several options. We can drop the bad rows, quarantine the data into a separate location for further investigation, or fail the pipeline. 
# MAGIC 
# MAGIC Our system may experience **data drift**. In this case, nothing is broken per se. But external factors, for example summer moves to winter, cause the incoming feature distributions to shift. If our model can no longer generalise to this new data, performance suffers. 
# MAGIC 
# MAGIC In these cases, instead of row-level checks, we need to monitor the summary statistics or the distributions of our columns of interest through time. If these statistics or distributions change significantly, then drift has occured. Importantly, during drift monitoring, it's common to have false positives. More often than not, even when the data has drifted, a model may not underperform. Additionally, we might even avoid drift altogether through frequently refreshing our model. Hence, data drift is harder to pinpoint definitively. From a practical point-of-view, this means we may not want our pipeline to fail even if we get a drift alert from our system.

# COMMAND ----------

# MAGIC %md 
# MAGIC 
# MAGIC ## Use case: 
# MAGIC We show an example of what a data quality setup for feature engineering might look like. For our dataset, we make use of the Instacart Market Basket Analysis dataset from Kaggle. From this dataset, we might create input features to our model such as: 
# MAGIC 

# MAGIC - Percentage of items in a user’s basket that are reorders 
# MAGIC - Average order size per user
# MAGIC - Average days between orders for each user

# COMMAND ----------

# MAGIC %md 
# MAGIC ### Pipeline step 1: ingest tables into bronze layer 

# MAGIC We define a simple DLT pipeline that reads in our raw data and saves it into Delta tables

# COMMAND ----------

import dlt
from pyspark.sql.types import *
import pyspark.sql.functions as F

# COMMAND ----------

aisle_filepath = "dbfs:/FileStore/feature_store_data_quality/instacart_data/aisles.csv"
dept_filepath = "dbfs:/FileStore/feature_store_data_quality/instacart_data/departments.csv"
order_product_prior_filepath = "dbfs:/FileStore/feature_store_data_quality/instacart_data/order_products__prior.csv"
order_product_train_filepath = "dbfs:/FileStore/feature_store_data_quality/instacart_data/order_products__train.csv"
order_filepath = "dbfs:/FileStore/feature_store_data_quality/instacart_data/orders.csv"
product_filepath = "dbfs:/FileStore/feature_store_data_quality/instacart_data/products.csv"

# COMMAND ----------

@dlt.table(
  name="aisle_raw",
  comment="The raw aisles dataset, ingested as csv",
)
def aisle_raw():          
  return (
    spark.read.option("header", True).csv(aisle_filepath)
  )
  
@dlt.table(
  name="department_raw",
  comment="The raw department dataset, ingested as csv"
)
def department_raw():          
  return (
    spark.read.option("header", True).csv(dept_filepath)
  )
  
@dlt.table(
  name="product_raw",
  comment="The product departments dataset, ingested as csv"
)
def product_raw():          
  return (
    spark.read.option("header", True).csv(product_filepath)
  )
  
@dlt.table(
  name="order_raw",
  comment="The raw order dataset, ingested as csv"
)
def order_raw():
  order = spark.read.option("header", True).csv(order_filepath)
  order = order.withColumn("order_number", F.col("order_number").cast(IntegerType())) \
               .withColumn("order_dow", F.col("order_dow").cast(IntegerType())) \
               .withColumn("order_hour_of_day", F.col("order_hour_of_day").cast(IntegerType())) \
               .withColumn("days_since_prior_order", F.col("days_since_prior_order").cast(IntegerType()))
  return order
  
@dlt.table(
  name="order_product_raw",
  comment="The raw order_product dataset, ingested as csv",
)
def order_product_raw():          
  prior = spark.read.option("header", True).csv(order_product_prior_filepath)
  train = spark.read.option("header", True).csv(order_product_train_filepath)
  all_order_product = prior.union(train)
  all_order_product = all_order_product.withColumn("reordered", F.col("reordered").cast(IntegerType())) \
                                       .withColumn("add_to_cart_order", F.col("add_to_cart_order").cast(IntegerType()))
  return all_order_product
