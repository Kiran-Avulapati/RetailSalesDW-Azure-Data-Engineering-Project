# CRM + ERP Data Warehouse — Azure Medallion Pipeline

A retail data warehouse pipeline that ingests CRM and ERP source data through Azure Data
Factory, Databricks Autoloader, and Delta Live Tables into a Synapse-served star schema —
built with the same architecture as the Netflix batch pipeline, applied to a richer,
multi-source dataset.

## Why this dataset
Unlike a single flat source, this project integrates **two systems of record** (CRM +
ERP) that disagree on formats, keys, and even gender codes — giving the pipeline real
data-quality problems to solve: deduplication via `ROW_NUMBER()`, key reformatting,
category standardization, referential-integrity checks across sources, and surrogate-key
generation for a proper star schema (`dim_customers`, `dim_products`, `fact_sales`).

## Architecture

```
GitHub (source_crm/, source_erp/ CSVs)
        │
        ▼
Azure Data Factory  — Web (list files) → Set Variable → Validation → ForEach → Copy
        │
        ▼
ADLS Gen2  raw/crm/*, raw/erp/*
        │
        ▼
Databricks Autoloader (1_Autoloader_Bronze.py)  —  incremental, schema-tracked
        │
        ▼
Bronze  (sql_datawarehouse.bronze.*)  — raw fidelity, 1:1 with source
        │
        ▼
Silver transformation notebooks (2_Silver_01..06)
  • dedupe, trim, standardize codes, fix key formats, resolve invalid dates
        │
        ▼
Silver  (sql_datawarehouse.silver.*)  — clean, conformed, source-integrity-checked
        │
        ▼
Delta Live Tables (3_DLT_Gold_StarSchema.py)
  • dim_customers, dim_products, fact_sales
  • dlt.expect_all_or_drop — bad rows dropped + counted automatically
        │
        ▼
Gold  (sql_datawarehouse.gold.*)  — star schema, analytics-ready
        │
        ▼
Azure Synapse (Warehouse)  →  Reporting / BI
```

## Folder guide

| Path | Purpose |
|---|---|
| `datasets/source_crm/`, `datasets/source_erp/` | Source CSVs — push these to a public GitHub repo so ADF can pull them, same as the Netflix project. |
| `ADF/SqlDataWarehouse_Ingest_pipeline.json` | Template ADF pipeline: GitHub → ADLS `raw`, two parallel ForEach branches (CRM, ERP), then triggers the Databricks Autoloader job. Fill in `<your-username>/<your-repo>`, linked services, and dataset definitions in ADF Studio. |
| `Azure Databricks Notebooks/0_*` | Catalog/schema + Bronze/Silver DDL (unchanged from the original project). |
| `Azure Databricks Notebooks/1_Autoloader_Bronze.py` | Raw → Bronze, incremental, via `cloudFiles`. |
| `Azure Databricks Notebooks/2_Silver_01..06_*.py` | Your original cleansing logic per table (dedup, trims, standardization, FK checks), reformatted as importable Databricks notebooks. |
| `Azure Databricks Notebooks/3_DLT_Gold_StarSchema.py` | Silver → Gold star schema as a DLT pipeline with quality expectations, replacing the original static SQL views. |

## Setup notes
1. Push this repo (including `datasets/`) to GitHub — ADF's Web activity reads the
   GitHub Contents API to list files, then Copy activities pull each raw file into ADLS.
2. Create the `raw`, `bronze`, `silver` containers/schemas as in `0_init_catalog_schemas.py`.
3. Import the notebooks into Databricks (Repos or Workspace import), set the
   `storage_account` widget in `1_Autoloader_Bronze.py`.
4. Create a DLT pipeline pointing at `3_DLT_Gold_StarSchema.py`, target schema `gold`.
5. Wire up the ADF pipeline (fill in linked services/datasets), then orchestrate with a
   Databricks Workflow or ADF trigger: ADF ingest → Autoloader job → DLT pipeline update.
6. Point Synapse serverless/dedicated SQL pool at the Gold Delta tables for reporting.
