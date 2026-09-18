# Databricks notebook source
# MAGIC %md
# MAGIC ## 3. Delta Live Tables — Gold Star Schema
# MAGIC Rebuilds the original `dim_customers` / `dim_products` / `fact_sales` *views*
# MAGIC (Scripts/gold/*.sql) as managed **DLT tables** with declarative data-quality
# MAGIC expectations — mirroring the Netflix project's `7_DLT_Notebook.ipynb` pattern
# MAGIC (`dlt.expect_all_or_drop`). Bad rows are dropped and counted automatically instead
# MAGIC of being silently joined in.

# COMMAND ----------

import dlt
from pyspark.sql.functions import row_number, coalesce, col, when
from pyspark.sql.window import Window

# COMMAND ----------

# MAGIC %md
# MAGIC ### `dim_customers`
# MAGIC CRM customer master + ERP birthdate/gender + ERP country, deduped, with a
# MAGIC surrogate `customer_key`.

# COMMAND ----------

customer_rules = {
    "valid_customer_id": "customer_id IS NOT NULL",
    "valid_customer_key": "customer_key IS NOT NULL",
}


@dlt.table(name="dim_customers", comment="Customer dimension (CRM + ERP birthdate/gender/location)")
@dlt.expect_all_or_drop(customer_rules)
def dim_customers():
    ci = spark.read.table("sql_datawarehouse.silver.crm_cust_info")
    ca = spark.read.table("sql_datawarehouse.silver.erp_cust_az12")
    la = spark.read.table("sql_datawarehouse.silver.erp_loc_a101")

    df = (
        ci.alias("ci")
        .join(ca.alias("ca"), col("ci.cst_key") == col("ca.cid"), "left")
        .join(la.alias("la"), col("la.cid") == col("ci.cst_key"), "left")
        .select(
            row_number().over(Window.orderBy("ci.cst_id")).alias("customer_key"),
            col("ci.cst_id").alias("customer_id"),
            col("ci.cst_key").alias("customer_number"),
            col("ci.cst_firstname").alias("first_name"),
            col("ci.cst_lastname").alias("last_name"),
            col("la.cntry").alias("country"),
            col("ci.cst_marital_status").alias("marital_status"),
            when(col("ci.cst_gndr") != "n/a", col("ci.cst_gndr"))
            .otherwise(coalesce(col("ca.gen"), "n/a"))
            .alias("gender"),
            col("ca.bdate").alias("birthdate"),
            col("ci.cst_create_date").alias("create_date"),
        )
    )
    return df

# COMMAND ----------

# MAGIC %md
# MAGIC ### `dim_products`
# MAGIC Current (non-retired) CRM products joined with ERP category/subcategory.

# COMMAND ----------

product_rules = {
    "valid_product_id": "product_id IS NOT NULL",
    "valid_product_key": "product_key IS NOT NULL",
}


@dlt.table(name="dim_products", comment="Product dimension (current products only, CRM + ERP category)")
@dlt.expect_all_or_drop(product_rules)
def dim_products():
    pn = spark.read.table("sql_datawarehouse.silver.crm_prd_info").where(col("prd_end_dt").isNull())
    pc = spark.read.table("sql_datawarehouse.silver.erp_px_cat_g1v2")

    df = (
        pn.alias("pn")
        .join(pc.alias("pc"), col("pn.cat_id") == col("pc.id"), "left")
        .select(
            row_number().over(Window.orderBy("pn.prd_start_dt", "pn.prd_key")).alias("product_key"),
            col("pn.prd_id").alias("product_id"),
            col("pn.prd_key").alias("product_number"),
            col("pn.prd_nm").alias("product_name"),
            col("pn.cat_id").alias("category_id"),
            col("pc.cat").alias("category"),
            col("pc.subcat").alias("subcategory"),
            col("pc.MAINTENANCE").alias("maintenance"),
            col("pn.prd_cost").alias("cost"),
            col("pn.prd_line").alias("product_line"),
            col("pn.prd_start_dt").alias("start_date"),
        )
    )
    return df

# COMMAND ----------

# MAGIC %md
# MAGIC ### `fact_sales`
# MAGIC CRM sales events, resolved to the `dim_customers`/`dim_products` surrogate keys.
# MAGIC Expectations here check both required measures and referential integrity —
# MAGIC unmatched product/customer keys are dropped rather than silently kept as NULL.

# COMMAND ----------

sales_rules = {
    "valid_order_number": "order_number IS NOT NULL",
    "valid_product_key": "product_key IS NOT NULL",
    "valid_customer_key": "customer_key IS NOT NULL",
    "non_negative_sales": "sales_amount >= 0",
}


@dlt.table(name="fact_sales", comment="Sales fact table, keyed to dim_customers/dim_products")
@dlt.expect_all_or_drop(sales_rules)
def fact_sales():
    sd = spark.read.table("sql_datawarehouse.silver.crm_sales_details")
    pr = dlt.read("dim_products")
    cu = dlt.read("dim_customers")

    df = (
        sd.alias("sd")
        .join(pr.alias("pr"), col("sd.sls_prd_key") == col("pr.product_number"), "left")
        .join(cu.alias("cu"), col("sd.sls_cust_id") == col("cu.customer_id"), "left")
        .select(
            col("sd.sls_ord_num").alias("order_number"),
            col("pr.product_key").alias("product_key"),
            col("cu.customer_key").alias("customer_key"),
            col("sd.sls_order_dt").alias("order_date"),
            col("sd.sls_ship_dt").alias("shipping_date"),
            col("sd.sls_due_dt").alias("due_date"),
            col("sd.sls_sales").alias("sales_amount"),
            col("sd.sls_quantity").alias("quantity"),
            col("sd.sls_price").alias("price"),
        )
    )
    return df
