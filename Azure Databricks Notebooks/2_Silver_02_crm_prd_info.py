-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Silver — crm_prd_info (derive cat_id/prd_key, cost nulls, product line, end-date fix)
-- COMMAND ----------


/*
==========================================
This Script is to transform the bronze crm_prd_info table data and load into the silver schema crm_prd_info table
==========================================
This truncates the existing data if exists in silver schema data
and loads the newly data into the silver tablesof crm_prd_info
===========================================

*/






-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Display the prodcut info table data and analyze

-- COMMAND ----------

use catalog sql_datawarehouse;
select * from sql_datawarehouse.bronze.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Check if we have any duplicates or nulls in primary key

-- COMMAND ----------

select prd_id,count(*) from sql_datawarehouse.bronze.crm_prd_info group by prd_id having count(*)>1 or prd_id is null;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### So we can see that we don't have any duplicates or nulls in the primary key column cst_id
-- MAGIC ### Next we need to proceed with the other columns 
-- MAGIC ### In the prd_key column we have product catergory as first 5 characters and we notice that data in product catergory table from erp source having like product_catergory so we are replacing the '-' with '_';

-- COMMAND ----------

select * from sql_datawarehouse.bronze.erp_px_cat_g1v2;
select 
prd_id,
prd_key,
replace(substring(prd_key,1,5),'-','_') as cat_id,
prd_nm,
prd_cost,
prd_line,
prd_start_dt,
prd_end_dt from sql_datawarehouse.bronze.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### We have to extract prd_key data without the category data

-- COMMAND ----------

select 
prd_id,
prd_key,
replace(substring(prd_key,1,5),'-','_') as cat_id,
substring(prd_key,7,len(prd_key)) as prd_key,
prd_nm,
prd_cost,
prd_line,
prd_start_dt,
prd_end_dt from sql_datawarehouse.bronze.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ####Now check the column product name column whether we have the unwanted spaces

-- COMMAND ----------

select prd_nm from sql_datawarehouse.bronze.crm_prd_info where trim(prd_nm)!=prd_nm;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ####Conclusion we don't have any unwanted spaces in name column
-- MAGIC ####Now need to check the quality of product cost column not to have null or negative numbers

-- COMMAND ----------

select prd_cost from sql_datawarehouse.bronze.crm_prd_info where prd_cost is null or prd_cost<0;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### We found a null in the cost column so we replace them with zero

-- COMMAND ----------

select 
prd_id,
prd_key,
replace(substring(prd_key,1,5),'-','_') as cat_id,
substring(prd_key,7,len(prd_key)) as prd_key,
prd_nm,
ifnull(prd_cost, 0) as prd_cost,
prd_line,
prd_start_dt,
prd_end_dt from sql_datawarehouse.bronze.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### we are good with product cost table as replaced nulls with zeroes
-- MAGIC #### Next we have product line columns
-- MAGIC #### Find the distinct values in prd_line columns

-- COMMAND ----------

SELECT DISTINCT prd_line from sql_datawarehouse.bronze.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### Now replace  the abbrivation with Understandable values

-- COMMAND ----------

select 
prd_id,
prd_key,
replace(substring(prd_key,1,5),'-','_') as cat_id,
substring(prd_key,7,len(prd_key)) as prd_key,
prd_nm,
ifnull(prd_cost, 0) as prd_cost,
case
  when upper(trim(prd_line))="M" then 'Mountain'
  when upper(trim(prd_line))='R' then 'Road'
  when upper(trim(prd_line))='T' then 'Touring'
  when upper(trim(prd_line))='S' then 'Other Sales'
  else 'n/a'
end as prd_line,
prd_start_dt,
prd_end_dt from sql_datawarehouse.bronze.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### Optimize the case function

-- COMMAND ----------

select 
prd_id,
prd_key,
replace(substring(prd_key,1,5),'-','_') as cat_id,
substring(prd_key,7,len(prd_key)) as prd_key,
prd_nm,
ifnull(prd_cost, 0) as prd_cost,
case upper(trim(prd_line))
  when "M" then 'Mountain'
  when 'R' then 'Road'
  when 'T' then 'Touring'
  when 'S' then 'Other Sales'
  else 'n/a'
end as prd_line,
prd_start_dt,
prd_end_dt from sql_datawarehouse.bronze.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### Now check for product start and end dates columns inconsisitencies

