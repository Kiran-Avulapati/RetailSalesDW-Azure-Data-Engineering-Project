-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Init — create catalog + bronze/silver/gold schemas
-- COMMAND ----------

/*
===================================================
Create Database/Catalog and Schemas
===================================================
Script Purpose:
  This script create the catalog if the same catalog exists with same name it drops and then create the new catalog
  If it dropped the exsiting catalog and then create the three schema's inside of the database/catalog :Bronze,Silver,Gold
Warning:
  If database exists and have the data then the data will be dropped.
====================================================


D
---Using the newly created Catalog/Database---sql_data_warehouse
  
use catalog sql_datawarehouse;


-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Checking whether the catalog exists with same name if exists drop the catalog 

-- COMMAND ----------

drop catalog if exists sql_datawarehouse cascade;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Create the catalog/Database 

-- COMMAND ----------

create catalog sql_datawarehouse

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Use the created catalog/database for the project

-- COMMAND ----------

use catalog sql_datawarehouse;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Create the three schema's Layers _Bronze,Silver,Gold_

-- COMMAND ----------

create schema bronze;
create schema silver;
create schema gold;


-- COMMAND ----------
