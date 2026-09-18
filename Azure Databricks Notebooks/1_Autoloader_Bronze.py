# Databricks notebook source
# MAGIC %md
# MAGIC ## 1. Autoloader — Raw → Bronze (incremental ingestion)
# MAGIC ADF lands the source_crm / source_erp CSVs (pulled from GitHub) into the ADLS Gen2
# MAGIC **`raw`** container. This notebook uses Databricks **Autoloader** (`cloudFiles`) to
# MAGIC incrementally detect and load only new/changed files into the **Bronze** Delta tables,
# MAGIC mirroring the Netflix project's Autoloader pattern (1_Autoloader.ipynb).

# COMMAND ----------

dbutils.widgets.text("storage_account", "sqldwprojectkiran")
storage_account = dbutils.widgets.get("storage_account")

# COMMAND ----------

# MAGIC %sql
# MAGIC use catalog sql_datawarehouse;

# COMMAND ----------

# MAGIC %md
# MAGIC ### Source → Bronze table mapping
# MAGIC Each entry maps a folder in the `raw` container (populated by the ADF ForEach/Copy
# MAGIC activity) to its target Bronze Delta table (DDL already defined in `ddl_bronze_SQL`).

# COMMAND ----------

tables = [
    {"source_folder": "crm/cust_info",     "bronze_table": "bronze.crm_cust_info"},
    {"source_folder": "crm/prd_info",      "bronze_table": "bronze.crm_prd_info"},
    {"source_folder": "crm/sales_details", "bronze_table": "bronze.crm_sales_details"},
    {"source_folder": "erp/cust_az12",     "bronze_table": "bronze.erp_cust_az12"},
    {"source_folder": "erp/loc_a101",      "bronze_table": "bronze.erp_loc_a101"},
    {"source_folder": "erp/px_cat_g1v2",   "bronze_table": "bronze.erp_px_cat_g1v2"},
]

# COMMAND ----------

# MAGIC %md
# MAGIC ### Run Autoloader for each source
# MAGIC `trigger(availableNow=True)` processes all currently-available new files then stops —
# MAGIC ideal for a scheduled/orchestrated batch job (Databricks Workflow or ADF trigger),
# MAGIC as opposed to a continuously-running stream.

# COMMAND ----------

for t in tables:
    checkpoint_location = (
        f"abfss://bronze@{storage_account}.dfs.core.windows.net/"
        f"_checkpoints/{t['bronze_table']}"
    )
    raw_path = f"abfss://raw@{storage_account}.dfs.core.windows.net/{t['source_folder']}"

    print(f"Ingesting {raw_path}  ->  {t['bronze_table']}")

    (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("cloudFiles.schemaLocation", checkpoint_location)
        .option("header", "true")
        .option("inferSchema", "true")
        .load(raw_path)
        .writeStream.option("checkpointLocation", checkpoint_location)
        .trigger(availableNow=True)
        .toTable(t["bronze_table"])
    )

# COMMAND ----------

# MAGIC %md
# MAGIC ### Quality check — row counts landed in Bronze

# COMMAND ----------

for t in tables:
    cnt = spark.table(t["bronze_table"]).count()
    print(f"{t['bronze_table']:35s} {cnt:>8,} rows")
