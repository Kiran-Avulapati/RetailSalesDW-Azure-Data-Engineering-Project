-- Databricks notebook source
-- MAGIC %md
-- MAGIC # Silver — crm_sales_details (date + FK integrity fixes)
-- COMMAND ----------

/*
==========================================
This Script is to transform the bronze crm_sales_details table data and load into the silver schema crm_sales_details table
==========================================
This truncates the existing data if exists in silver schema data
and loads the newly data into the silver tablesof crm_sales_details
===========================================

*/


-- COMMAND ----------

-- MAGIC %md
-- MAGIC # We are now data cleaning the sales details table
-- MAGIC #### Diplaying the data from sales details table to analyze

-- COMMAND ----------

use catalog sql_datawarehouse;
describe table sql_datawarehouse.bronze.crm_sales_details;
select * from sql_datawarehouse.bronze.crm_sales_details;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### Data quality check for the sales details table before transformation
-- MAGIC check for Sales_order_number  having unwanted spaces

-- COMMAND ----------

select 
sls_ord_num,
sls_prd_key,
sls_cust_id,
sls_order_dt,
sls_ship_dt,
sls_due_dt,
sls_sales,
sls_quantity
sls_price from sql_datawarehouse.bronze.crm_sales_details where sls_ord_num != Trim(sls_ord_num);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Check for the integrity of the product key and customer id with the product key in product table and for cust_id in cust_info table from silver table;
-- MAGIC Product Key

-- COMMAND ----------

select 
sls_ord_num,
sls_prd_key,
sls_cust_id,
sls_order_dt,
sls_ship_dt,
sls_due_dt,
sls_sales,
sls_quantity
sls_price from sql_datawarehouse.bronze.crm_sales_details where sls_prd_key not in (select prd_key from sql_datawarehouse.silver.crm_prd_info);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Cust_id

-- COMMAND ----------

select 
sls_ord_num,
sls_prd_key,
sls_cust_id,
sls_order_dt,
sls_ship_dt,
sls_due_dt,
sls_sales,
sls_quantity
sls_price from sql_datawarehouse.bronze.crm_sales_details where sls_cust_id not in (select cst_id from sql_datawarehouse.silver.crm_cust_info);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### We are good with first three columns prd_key and cust_id columns no issue found
-- MAGIC We are with sls_order_dt,sls_ship_dt,sls_due_dt columns have issue with type of the data as they are in interger form we need to cast them to date format

-- COMMAND ----------

select sls_order_dt from sql_datawarehouse.bronze.crm_sales_details;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC check for the negative or zero valued data in the sls_order_dt  columns

-- COMMAND ----------

select sls_order_dt from sql_datawarehouse.bronze.crm_sales_details where sls_order_dt <=0;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC So we need to replace zeroes with null before casting

-- COMMAND ----------

select nullif(sls_order_dt,0) as sls_order_dt from sql_datawarehouse.bronze.crm_sales_details where sls_order_dt<=0 
or len(sls_order_dt)!=8
or sls_order_dt>20500101
or sls_order_dt<19000101;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Fixing the date issue

-- COMMAND ----------

select 
sls_ord_num,
sls_prd_key,
sls_cust_id,
case when sls_order_dt <=0 or len(sls_order_dt)!=8 then null else to_date(cast(sls_order_dt as string), 'yyyyMMdd') end as sls_order_dt,
sls_ship_dt,
sls_due_dt,
sls_sales,
sls_quantity
sls_price from sql_datawarehouse.bronze.crm_sales_details

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Check the same for ship_date

-- COMMAND ----------

select nullif(sls_ship_dt,0) as sls_ship_dt from sql_datawarehouse.bronze.crm_sales_details where sls_ship_dt<=0 
or len(sls_ship_dt)!=8
or sls_ship_dt>20500101
or sls_ship_dt<19000101;
select 
sls_ord_num,
sls_prd_key,
sls_cust_id,
case when sls_order_dt <=0 or len(sls_order_dt)!=8 then null else to_date(cast(sls_order_dt as string), 'yyyyMMdd') end as sls_order_dt,
case when sls_ship_dt <=0 or len(sls_ship_dt)!=8 then null else to_date(cast(sls_ship_dt as string), 'yyyyMMdd') end as sls_ship_dt,
sls_due_dt,
sls_sales,
sls_quantity
sls_price from sql_datawarehouse.bronze.crm_sales_details

