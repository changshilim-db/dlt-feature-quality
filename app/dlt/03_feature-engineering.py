# Databricks notebook source
# MAGIC %md 
# MAGIC # Feature Engineering
# MAGIC 
# MAGIC Now our data is cleaned and residing in our silver table. 
# MAGIC 
# MAGIC Using this data, we can start to define features. These features capture user behaviour and can form inputs into a downstream model to predict reorders. 
# MAGIC 
# MAGIC Several helpful practices we can use: 
# MAGIC - to make unit testing easy, feature engineering functions should expect a dataframe as input and a dataframe as output
# MAGIC - our feature engineering logic should be self-contained and modularised from our function that creates 
# MAGIC - this also helps us define unit tests for our feature engineering logic later. 

# COMMAND ----------

import dlt
import pyspark.sql.functions as F

# COMMAND ----------

@dlt.view()
def input_table():
  df = spark.table("feature_store_data_quality_db.orders_joined_silver")
  df_filtered = df.filter((F.col("user_id")=="100013") | (F.col("user_id")=="10000") | (F.col("user_id")=="100001"))
  return df_filtered

# COMMAND ----------

# create a function for easy testing later 
@dlt.view()
def pct_reorders_per_user():
  """
  function to calculate what percentage of items bought by a user are reorders. 
  :param df: input dataframe containing user_id and reordered items bought
  :return: DataFrame with column containing proportion of reordered items in an order
  """
  df = dlt.read("input_table").select("user_id", "reordered")
  
  def reorder_pandas(df):
    df = df.groupby(["user_id"]).apply(lambda x: x.reordered.sum() / x.shape[0] * 100).reset_index()
    df.columns = ["user_id", "pct_reorders"]
    return df
  
  pct_reordered_df = df.groupby(["user_id"]).applyInPandas(reorder_pandas, schema="user_id string, pct_reorders double")
  return pct_reordered_df

# COMMAND ----------

# average number of days between orders for a user
@dlt.view()
def avg_days_btw_orders_per_user():
  """
  calculate average number of days between orders for a particular user 
  :param df: input dataframe containing user_id, order_number and days_since_prior_order
  :return: DataFrame with column containing average number of days between orders
  """
  df = dlt.read("input_table").select("user_id", "order_number", "days_since_prior_order")
  
  def days_btw_orders_pandas(df):
    df = df.groupby(["user_id", "order_number"]).first().reset_index().fillna(0)
    df = df.groupby("user_id").apply(lambda x: x.days_since_prior_order.mean()).reset_index()
    df.columns = ["user_id", "avg_days_btw_orders"]
    return df
  
  df = df.groupby("user_id").applyInPandas(days_btw_orders_pandas, schema = "user_id string, avg_days_btw_orders double")
  return df

# COMMAND ----------

@dlt.view()
def avg_order_size_per_user():
  """
  calculate average order size for a particular user 
  :param df: input dataframe 
  :return: DataFrame with column containing average number of days between orders
  """
  df = dlt.read("input_table")
  
  def avg_order_size_pandas(df):
    order_size = df.groupby(["user_id", "order_number"]).apply(lambda x: x.order_number.count()).reset_index()
    order_size.columns = ["user_id", "order_number", "order_size"]
    avg = order_size.groupby("user_id").mean().reset_index().drop("order_number", axis=1).rename(columns={"order_size": "avg_order_size"})
    return avg
  
  df = df.groupby("user_id").applyInPandas(avg_order_size_pandas, schema = "user_id string, avg_order_size double")
  return df

# COMMAND ----------

@dlt.table()
def user_features():
  pct_reorders_per_user = dlt.read("pct_reorders_per_user")
  avg_days_btw_orders_per_user = dlt.read("avg_days_btw_orders_per_user")
  avg_order_size_per_user = dlt.read("avg_order_size_per_user")
  user_table = pct_reorders_per_user.join(avg_days_btw_orders_per_user, on="user_id").join(avg_order_size_per_user, on="user_id")
  return user_table

# COMMAND ----------

# save summary statistics to output table
@dlt.table()
def user_features_summary_stats():
  user_table = dlt.read("user_features")
  summary_stats = user_table.describe()
  summary_stats = summary_stats.withColumn("timestamp", F.current_timestamp())
  return summary_stats
