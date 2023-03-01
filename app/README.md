# Feature Engineering Pipeline Overview

The sample feature engineering pipeline follows the [Medallion Architecture](https://www.databricks.com/glossary/medallion-architecture) data design pattern to logically organize data in Databricks.

0. **Initialize**: Setup script to download sample data and create a database for DLT output
1. **Ingest data into Bronze Layer**: Reads in raw data in csv format and storing them as the bronze table
2. **Loading into Silver Layer**: Performs quality control and cleans up the data for the silver table
3. **Feature Engineering**: Feature engineering logic is applied on the silver table
4. **Load to Feature Store**: Store the features into a Feature Store table

Each of these are modularized as separate component and can be linked together as a Databricks multi-task Job.