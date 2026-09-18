-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Silver — erp_loc_a101 (clean CID, standardize country names)
-- COMMAND ----------

/*
==========================================
This Script is to transform the bronze ERP_loc_a101 table data and load into the silver schema ERP_loc_a101 table
==========================================
This truncates the existing data if exists in silver schema data
and loads the newly data into the silver tables of ERP_loc_a101
===========================================

*/





-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Now we transforming thr Bronze table ERP_loc_A101 table to silver table 
-- MAGIC Start analyzing the erp loc a101 table

-- COMMAND ----------

use catalog sql_datawarehouse;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Let us pull the data from bronze table of erp_location of the customer

-- COMMAND ----------

select * from sql_datawarehouse.bronze.erp_loc_a101;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC We can see that customer cid is related to cst_key from cust info table and we can get that location tagged

-- COMMAND ----------

select * from sql_datawarehouse.silver.crm_cust_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC We can see the cid and cst_key has to be in same data format
-- MAGIC So we tranform the cid column in loc table

-- COMMAND ----------

select cid from sql_datawarehouse.bronze.erp_loc_a101;

select cst_key from sql_datawarehouse.silver.crm_cust_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Transformt the cid columns

-- COMMAND ----------

select
replace(cid,'-','') as cid,
cntry
from sql_datawarehouse.bronze.erp_loc_a101;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Let us see all the distinct locationss

-- COMMAND ----------

select distinct cntry from sql_datawarehouse.bronze.erp_loc_a101;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Now we need to standardize the country data

-- COMMAND ----------

select
replace(cid,'-','') as cid,
case
  when trim(cntry)='DE' then 'Germany'
  when trim(cntry) in ('US','USA') then 'United States'
  when trim(cntry)='' or cntry is null then 'n/a'
  else cntry
end as cntry
from sql_datawarehouse.bronze.erp_loc_a101; 

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Let us see the tranformation worked or not?

-- COMMAND ----------

select distinct
cntry as oldcountry,
case
  when trim(cntry)='DE' then 'Germany'
  when trim(cntry) in ('US','USA') then 'United States'
  when trim(cntry)='' or cntry is null then 'n/a'
  else cntry
end as cntry
from sql_datawarehouse.bronze.erp_loc_a101 order by cntry;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC We need to load the data as we didn't change any schema so no need to change the ddl
-- MAGIC ### Before loading data into silver table we need to truncate the data to avoid duplicate data

-- COMMAND ----------

truncate table sql_datawarehouse.silver.erp_loc_a101;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC we will load the data into silver table

-- COMMAND ----------

insert into sql_datawarehouse.silver.erp_loc_a101(cid,cntry,dwh_create_date)
select
replace(cid,'-','') as cid,
case
  when trim(cntry)='DE' then 'Germany'
  when trim(cntry) in ('US','USA') then 'United States'
  when trim(cntry)='' or cntry is null then 'n/a'
  else cntry
end as cntry,
getdate() as dwh_create_date
from sql_datawarehouse.bronze.erp_loc_a101; 

-- COMMAND ----------

-- MAGIC %md
-- MAGIC We loaded the data now need to check the quality in silver table

-- COMMAND ----------

select distinct cntry from sql_datawarehouse.silver.erp_loc_a101;
select * from sql_datawarehouse.silver.erp_loc_a101;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## NOW the data is standardized
-- MAGIC 

-- COMMAND ----------
