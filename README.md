# 🚚 LogiClean

### Automated Logistics Data Cleaning & ETL Pipeline

**LogiClean** is a Python-based ETL and data-quality pipeline designed to turn messy logistics, shipment, and warehouse files into structured, analysis-ready data.

It automatically cleans, validates, standardizes, and reports problems in operational data from **CSV, Excel, and JSON files**.

The project is designed around real-world logistics workflows where data may come from different warehouses, customers, carriers, ERP exports, or spreadsheets with inconsistent formats.

---

## 🎯 What problem does it solve?

Logistics data is often messy:

* Different column names between files
* Duplicate shipments
* Missing SKUs
* Incorrect dates
* Inconsistent shipment statuses
* Negative or invalid quantities
* Different weight units
* Incorrect city or country formatting
* Missing warehouse information
* Multiple Excel sheets
* Different CSV encodings

LogiClean automatically processes these issues and produces clean, structured output.

---

## ⚙️ Main Features

### 📥 Multi-format input

Supports:

* CSV
* XLSX
* XLS
* JSON
* Multi-sheet Excel workbooks

---

### 🔍 Automatic data detection

LogiClean attempts to identify whether an uploaded dataset contains:

* **Shipment data**
* **Inventory data**

It then applies the appropriate cleaning rules automatically.

---

### 🧹 Data Cleaning & Standardization

The pipeline can standardize:

* Shipment IDs
* Order IDs
* SKUs
* Product names
* Customer information
* Phone numbers
* Dates
* Cities
* Countries
* Shipment statuses
* Quantities
* Weights
* Currencies
* Warehouse information

Example:

```text
deliverd → DELIVERED
dlvd → DELIVERED

in transit → IN_TRANSIT

alex → Alexandria

lbs → converted to KG
```

---

## 🔄 Flexible Column Mapping

Different companies often use different column names for the same information.

LogiClean recognizes aliases such as:

```text
shipment no
shipment id
shipment number
ship id
```

and maps them to:

```text
shipment_id
```

It does the same for inventory, customer, warehouse, quantity, product and other logistics fields.

---

## 🧠 Data Quality Checks

Every processed record receives a status:

```text
CLEAN
FIXED
NEEDS_REVIEW
```

Records with critical problems can also be rejected instead of silently entering the cleaned dataset.

Examples include:

* Missing shipment IDs
* Missing SKUs
* Invalid shipment dates
* Invalid quantities
* Unknown statuses
* Missing warehouse information

---

## ♻️ Duplicate Detection

LogiClean automatically detects duplicate records.

### Shipments

Duplicates are detected using:

```text
shipment_id
```

### Inventory

Duplicates are detected using:

```text
SKU + Warehouse
```

When multiple duplicates exist, the pipeline prioritizes the record containing the most complete information.

---

## 📊 Inventory Intelligence

Inventory records are automatically classified as:

```text
IN_STOCK
LOW_STOCK
OUT_OF_STOCK
UNKNOWN
```

using the current quantity and minimum-stock level where available.

---

## 📤 Generated Outputs

After processing the input files, LogiClean creates two Excel workbooks.

### `cleaned_data.xlsx`

Contains:

**Shipments**

Cleaned and standardized shipment records.

**Inventory**

Cleaned and standardized warehouse/inventory records.

---

### `repair_report.xlsx`

Contains three sheets:

#### Summary

Shows metrics such as:

* Total files processed
* Total rows processed
* Accepted records
* Rejected records
* Duplicate records removed
* Clean records
* Automatically fixed records
* Records requiring review
* Total issues detected
* Overall data-quality score

#### Issue Log

Records detected problems including:

* Source file
* Sheet
* Row
* Field
* Original value
* Problem detected
* Action taken
* Corrected value

#### Rejected Records

Keeps records that could not safely be processed so they can be manually reviewed.

---

## 🏗️ Pipeline Flow

```text
CSV / Excel / JSON
        ↓
Load Files
        ↓
Detect Dataset Type
        ↓
Map Column Names
        ↓
Validate Records
        ↓
Clean & Standardize
        ↓
Remove Duplicates
        ↓
Classify Data Quality
        ↓
Generate Clean Dataset
        ↓
Generate Repair Report
```

---

## 🚀 Installation

Clone the repository:

```bash
git clone https://github.com/Aumar-mahmud/logiclean.git
cd logiclean
```

Install the dependencies:

```bash
pip install -r requirements.txt
```

Current dependencies:

```text
pandas
openpyxl
```

---

## 📁 Input Files

Place your files inside:

```text
data/input/
```

Example:

```text
data/
└── input/
    ├── shipments.csv
    ├── warehouse.xlsx
    └── inventory.json
```

Then run:

```bash
python main.py
```

---

## 📁 Output

The pipeline creates:

```text
data/
└── output/
    ├── cleaned_data.xlsx
    └── repair_report.xlsx
```

---

## 🛠️ Technologies

* Python
* Pandas
* OpenPyXL
* ETL
* Data Cleaning
* Data Validation
* Logistics Data Processing
* Supply Chain Analytics

---

## 💼 Business Use Cases

LogiClean can be useful for:

* Freight forwarders
* Fulfillment companies
* Warehouses
* E-commerce logistics
* Inventory teams
* Supply-chain analysts
* ERP/WMS data preparation
* Recurring Excel/CSV processing
* Operational reporting

---

## 🗺️ Future Development

Planned improvements include:

* 🌐 Browser-based file upload
* ☁️ Cloud deployment
* 📊 Interactive logistics dashboard
* 🔗 Google Drive integration
* 📈 Automatic operational KPIs
* 🧩 Additional logistics-data modules
* ⚙️ User-configurable cleaning rules

---

## 👤 Author

**Aumar Ghreeb Ahmed Mahmud**

Management Information Systems graduate focused on logistics, data analytics and process automation.

**LinkedIn:**
linkedin.com/in/aumar-mahmud-3221a4438

**GitHub:**
github.com/Aumar-mahmud

