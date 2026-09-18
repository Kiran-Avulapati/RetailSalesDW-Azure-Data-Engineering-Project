-- Databricks notebook source
-- MAGIC %md
-- MAGIC # DDL — Bronze tables
-- COMMAND ----------

===============================
DDL Script:Create Bronze Tables
===============================
Script Purpose:
This scripts creates Tables in the Bronze Schema ,dropping exiting table 
if they alredy exists.
Run this script to re-define the DDL Strucure of 'Bronze' Tables

========================================================


-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Use the defined catalog sql_datawarehouse

-- COMMAND ----------

use catalog sql_datawarehouse;

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Create a tables based on the source datasets for ERP and CRM Data sets
-- MAGIC ###  If Tables are already presented replace them with new tables
-- MAGIC 
-- MAGIC ### First table crm_cust_info

-- COMMAND ----------

create or replace table bronze.crm_cust_info(
cst_id int,
cst_key varchar(50),
cst_firstname varchar(50),
cst_lastname varchar(50),
cst_marital_status varchar(50),
cst_gndr varchar(50),
cst_create_date date
);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Second table crm_prd_info

-- COMMAND ----------

create or replace table bronze.crm_prd_info(
  prd_id int,
  prd_key varchar(50),
  prd_nm varchar(50),
  prd_cost int,
  prd_line varchar(50),
  prd_start_dt date,
  prd_end_dt date
);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Third Table crm_sales_details

-- COMMAND ----------

create or replace table bronze.crm_sales_details(
  sls_ord_num varchar(50),
  sls_prd_key varchar(50),
  sls_cust_id int,
  sls_order_dt int,
  sls_ship_dt int,
  sls_due_dt int,
  sls_sales int,
  sls_quantity int,
  sls_price int
);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Fourth Table erp_cust_AZ12
-- MAGIC 

-- COMMAND ----------

create or replace table bronze.erp_cust_AZ12(
  CID varchar(50),
  BDATE date,
  GEN varchar(50)
);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Fifth Table erp_Loc_A101

-- COMMAND ----------

create or replace table bronze.erp_loc_a101(
  cid varchar(50),
  cntry varchar(50)
);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ### Sixth Table ERP_PX_CAT_G1V2

-- COMMAND ----------

create or replace table bronze.erp_px_cat_g1v2(
  id varchar(50),
  cat varchar(50),
  subcat varchar(50),
  MAINTENANCE varchar(50)
);

-- COMMAND ----------

-- MAGIC %md
-- MAGIC ## By this we created a required table to store data from the sourse systems
-- MAGIC 

-- COMMAND ----------
