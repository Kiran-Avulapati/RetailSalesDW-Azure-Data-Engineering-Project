-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Silver — erp_cust_az12 (clean CID, birthdate bounds, gender standardization)
-- COMMAND ----------

/*
==========================================
This Script is to transform the bronze ERP_Cust_az12 table data and load into the silver schema ERP_Cust_az12 table
==========================================
This truncates the existing data if exists in silver schema data
and loads the newly data into the silver tablesof ERP_Cust_az12
===========================================

*/

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Let us Ananlyze the ERP_Cust_az12 Table

-- COMMAND ----------

use catalog sql_datawarehouse;
select * from sql_datawarehouse.bronze.erp_cust_az12;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### As we know that it relates to customer info table during data modeling 
-- MAGIC ### So now we are going to analyze the silver customerinfo table with current table

-- COMMAND ----------

select * from sql_datawarehouse.silver.crm_cust_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### We can see the column column that CID and cst_key relates
-- MAGIC ### There are extra characters in the cid column where compared to cst_key columns

-- COMMAND ----------

select * from sql_datawarehouse.bronze.erp_cust_az12 where cid like '%AW000%';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Check if we have the exact words without any characters in cid

-- COMMAND ----------

select * from sql_datawarehouse.bronze.erp_cust_az12 where cid like 'AW00%';

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Yes we do have the rows where data is good without any extra characters we need to handle that cases as well

-- COMMAND ----------

select
cid,
case 
  when cid like 'NAS%' then substring(cid,4,len(cid))
  else cid
end cid,
BDATE,
gen
from sql_datawarehouse.bronze.erp_cust_az12;


-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### We removed extra unwanted characters in cid coulmn now need to check every key presents in silver customer info table

-- COMMAND ----------

with temp as(
select
cid,
case 
  when cid like 'NAS%' then substring(cid,4,len(cid))
  else cid
end as cid1,
BDATE,
gen
from sql_datawarehouse.bronze.erp_cust_az12)
select
cid,
cid1,
BDATE,
gen from temp
where cid1 not in (select distinct cst_key from sql_datawarehouse.silver.crm_cust_info);


-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### So we can see that no rows returned so every cid is present in cst_key in silver cust table

-- COMMAND ----------

select
case 
  when cid like 'NAS%' then substring(cid,4,len(cid))
  else cid
end cid,
BDATE,
gen
from sql_datawarehouse.bronze.erp_cust_az12;


-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Let us check for the BDate column

-- COMMAND ----------

select bdate from sql_datawarehouse.bronze.erp_cust_az12;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Check if we have customer whose birth date is 100 years before or in future

-- COMMAND ----------

select bdate from sql_datawarehouse.bronze.erp_cust_az12 where bdate <'1924-01-01' or bdate > getdate();

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### To handle the case of future birth date we will replace the bdate as null

-- COMMAND ----------

select
case 
  when cid like 'NAS%' then substring(cid,4,len(cid))
  else cid
end cid,
case
  when bdate >getdate() then null
  else bdate end as bdate,
gen
from sql_datawarehouse.bronze.erp_cust_az12;


-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Now need to work on the gender column

-- COMMAND ----------

select distinct gen from sql_datawarehouse.bronze.erp_cust_az12;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC We see data issue with consistency and need to perform data standardization

-- COMMAND ----------

select 
gen,
case 
  when upper(trim(gen)) in ('F','FEMALE') then 'Female'
  when upper(trim(gen)) in ('M','MALE') then 'Male'
  else 'n/a'
  end as gen


 from sql_datawarehouse.bronze.erp_cust_az12;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Finally adding all the transformation to single query 

-- COMMAND ----------

select
case 
  when cid like 'NAS%' then substring(cid,4,len(cid))
  else cid
end cid,
case
  when bdate >getdate() then null
  else bdate end as bdate,
case 
  when upper(trim(gen)) in ('F','FEMALE') then 'Female'
  when upper(trim(gen)) in ('M','MALE') then 'Male'
  else 'n/a'
  end as gen
from sql_datawarehouse.bronze.erp_cust_az12;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Before loading data into silver table we need to truncate the data to avoid duplicate data

-- COMMAND ----------

truncate table sql_datawarehouse.silver.erp_cust_az12;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Load the transfomed data into silver erp_cust_az12 table

-- COMMAND ----------

insert into sql_datawarehouse.silver.erp_cust_az12(cid,bdate,gen,dwh_create_date)
select
case 
  when cid like 'NAS%' then substring(cid,4,len(cid))
  else cid
end cid,
case
  when bdate >getdate() then null
  else bdate end as bdate,
case 
  when upper(trim(gen)) in ('F','FEMALE') then 'Female'
  when upper(trim(gen)) in ('M','MALE') then 'Male'
  else 'n/a'
  end as gen,
getdate() as dwh_create_date
from sql_datawarehouse.bronze.erp_cust_az12;


-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Perform the data quality checks
-- MAGIC For bdate column

-- COMMAND ----------

select bdate from sql_datawarehouse.silver.erp_cust_az12 where BDATE <'1924-01-01' or bdate >getdate();

-- COMMAND ----------

-- MAGIC %md
-- MAGIC For Gender columns

-- COMMAND ----------

SELECT DISTINCT gen from sql_datawarehouse.silver.erp_cust_az12;
select * from sql_datawarehouse.silver.erp_cust_az12;
select count(*) from sql_datawarehouse.silver.erp_cust_az12;


-- COMMAND ----------
