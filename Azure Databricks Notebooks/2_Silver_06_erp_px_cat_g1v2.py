-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Silver — erp_px_cat_g1v2 (category/subcategory pass-through + checks)
-- COMMAND ----------

/*
==========================================
This Script is to transform the bronze ERP_px_cat_g1v2 table data and load into the silver schema ERP_px_cat_g1v2 table
==========================================
This truncates the existing data if exists in silver schema data
and loads the newly data into the silver tables of ERP_px_cat_g1v2
===========================================

*/




-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Now we are with the last table product categories table we need to transform the table and load into the silver table
-- MAGIC ### Let us start analyzing the table

-- COMMAND ----------

use catalog sql_datawarehouse;
select * from sql_datawarehouse.bronze.erp_px_cat_g1v2;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### During the table modeling we saw a relationship between product info in CRM source table

-- COMMAND ----------

select * from sql_datawarehouse.silver.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Now we can see that cat_id in product info table relates with id in px_cat_g1v2 table
-- MAGIC ### So we have the good data in ID column of px_cat table so lets check for next columns

-- COMMAND ----------

select cat from sql_datawarehouse.bronze.erp_px_cat_g1v2 where trim(cat)!=cat;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### we can see the cat column have no unwanted spaces lets check the same for the next column subcat

-- COMMAND ----------

select cat from sql_datawarehouse.bronze.erp_px_cat_g1v2 where trim(subcat)!=subcat;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Found no unwanted spaces in the px_cat table let's check for the maintainence columns

-- COMMAND ----------

select cat from sql_datawarehouse.bronze.erp_px_cat_g1v2 where trim(MAINTENANCE)!=MAINTENANCE;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### We have no issues in all the columns let start with data standardization and consistency

-- COMMAND ----------

select distinct cat from sql_datawarehouse.bronze.erp_px_cat_g1v2;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Do it the same for all the columns

-- COMMAND ----------

select distinct subcat from sql_datawarehouse.bronze.erp_px_cat_g1v2;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Let's check in the maintanance

-- COMMAND ----------

select distinct MAINTENANCE from sql_datawarehouse.bronze.erp_px_cat_g1v2;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Before loading data into silver table we need to truncate the data to avoid duplicate data

-- COMMAND ----------

truncate table sql_datawarehouse.silver.erp_px_cat_g1v2;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Even if the table has no issues we need to store in the silver table

-- COMMAND ----------

insert into sql_datawarehouse.silver.erp_px_cat_g1v2(id,cat,subcat,MAINTENANCE,dwh_create_date)
select
id,
cat,
subcat,
maintenance,
getdate() as dwh_create_date
from
sql_datawarehouse.bronze.erp_px_cat_g1v2;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Let us check the loaded data in silver table

-- COMMAND ----------

select * from sql_datawarehouse.silver.erp_px_cat_g1v2;


-- COMMAND ----------
