-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Silver — crm_cust_info (dedupe, trim, standardize gender/marital status)
-- COMMAND ----------

/*
==========================================
This Script is to transform the bronze crm_cust_info table data and load into the silver schema crm_cust_info table
==========================================
This truncates the existing data if exists in silver schema data
and loads the newly data into the silver tablesof crm_cust_info
===========================================

*/



-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Data cleansing table wise 
-- MAGIC ### 1.CRM_cust_info
-- MAGIC ### Display the entire table

-- COMMAND ----------

use catalog sql_datawarehouse;
select * from sql_datawarehouse.bronze.crm_cust_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Check the primary key quality to not to have duplicates and nulls in the primary key column

-- COMMAND ----------

select cst_id,count(*) as repetation_of_primarykey from sql_datawarehouse.bronze.crm_cust_info group by cst_id having count(*)>1 or cst_id is null;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Need to check why we have same key valued rows multiple times

-- COMMAND ----------

select * from sql_datawarehouse.bronze.crm_cust_info where cst_id=29466;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Now need to transform the primary key column to have unique values to keep the recent record as it is

-- COMMAND ----------

select *,
row_number() over(partition by cst_id order by cst_create_date desc) as flag
from sql_datawarehouse.bronze.crm_cust_info where cst_id=29466;
select * from (select *,
row_number() over(partition by cst_id order by cst_create_date desc) as flag
from sql_datawarehouse.bronze.crm_cust_info) where flag=1;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Check for the unwanted spaces in the names columns and find the those names

-- COMMAND ----------

select cst_firstname from sql_datawarehouse.bronze.crm_cust_info where trim(cst_firstname)!=cst_firstname;
select cst_lastname from sql_datawarehouse.bronze.crm_cust_info where trim(cst_lastname)!=cst_lastname;
select cst_gndr from sql_datawarehouse.bronze.crm_cust_info where trim(cst_gndr)!=cst_gndr;
select cst_marital_status from sql_datawarehouse.bronze.crm_cust_info where trim(cst_marital_status)!=cst_marital_status;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Now Transform those name using trim function

-- COMMAND ----------

select 
  cst_id,
  cst_key,
  trim(cst_firstname) as cst_firstname,
  trim(cst_lastname) as cst_lastname,
  cst_marital_status,
  cst_gndr,
  cst_create_date
from (select *,
row_number() over(partition by cst_id order by cst_create_date desc) as flag
from sql_datawarehouse.bronze.crm_cust_info) where flag=1 and cst_id is not null;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### So we are good with primary key and names now we need to standardize the data for gender and marital_status columns
-- MAGIC 

-- COMMAND ----------

select distinct cst_marital_status from sql_datawarehouse.bronze.crm_cust_info;
select 
  cst_id,
  cst_key,
  trim(cst_firstname) as cst_firstname,
  trim(cst_lastname) as cst_lastname,
  case
    when upper(trim(cst_marital_status)) = 'S' then 'Single'
    when upper(trim(cst_marital_status)) = 'M' then 'Married'
    else 'n/a'
  end as cst_marital_status,
  case 
    when upper(trim(cst_gndr)) = 'M' then 'Male'
    when upper(trim(cst_gndr)) = 'F' then 'Female'
    else 'n/a' 
  end as cst_gndr,
  cst_create_date
from (
  select *,
    row_number() over(partition by cst_id order by cst_create_date desc) as flag
  from sql_datawarehouse.bronze.crm_cust_info
) 
where flag = 1 and cst_id is not null;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Before loading data into silver table we need to truncate the data to avoid duplicate data

-- COMMAND ----------

truncate table sql_datawarehouse.silver.crm_cust_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Insert the cleansed and transformed data into SILVER Schema
-- MAGIC 

-- COMMAND ----------

insert into sql_datawarehouse.silver.crm_cust_info(
cst_id,
cst_key,
cst_firstname,
cst_lastname,
cst_marital_status,
cst_gndr,
cst_create_date,
dwh_create_date
)
select 
  cst_id,
  cst_key,
  trim(cst_firstname) as cst_firstname,
  trim(cst_lastname) as cst_lastname,
  case
    when upper(trim(cst_marital_status)) = 'S' then 'Single'
    when upper(trim(cst_marital_status)) = 'M' then 'Married'
    else 'n/a'
  end as cst_marital_status,
  case 
    when upper(trim(cst_gndr)) = 'M' then 'Male'
    when upper(trim(cst_gndr)) = 'F' then 'Female'
    else 'n/a' 
  end as cst_gndr,
  cst_create_date,
  getdate() as dwh_create_date
from (
  select *,
    row_number() over(partition by cst_id order by cst_create_date desc) as flag
  from sql_datawarehouse.bronze.crm_cust_info
) 
where flag = 1 and cst_id is not null;
select * from sql_datawarehouse.silver.crm_cust_info;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Validate the data after transforming for duplicates and nulls in the loaded silver schema's
-- MAGIC 1.Primary key check
-- MAGIC expectation:No Results

-- COMMAND ----------

select cst_id,count(*) as count_of_primarykey from sql_datawarehouse.silver.crm_cust_info group by cst_id having count(*)>1 or cst_id is null;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC 2.unwanted spaces 
-- MAGIC Expectation : No results

-- COMMAND ----------

select cst_firstname from sql_datawarehouse.silver.crm_cust_info where trim(cst_firstname)!=cst_firstname;

select cst_lastname from sql_datawarehouse.silver.crm_cust_info where trim(cst_lastname)!=cst_lastname;
select distinct cst_gndr from sql_datawarehouse.silver.crm_cust_info;
select distinct cst_marital_status from sql_datawarehouse.silver.crm_cust_info;


-- COMMAND ----------