-- COMMAND ----------

-- MAGIC %md
-- MAGIC DO check for the Due_Date column

-- COMMAND ----------

select nullif(sls_due_dt,0) as sls_due_dt from sql_datawarehouse.bronze.crm_sales_details where sls_due_dt<=0 
or len(sls_due_dt)!=8
or sls_due_dt>20500101
or sls_due_dt<19000101;
select 
sls_ord_num,
sls_prd_key,
sls_cust_id,
case when sls_order_dt <=0 or len(sls_order_dt)!=8 then null else to_date(cast(sls_order_dt as string), 'yyyyMMdd') end as sls_order_dt,
case when sls_ship_dt <=0 or len(sls_ship_dt)!=8 then null else to_date(cast(sls_ship_dt as string), 'yyyyMMdd') end as sls_ship_dt,
case when sls_due_dt <=0 or len(sls_due_dt)!=8 then null else to_date(cast(sls_due_dt as string), 'yyyyMMdd') end as sls_due_dt,
sls_sales,
sls_quantity
sls_price from sql_datawarehouse.bronze.crm_sales_details

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### You need to check for inconsisitencies in the order data and due and ship date as occurrence of the events

-- COMMAND ----------

select sls_order_dt,sls_due_dt,sls_ship_dt from sql_datawarehouse.bronze.crm_sales_details
where sls_order_dt>sls_due_dt or sls_order_dt>sls_ship_dt;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### NO inconsistencies in the dates columns as they are in expected state no transformation required
-- MAGIC #### Now we are left with last three columns

-- COMMAND ----------

select * from sql_datawarehouse.bronze.crm_sales_details

-- COMMAND ----------

-- MAGIC %md
-- MAGIC #### There is a business rule that sales =quantity*price and this values shouldn't be a negative number or null values

-- COMMAND ----------

select sls_sales,sls_quantity,sls_price from sql_datawarehouse.bronze.crm_sales_details where sls_sales!=sls_quantity*sls_price
or sls_price<=0 or sls_sales <=0 or sls_quantity<=0
or sls_price is null or sls_sales is null or sls_quantity is null;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Fixing the null or incorrect data with the other two columns as per business experts suggestion

-- COMMAND ----------

select sls_sales,sls_quantity,sls_price,
case when sls_sales is null or sls_sales<=0 or sls_sales!=sls_quantity*abs(sls_price) then sls_quantity*abs(sls_price) else sls_sales end as new_sls_sales,
case when sls_price is null or sls_price<=0 then abs(sls_sales)/nullif(sls_quantity,0) else sls_price end as new_sls_price

 from sql_datawarehouse.bronze.crm_sales_details 

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Let us do transformation in the whole table query

-- COMMAND ----------

select 
sls_ord_num,
sls_prd_key,
sls_cust_id,
case when sls_order_dt <=0 or len(sls_order_dt)!=8 then null else to_date(cast(sls_order_dt as string), 'yyyyMMdd') end as sls_order_dt,
case when sls_ship_dt <=0 or len(sls_ship_dt)!=8 then null else to_date(cast(sls_ship_dt as string), 'yyyyMMdd') end as sls_ship_dt,
case when sls_due_dt <=0 or len(sls_due_dt)!=8 then null else to_date(cast(sls_due_dt as string), 'yyyyMMdd') end as sls_due_dt,
case when sls_sales is null or sls_sales<=0 or sls_sales!=sls_quantity*abs(sls_price) then sls_quantity*abs(sls_price) else sls_sales end as sls_sales,
sls_quantity,
case when sls_price is null or sls_price<=0 then abs(sls_sales)/nullif(sls_quantity,0) else sls_price end as sls_price,
getdate() as dwh_create_date
 from sql_datawarehouse.bronze.crm_sales_details

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Now we are good with the data now need to check the schemas we created in the ddl statements

