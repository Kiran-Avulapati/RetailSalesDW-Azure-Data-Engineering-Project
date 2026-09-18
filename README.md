# 🚀 RetailSalesDW-Azure-Data-Engineering-Project

<div align="center">

![Azure](https://img.shields.io/badge/Microsoft%20Azure-0078D4?style=for-the-badge&logo=microsoft-azure&logoColor=white)
![Data Factory](https://img.shields.io/badge/Azure%20Data%20Factory-0078D4?style=for-the-badge&logo=microsoftazure&logoColor=white)
![Databricks](https://img.shields.io/badge/Azure%20Databricks-FF3621?style=for-the-badge&logo=databricks&logoColor=white)
![PySpark](https://img.shields.io/badge/PySpark-E25A1C?style=for-the-badge&logo=apachespark&logoColor=white)
![Delta Lake](https://img.shields.io/badge/Delta%20Lake-00ADD8?style=for-the-badge)
![Python](https://img.shields.io/badge/Python-3776AB?style=for-the-badge&logo=python&logoColor=white)
![GitHub](https://img.shields.io/badge/GitHub-181717?style=for-the-badge&logo=github&logoColor=white)

**An end-to-end Azure Data Engineering pipeline integrating CRM and ERP data into an analytics-ready Data Warehouse**

[Overview](#-overview) •
[Architecture](#-architecture) •
[Pipeline](#-azure-data-factory-pipeline) •
[Data Layers](#-medallion-architecture) •
[Technologies](#-technologies-used) •
[Setup](#-setup)

</div>

---

## 📌 Overview

This project implements an end-to-end **CRM & ERP Data Warehouse** using Microsoft Azure.

Data from CRM and ERP source systems is extracted from GitHub and orchestrated through **Azure Data Factory**. The data is stored in **Azure Data Lake Storage Gen2**, incrementally processed using **Databricks Autoloader**, transformed with **PySpark**, and organized using the **Medallion Architecture**.

The final **Gold layer** is built using **Delta Live Tables (DLT)** and provides an analytics-ready **Star Schema** consisting of customer and product dimensions and a sales fact table.

### 🎯 Key Objectives

- ✅ Integrate CRM and ERP source systems
- ✅ Automate data ingestion using Azure Data Factory
- ✅ Store raw data in Azure Data Lake Storage Gen2
- ✅ Perform incremental ingestion using Databricks Autoloader
- ✅ Clean and transform data using PySpark
- ✅ Apply data quality and validation rules
- ✅ Integrate data across CRM and ERP systems
- ✅ Build an analytics-ready Gold Star Schema
- ✅ Implement Delta Live Tables for Gold-layer processing

---

# 🏗️ Architecture
<img width="1079" height="380" alt="image" src="https://github.com/user-attachments/assets/99d2d4b1-6d44-4566-baf0-ea561778b278" />

```text
┌──────────────────────────────────────────────────────────────┐
│                        SOURCE SYSTEMS                        │
│                                                              │
│              GitHub Repository - CSV Files                  │
│                                                              │
│       ┌─────────────────┐       ┌─────────────────┐         │
│       │      CRM        │       │      ERP        │         │
│       │ Customer        │       │ Customer        │         │
│       │ Product         │       │ Location        │         │
│       │ Sales           │       │ Product Category│         │
│       └────────┬────────┘       └────────┬────────┘         │
└────────────────┼──────────────────────────┼──────────────────┘
                 │                          │
                 └────────────┬─────────────┘
                              ▼
┌──────────────────────────────────────────────────────────────┐
│                    AZURE DATA FACTORY                       │
│                                                              │
│  Web Metadata → Set Variable → Validation → ForEach → Copy  │
│                                                              │
│                 CRM + ERP Ingestion                          │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                    AZURE DATA LAKE GEN2                     │
│                         RAW LAYER                            │
│                                                              │
│              CRM Files        ERP Files                     │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                     AZURE DATABRICKS                        │
│                                                              │
│                  Databricks Autoloader                      │
│                         ↓                                    │
│                       PySpark                                │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                         BRONZE                              │
│                                                              │
│                    Raw Ingested Data                         │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                         SILVER                              │
│                                                              │
│  Cleansing • Deduplication • Standardization • Validation   │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                  DELTA LIVE TABLES                          │
│                                                              │
│            Data Quality Expectations + Modeling              │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                           GOLD                              │
│                                                              │
│       dim_customers     dim_products     fact_sales          │
│                                                              │
│                    ⭐ STAR SCHEMA ⭐                         │
└──────────────────────────────┬───────────────────────────────┘
                               │
                               ▼
┌──────────────────────────────────────────────────────────────┐
│                     ANALYTICS / BI                          │
│                                                              │
│                   Reporting & Analysis                      │
└──────────────────────────────────────────────────────────────┘
```

---

# 🔄 Azure Data Factory Pipeline

Azure Data Factory handles the ingestion and orchestration of CRM and ERP source files.

## CRM Ingestion

```text
GithubMetadata_CRM
        │
        ▼
SetVariable_CRM_Files
        │
        ▼
ValidationGithub_CRM
        │
        ▼
ForAllCrmFiles
        │
        ▼
Copy_Github_CRM_File
```

## ERP Ingestion

```text
GithubMetadata_ERP
        │
        ▼
SetVariable_ERP_Files
        │
        ▼
ValidationGithub_ERP
        │
        ▼
ForAllErpFiles
        │
        ▼
Copy_Github_ERP_File
```

## Databricks Trigger

After CRM and ERP ingestion completes successfully:

```text
       CRM Ingestion ────────┐
                             ├──► Trigger_Databricks_Autoloader_Job
       ERP Ingestion ────────┘
```

This ensures the downstream Databricks processing starts only after the required source files have been ingested.

---

# 🥉 Medallion Architecture

## 🟤 Bronze Layer

The Bronze layer stores the source data after ingestion with minimal transformation.

### Bronze Tables

```text
bronze.crm_cust_info
bronze.crm_prd_info
bronze.crm_sales_details

bronze.erp_cust_az12
bronze.erp_loc_a101
bronze.erp_px_cat_g1v2
```

### Bronze Processing

- Databricks Autoloader
- `cloudFiles`
- Incremental file ingestion
- Checkpoint-based processing
- Source-to-table mapping

---

## 🥈 Silver Layer

The Silver layer performs data cleansing, standardization, transformation, and validation.

### CRM Customer

`2_Silver_01_crm_cust_info.py`

- Duplicate record handling
- Latest-record selection
- Null key filtering
- String trimming
- Gender standardization
- Marital-status standardization

### CRM Product

`2_Silver_02_crm_prd_info.py`

- Product key transformation
- Category key extraction
- Product cost validation
- Null-value handling
- Product-line standardization
- Date validation

### CRM Sales

`2_Silver_03_crm_sales_details.py`

- Product key validation
- Customer key validation
- Date conversion
- Invalid date handling
- Quantity validation
- Price validation
- Sales amount validation

Business rule:

```text
Sales Amount = Quantity × Price
```

### ERP Customer

`2_Silver_04_erp_cust_az12.py`

Processes ERP customer demographic information and standardizes customer attributes.

### ERP Location

`2_Silver_05_erp_loc_a101.py`

Processes customer location and country information.

### ERP Product Category

`2_Silver_06_erp_px_cat_g1v2.py`

Processes:

- Product categories
- Product subcategories
- Maintenance information
- Product-category relationships

---

# 🥇 Gold Layer

The Gold layer is implemented using **Delta Live Tables**.

Notebook:

```text
3_DLT_Gold_StarSchema.py
```

## ⭐ Star Schema

```text
                    ┌───────────────────┐
                    │   dim_customers   │
                    │───────────────────│
                    │ customer_key      │
                    │ customer_id       │
                    │ customer_name     │
                    │ gender            │
                    │ birth_date        │
                    │ country           │
                    └─────────┬─────────┘
                              │
                              │
                              ▼
                    ┌───────────────────┐
                    │    fact_sales     │
                    │───────────────────│
                    │ order_number      │
                    │ customer_key      │
                    │ product_key       │
                    │ order_date        │
                    │ shipping_date     │
                    │ due_date          │
                    │ sales_amount      │
                    │ quantity          │
                    │ price             │
                    └─────────┬─────────┘
                              │
                              │
                              ▼
                    ┌───────────────────┐
                    │   dim_products    │
                    │───────────────────│
                    │ product_key       │
                    │ product_id        │
                    │ product_name      │
                    │ category          │
                    │ subcategory       │
                    │ product_line      │
                    │ product_cost      │
                    └───────────────────┘
```

---

# 📊 Gold Tables

### `dim_customers`

Combines customer information from CRM and ERP systems.

Includes attributes such as:

- Customer ID
- Customer name
- Gender
- Birth date
- Country
- Marital status

A warehouse surrogate customer key is generated for analytical modeling.

### `dim_products`

Combines CRM product data with ERP category information.

Includes:

- Product ID
- Product name
- Product category
- Subcategory
- Product line
- Product cost

### `fact_sales`

Contains transactional sales information:

- Order number
- Customer key
- Product key
- Order date
- Shipping date
- Due date
- Sales amount
- Quantity
- Price

---

# 🛡️ Data Quality

Data quality is applied throughout the pipeline.

### Silver Quality Checks

- 🔍 Duplicate detection
- 🔍 Null validation
- 🔍 Primary-key validation
- 🔍 Date validation
- 🔍 Data standardization
- 🔍 Business-rule validation
- 🔍 Cross-source consistency

### Gold Quality Checks

Delta Live Tables expectations validate:

```text
✓ Customer IDs
✓ Customer Keys
✓ Product IDs
✓ Product Keys
✓ Order Numbers
✓ Sales Amounts
✓ Referential Integrity
```

---

# 📂 Project Structure

```text
CRM-ERP-Data-Warehouse/
│
├── ADF/
│   └── SqlDataWarehouse_Ingest_pipeline.json
│
├── Azure Databricks Notebooks/
│   │
│   ├── 0_init_catalog_schemas.py
│   ├── 0_ddl_bronze.py
│   ├── 0_ddl_silver.py
│   │
│   ├── 1_Autoloader_Bronze.py
│   │
│   ├── 2_Silver_01_crm_cust_info.py
│   ├── 2_Silver_02_crm_prd_info.py
│   ├── 2_Silver_03_crm_sales_details.py
│   ├── 2_Silver_04_erp_cust_az12.py
│   ├── 2_Silver_05_erp_loc_a101.py
│   ├── 2_Silver_06_erp_px_cat_g1v2.py
│   │
│   └── 3_DLT_Gold_StarSchema.py
│
├── datasets/
│   │
│   ├── source_crm/
│   │   ├── cust_info.csv
│   │   ├── prd_info.csv
│   │   └── sales_details.csv
│   │
│   └── source_erp/
│       ├── CUST_AZ12.csv
│       ├── LOC_A101.csv
│       └── PX_CAT_G1V2.csv
│
└── README.md
```

---

# 🛠️ Technologies Used

| Component | Technology | Purpose |
|-----------|------------|---------|
| ☁️ Cloud | Microsoft Azure | Cloud infrastructure |
| 🔄 Orchestration | Azure Data Factory | Data ingestion and workflow orchestration |
| 🗄️ Storage | Azure Data Lake Storage Gen2 | Data lake storage |
| ⚡ Processing | Azure Databricks | Distributed data processing |
| 🐍 Programming | Python / PySpark | Data transformation |
| 📥 Ingestion | Databricks Autoloader | Incremental file processing |
| 🧱 Storage Format | Delta Lake | Reliable lakehouse storage |
| 📊 Data Quality | Delta Live Tables | Quality rules and Gold processing |
| 🗃️ Modeling | Star Schema | Analytics-ready warehouse model |
| 🔧 Version Control | GitHub | Source and project management |

---

# 📥 Source Datasets

## CRM

```text
cust_info.csv
prd_info.csv
sales_details.csv
```

## ERP

```text
CUST_AZ12.csv
LOC_A101.csv
PX_CAT_G1V2.csv
```

The two systems are integrated during the Silver and Gold transformation stages.

---

# ⚙️ Setup

## 1. Clone the Repository

```bash
git clone https://github.com/<your-username>/<your-repository>.git
cd <your-repository>
```

## 2. Create Azure Resources

Required Azure resources:

- Azure Data Factory
- Azure Data Lake Storage Gen2
- Azure Databricks Workspace

## 3. Configure ADLS Gen2

Create the required storage paths for CRM and ERP raw data.

Example:

```text
raw/
├── crm/
│   ├── cust_info/
│   ├── prd_info/
│   └── sales_details/
│
└── erp/
    ├── cust_az12/
    ├── loc_a101/
    └── px_cat_g1v2/
```

## 4. Configure Azure Data Factory

Import/configure:

```text
ADF/
└── SqlDataWarehouse_Ingest_pipeline.json
```

Configure the required:

- GitHub connection
- ADLS Gen2 connection
- Databricks connection
- Pipeline parameters

## 5. Configure Databricks

Import the notebooks from:

```text
Azure Databricks Notebooks/
```

Initialize the catalog and schemas:

```text
0_init_catalog_schemas.py
```

Create Bronze tables:

```text
0_ddl_bronze.py
```

Create Silver tables:

```text
0_ddl_silver.py
```

## 6. Run the Pipeline

Trigger the Azure Data Factory pipeline.

The workflow then proceeds through:

```text
ADF
 ↓
ADLS Gen2
 ↓
Autoloader
 ↓
Bronze
 ↓
Silver
 ↓
DLT
 ↓
Gold
```

---

# 🔁 End-to-End Workflow

```text
             ┌──────────────┐
             │    GitHub    │
             └──────┬───────┘
                    │
                    ▼
          ┌──────────────────┐
          │ Azure Data Factory│
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │    ADLS Gen2     │
          │    Raw Layer     │
          └────────┬─────────┘
                   │
                   ▼
          ┌──────────────────┐
          │ Databricks       │
          │ Autoloader       │
          └────────┬─────────┘
                   │
                   ▼
             ┌──────────┐
             │  Bronze  │
             └────┬─────┘
                  │
                  ▼
             ┌──────────┐
             │  Silver  │
             └────┬─────┘
                  │
                  ▼
          ┌─────────────────┐
          │ Delta Live Tables│
          └────────┬────────┘
                   │
                   ▼
             ┌──────────┐
             │   Gold   │
             └────┬─────┘
                  │
                  ▼
          ┌─────────────────┐
          │ Analytics / BI  │
          └─────────────────┘
```

---

# 🚀 Key Features

| Feature | Description |
|---------|-------------|
| 🔄 Automated Ingestion | ADF orchestrates CRM and ERP ingestion |
| 📥 Incremental Processing | Autoloader processes newly available files |
| 🥉 Bronze Layer | Preserves ingested source data |
| 🥈 Silver Layer | Cleans and standardizes data |
| 🥇 Gold Layer | Provides analytics-ready dimensional data |
| 🔗 Data Integration | Combines CRM and ERP information |
| 🛡️ Data Quality | Applies validation and DLT expectations |
| ⭐ Star Schema | Supports analytical querying |
| 📈 Scalable Processing | Uses Databricks and PySpark |

---

# 🎓 Learning Outcomes

This project demonstrates practical experience with:

- Azure Data Engineering
- Azure Data Factory
- Azure Data Lake Storage Gen2
- Azure Databricks
- Databricks Autoloader
- PySpark
- Delta Lake
- Delta Live Tables
- Medallion Architecture
- ETL / ELT pipelines
- Data quality engineering
- Data warehouse modeling
- Star schema design
- CRM and ERP data integration
- Incremental data processing

---

# 🔮 Future Improvements

- 📊 Build Power BI dashboards on the Gold layer
- 🔔 Add pipeline failure notifications
- 🔄 Implement CI/CD deployment
- 🧪 Add automated data-quality reporting
- ⚙️ Add environment-specific configurations
- 📈 Add monitoring and operational dashboards

---

# 📜 License

This project is intended for educational and portfolio purposes.

---

<div align="center">

### 👨‍💻 Developed by **Kiran Avulapati**

**Azure Data Engineering • Databricks • PySpark • Data Warehousing**

⭐ **If you find this project useful, consider giving the repository a star!** ⭐

</div>