-- COMMAND ----------

select prd_id,prd_key,prd_start_dt,prd_end_dt from sql_datawarehouse.bronze.crm_prd_info;
select prd_id,prd_key,prd_start_dt,prd_end_dt from sql_datawarehouse.bronze.crm_prd_info where prd_end_dt<prd_start_dt;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### Here we see that prd_end_date as before the prd_start_date which is not correct so we need to transform the end date column

-- COMMAND ----------

select 
prd_id,
prd_key,
cast(prd_start_dt as date) as prd_start_dt,
cast(lead(prd_start_dt) over(partition by prd_key order by prd_start_dt)-1 as date) as prd_end_dt

from sql_datawarehouse.bronze.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### We have used lead window function to use the next startdate minus one day as end_date to avoid the intersections of the prodcut id 

-- COMMAND ----------

select 
prd_id,
prd_key,
replace(substring(prd_key,1,5),'-','_') as cat_id,
substring(prd_key,7,len(prd_key)) as prd_key,
prd_nm,
ifnull(prd_cost, 0) as prd_cost,
case upper(trim(prd_line))
  when "M" then 'Mountain'
  when 'R' then 'Road'
  when 'T' then 'Touring'
  when 'S' then 'Other Sales'
  else 'n/a'
end as prd_line,
prd_start_dt,
lead(prd_start_dt) over(partition by prd_key order by prd_start_dt)-1 as prd_end_dt
from sql_datawarehouse.bronze.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### So here we fixed the data now it's time to load date into the silver tables
-- MAGIC ### But the issue here is metadata in the tables like we have extra columns need to modify the table schema using DDL Commands

-- COMMAND ----------

select * from sql_datawarehouse.silver.crm_prd_info;
create or replace table sql_datawarehouse.silver.crm_prd_info(
  prd_id int,
  cat_id varchar(50),
  prd_key varchar(50),
  prd_nm varchar(50),
  prd_cost int,
  prd_line varchar(50),
  prd_start_dt date,
  prd_end_dt date ,
  dwh_create_date date);
select * from sql_datawarehouse.silver.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Before loading data into silver table we need to truncate the data to avoid duplicate data

-- COMMAND ----------

truncate table sql_datawarehouse.silver.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### we need to store transformed data into silver table

-- COMMAND ----------

insert into sql_datawarehouse.silver.crm_prd_info(
  prd_id,
  cat_id,
  prd_key,
  prd_nm,
  prd_cost,
  prd_line,
  prd_start_dt,
  prd_end_dt,
  dwh_create_date
)
select 
prd_id,
replace(substring(prd_key,1,5),'-','_') as cat_id,
substring(prd_key,7,len(prd_key)) as prd_key,
prd_nm,
ifnull(prd_cost, 0) as prd_cost,
case upper(trim(prd_line))
  when "M" then 'Mountain'
  when 'R' then 'Road'
  when 'T' then 'Touring'
  when 'S' then 'Other Sales'
  else 'n/a'
end as prd_line,
prd_start_dt,
lead(prd_start_dt) over(partition by prd_key order by prd_start_dt)-1 as prd_end_dt,
getdate() as dwh_create_date
from sql_datawarehouse.bronze.crm_prd_info;
select * from sql_datawarehouse.silver.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### We loaded the data into the silver tables 
-- MAGIC #### Quality check of the silver table
-- MAGIC Primary key check

-- COMMAND ----------

select prd_id,count(*) from sql_datawarehouse.silver.crm_prd_info group by prd_id having count(*)>1;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Check for the unwanted spaces in the product name column

-- COMMAND ----------

select prd_nm from sql_datawarehouse.silver.crm_prd_info where trim(prd_nm)!=prd_nm;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Check the count of product line varities

-- COMMAND ----------

select distinct prd_line from sql_datawarehouse.silver.crm_prd_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Check for the Start and date consisitency

-- COMMAND ----------

select prd_id,prd_start_dt,prd_end_dt from sql_datawarehouse.silver.crm_prd_info where prd_end_dt<prd_start_dt;
SELECT * from sql_datawarehouse.silver.crm_prd_info

-- COMMAND ----------

-- MAGIC %md
-- MAGIC # We are good with product table data in the silver table
-- MAGIC 

-- COMMAND ----------