-- COMMAND ----------

select * from sql_datawarehouse.silver.crm_sales_details;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC As there is a change in the datatype of the ship due order date columns we need to alter the table schema;
-- MAGIC 

-- COMMAND ----------

create or replace table sql_datawarehouse.silver.crm_sales_details(
  sls_ord_num varchar(50),
  sls_prd_key varchar(50),
  sls_cust_id int,
  sls_order_dt date,
  sls_ship_dt date,
  sls_due_dt date ,
  sls_sales integer,
  sls_quantity integer,
  sls_price integer,
  dwh_create_date date
  );

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Before loading data into silver table we need to truncate the data to avoid duplicate data

-- COMMAND ----------

truncate table sql_datawarehouse.silver.crm_sales_details;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC Now we need to transformed load data into silver table

-- COMMAND ----------

insert into sql_datawarehouse.silver.crm_sales_details(
  sls_ord_num ,
  sls_prd_key ,
  sls_cust_id ,
  sls_order_dt,
  sls_ship_dt ,
  sls_due_dt  ,
  sls_sales ,
  sls_quantity,
  sls_price ,
  dwh_create_date 

)
select 
sls_ord_num,
sls_prd_key,
sls_cust_id,
case when sls_order_dt <=0 or len(sls_order_dt)!=8 then null else to_date(cast(sls_order_dt as string), 'yyyyMMdd') end as sls_order_dt,
case when sls_ship_dt <=0 or len(sls_ship_dt)!=8 then null else to_date(cast(sls_ship_dt as string), 'yyyyMMdd') end as sls_ship_dt,
case when sls_due_dt <=0 or len(sls_due_dt)!=8 then null else to_date(cast(sls_due_dt as string), 'yyyyMMdd') end as sls_due_dt,
case when sls_sales is null or sls_sales<=0 or sls_sales!=sls_quantity*abs(sls_price) then sls_quantity*abs(sls_price) else sls_sales end as sls_sales,
sls_quantity,
case when sls_price is null or sls_price<=0 then abs(sls_sales)/nullif(sls_quantity,0) else sls_price end as sls_price,
getdate() as dwh_create_date
 from sql_datawarehouse.bronze.crm_sales_details


-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## Quality Check of the silver Table
-- MAGIC Unwanted spaces on sls_ord_num in silver tables

-- COMMAND ----------

select 
sls_ord_num,
sls_prd_key,
sls_cust_id,
sls_order_dt,
sls_ship_dt,
sls_due_dt,
sls_sales,
sls_quantity
sls_price from sql_datawarehouse.silver.crm_sales_details where sls_ord_num != Trim(sls_ord_num);
select 
sls_ord_num,
sls_prd_key,
sls_cust_id,
sls_order_dt,
sls_ship_dt,
sls_due_dt,
sls_sales,
sls_quantity
sls_price from sql_datawarehouse.bronze.crm_sales_details where sls_prd_key not in (select prd_key from sql_datawarehouse.silver.crm_prd_info);


select 
sls_ord_num,
sls_prd_key,
sls_cust_id,
sls_order_dt,
sls_ship_dt,
sls_due_dt,
sls_sales,
sls_quantity
sls_price from sql_datawarehouse.bronze.crm_sales_details where sls_cust_id not in (select cst_id from sql_datawarehouse.silver.crm_cust_info);


select sls_order_dt from sql_datawarehouse.silver.crm_sales_details;

select sls_order_dt from sql_datawarehouse.silver.crm_sales_details;

select sls_order_dt,sls_due_dt,sls_ship_dt from sql_datawarehouse.silver.crm_sales_details
where sls_order_dt>sls_due_dt or sls_order_dt>sls_ship_dt;
select sls_sales,sls_quantity,sls_price from sql_datawarehouse.silver.crm_sales_details where sls_sales!=sls_quantity*sls_price
or sls_price<=0 or sls_sales <=0 or sls_quantity<=0
or sls_price is null or sls_sales is null or sls_quantity is null;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## ALL the checks has been done on the sales details table after loading into the silver table and before loading we made all the required transformation
-- MAGIC 

-- COMMAND ----------
