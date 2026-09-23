from __future__ import annotations

import json
import re
from pathlib import Path

import pandas as pd


BASE_DIR = Path(__file__).resolve().parent
INPUT_DIR = BASE_DIR / "data" / "input"
OUTPUT_DIR = BASE_DIR / "data" / "output"

ISSUE_LOG = []
REJECTED_RECORDS = []


# --------------------------------------------------
# Header aliases
# --------------------------------------------------

def normalize_text_key(text: str) -> str:
    return re.sub(r"[^a-z0-9]+", " ", str(text).lower()).strip()


SHIPMENT_ALIAS_RAW = {
    "shipment no": "shipment_id",
    "shipment id": "shipment_id",
    "shipment number": "shipment_id",
    "shipment_id": "shipment_id",
    "ship id": "shipment_id",
    "order id": "order_id",
    "order no": "order_id",
    "order number": "order_id",
    "cust name": "customer_name",
    "customer": "customer_name",
    "customer name": "customer_name",
    "receiver": "customer_name",
    "mobile": "phone",
    "phone": "phone",
    "phone number": "phone",
    "email": "email",
    "address": "address",
    "qty": "quantity",
    "quantity": "quantity",
    "dt": "ship_date",
    "date": "ship_date",
    "ship date": "ship_date",
    "shipment date": "ship_date",
    "delivery date": "delivery_date",
    "dest": "city",
    "destination": "city",
    "city": "city",
    "country": "country",
    "status": "status",
    "order status": "status",
    "order_status": "status",
    "carrier": "carrier",
    "weight": "weight",
    "unit": "unit",
    "amount": "amount",
    "value": "amount",
    "currency": "currency",
    "sku": "sku",
    "item": "product_name",
    "product": "product_name",
    "product name": "product_name",
}

INVENTORY_ALIAS_RAW = {
    "sku": "sku",
    "item code": "sku",
    "product code": "sku",
    "code": "sku",
    "item": "product_name",
    "product": "product_name",
    "product name": "product_name",
    "qty": "quantity",
    "quantity": "quantity",
    "stock": "quantity",
    "on hand": "quantity",
    "wh": "warehouse",
    "warehouse": "warehouse",
    "location": "warehouse",
    "branch": "warehouse",
    "updated": "last_updated",
    "last updated": "last_updated",
    "update date": "last_updated",
    "date": "last_updated",
    "supplier": "supplier",
    "min stock level": "min_stock_level",
    "minimum stock": "min_stock_level",
    "unit": "unit",
}

SHIPMENT_ALIASES = {normalize_text_key(k): v for k, v in SHIPMENT_ALIAS_RAW.items()}
INVENTORY_ALIASES = {normalize_text_key(k): v for k, v in INVENTORY_ALIAS_RAW.items()}


# --------------------------------------------------
# Standard mappings
# --------------------------------------------------

STATUS_MAP = {
    "delivered": "DELIVERED",
    "deliverd": "DELIVERED",
    "dlvd": "DELIVERED",
    "shipped": "SHIPPED",
    "ship": "SHIPPED",
    "in transit": "IN_TRANSIT",
    "transit": "IN_TRANSIT",
    "out for delivery": "IN_TRANSIT",
    "pending": "PENDING",
    "processing": "PROCESSING",
    "prepared": "PROCESSING",
    "cancelled": "CANCELLED",
    "canceled": "CANCELLED",
    "returned": "RETURNED",
    "return": "RETURNED",
    "on hold": "ON_HOLD",
    "hold": "ON_HOLD",
    "unknown status": "ON_HOLD",
    "unknown": "ON_HOLD",
}

CITY_MAP = {
    "cairo": "Cairo",
    "el qahera": "Cairo",
    "cairo eg": "Cairo",
    "cairo egypt": "Cairo",
    "alexandria": "Alexandria",
    "alex": "Alexandria",
    "al alexandriyah": "Alexandria",
    "giza": "Giza",
    "suez": "Suez",
    "port said": "Port Said",
}

CURRENCY_MAP = {
    "EGP": "EGP",
    "E£": "EGP",
    "£EG": "EGP",
    "EGP£": "EGP",
    "USD": "USD",
    "$": "USD",
    "US$": "USD",
    "EUR": "EUR",
    "€": "EUR",
}

UNIT_MAP = {
    "kg": "KG",
    "kilogram": "KG",
    "kilograms": "KG",
    "kgs": "KG",
    "lb": "LB",
    "lbs": "LB",
    "pound": "LB",
    "pounds": "LB",
}

SHIPMENT_OUTPUT_COLUMNS = [
    "shipment_id",
    "order_id",
    "customer_name",
    "phone",
    "email",
    "address",
    "city",
    "country",
    "sku",
    "product_name",
    "quantity",
    "weight_kg",
    "ship_date",
    "delivery_date",
    "carrier",
    "status",
    "amount",
    "currency",
    "source_file",
    "source_sheet",
    "row_number",
    "clean_status",
]

INVENTORY_OUTPUT_COLUMNS = [
    "sku",
    "product_name",
    "warehouse",
    "quantity",
    "unit",
    "last_updated",
    "supplier",
    "min_stock_level",
    "stock_status",
    "source_file",
    "source_sheet",
    "row_number",
    "clean_status",
]


# --------------------------------------------------
# Utility functions
# --------------------------------------------------

def clean_text(value) -> str:
    if value is None:
        return ""
    if not isinstance(value, (list, dict)):
        try:
            if pd.isna(value):
                return ""
        except Exception:
            pass
    return re.sub(r"\s+", " ", str(value)).strip()


def to_serializable(row: dict) -> str:
    return json.dumps(row, default=str, ensure_ascii=False)


def add_issue(
    entity: str,
    source_file: str,
    source_sheet: str,
    row_number,
    field: str,
    original_value,
    issue: str,
    action: str,
    fixed_value,
):
    ISSUE_LOG.append(
        {
            "entity": entity,
            "source_file": source_file,
            "source_sheet": source_sheet,
            "row_number": row_number,
            "field": field,
            "original_value": original_value,
            "issue": issue,
            "action": action,
            "fixed_value": fixed_value,
        }
    )


def add_rejected(
    entity: str,
    source_file: str,
    source_sheet: str,
    row_number,
    reason: str,
    raw_row: dict,
):
    REJECTED_RECORDS.append(
        {
            "entity": entity,
            "source_file": source_file,
            "source_sheet": source_sheet,
            "row_number": row_number,
            "reason": reason,
            "raw_data": to_serializable(raw_row),
        }
    )


# --------------------------------------------------
# Entity detection and schema mapping
# --------------------------------------------------

def detect_entity(df: pd.DataFrame) -> str:
    norm_cols = [normalize_text_key(c) for c in df.columns]

    if any(SHIPMENT_ALIASES.get(nc) == "shipment_id" for nc in norm_cols):
        return "shipments"

    if any(INVENTORY_ALIASES.get(nc) == "sku" for nc in norm_cols):
        return "inventory"

    ship_score = sum(1 for nc in norm_cols if nc in SHIPMENT_ALIASES)
    inv_score = sum(1 for nc in norm_cols if nc in INVENTORY_ALIASES)

    if ship_score > inv_score:
        return "shipments"
    if inv_score > ship_score:
        return "inventory"

    return "unknown"


def map_columns(df: pd.DataFrame, entity: str) -> pd.DataFrame:
    if entity == "shipments":
        aliases = SHIPMENT_ALIASES
    elif entity == "inventory":
        aliases = INVENTORY_ALIASES
    else:
        aliases = {}

    mapping = {}
    for col in df.columns:
        if str(col).startswith("_"):
            continue
        key = normalize_text_key(col)
        if key in aliases:
            target = aliases[key]
            if target not in mapping.values():
                mapping[col] = target

    return df.rename(columns=mapping)


# --------------------------------------------------
# Field normalizers
# --------------------------------------------------

def normalize_phone(value):
    raw = clean_text(value)
    if not raw:
        return None, "missing"

    digits = re.sub(r"\D", "", raw)
    if not digits:
        return None, "invalid"

    if digits.startswith("00"):
        digits = digits[2:]

    if digits.startswith("20") and len(digits) == 12:
        return "+" + digits, "clean" if raw == "+" + digits else "fixed"

    if digits.startswith("0") and len(digits) == 11:
        return "+20" + digits[1:], "fixed"

    if digits.startswith("1") and len(digits) == 10:
        return "+20" + digits, "fixed"

    if 10 <= len(digits) <= 15:
        return "+" + digits, "fixed"

    return None, "invalid"


def normalize_date(value):
    if value is None:
        return None, "missing"

    if not isinstance(value, (list, dict)):
        try:
            if pd.isna(value):
                return None, "missing"
        except Exception:
            pass

    if isinstance(value, (int, float)) and 20000 < float(value) < 80000:
        try:
            parsed = pd.Timestamp("1899-12-30") + pd.Timedelta(days=int(value))
            return parsed.date(), "fixed"
        except Exception:
            pass

    raw = clean_text(value)
    if not raw:
        return None, "missing"

    parsed = pd.to_datetime(raw, errors="coerce")

    if pd.isna(parsed):
        for fmt in ("%d-%m-%Y", "%d/%m/%Y", "%Y-%m-%d", "%d-%b-%Y", "%b %d %Y", "%Y/%m/%d"):
            try:
                parsed_fmt = pd.to_datetime(raw, format=fmt, errors="coerce")
                if not pd.isna(parsed_fmt):
                    parsed = parsed_fmt
                    break
            except Exception:
                continue

    if pd.isna(parsed):
        return None, "invalid"

    return parsed.date(), "clean"


def normalize_number(value):
    raw = clean_text(value)
    if not raw:
        return None, "missing"

    raw = raw.replace(",", "").replace(" ", "")
    try:
        return float(raw), "clean"
    except Exception:
        return None, "invalid"


def normalize_quantity(value):
    number, status = normalize_number(value)
    if number is None:
        return None, status

    if number < 0:
        return 0, "negative"

    return int(round(number)), "clean"


def normalize_status(value):
    raw = clean_text(value)
    if not raw:
        return "PENDING", "missing"

    key = normalize_text_key(raw)
    mapped = STATUS_MAP.get(key)

    if mapped:
        return mapped, "clean" if raw.upper() == mapped else "fixed"

    return "ON_HOLD", "unknown"


def normalize_city(value):
    raw = clean_text(value)
    if not raw:
        return None, "missing"

    key = normalize_text_key(raw)
    mapped = CITY_MAP.get(key, raw.title())

    return mapped, "clean" if raw == mapped else "fixed"


def normalize_country(value):
    raw = clean_text(value)
    if not raw:
        return "Egypt", "fixed"

    return raw.title(), "clean"


def normalize_sku(value):
    raw = clean_text(value)
    if not raw:
        return None, "missing"

    s = raw.upper()
    s = re.sub(r"[\s_]+", "-", s)
    s = re.sub(r"-+", "-", s).strip("-")
    s = re.sub(r"([A-Z]+)(\d+)$", r"\1-\2", s)

    return s, "clean" if s == raw else "fixed"


def normalize_weight(weight_value, unit_value):
    weight, status = normalize_number(weight_value)
    if weight is None:
        return None, status

    unit_raw = clean_text(unit_value)
    unit_key = normalize_text_key(unit_raw)
    unit_std = UNIT_MAP.get(unit_key, "KG")

    changed = status != "clean" or unit_std == "LB" or unit_raw != ""

    if unit_std == "LB":
        weight *= 0.453592

    return round(weight, 3), "fixed" if changed else "clean"


def normalize_currency(value):
    raw = clean_text(value)
    if not raw:
        return None, "missing"

    key = raw.upper()
    mapped = CURRENCY_MAP.get(key, key if len(key) == 3 else raw.upper())

    return mapped, "clean" if mapped == raw.upper() else "fixed"


# --------------------------------------------------
# Row cleaners
# --------------------------------------------------

def clean_shipment_row(row: dict, source_file: str, sheet: str, row_number):
    raw_for_reject = {k: v for k, v in row.items() if not str(k).startswith("_")}

    fixed = False
    review = False

    out = {
        "source_file": source_file,
        "source_sheet": sheet,
        "row_number": row_number,
    }

    # shipment_id
    shipment_id = clean_text(row.get("shipment_id"))
    if not shipment_id:
        add_issue(
            "shipment",
            source_file,
            sheet,
            row_number,
            "shipment_id",
            row.get("shipment_id"),
            "Missing shipment_id",
            "Rejected",
            "",
        )
        add_rejected(
            "shipment",
            source_file,
            sheet,
            row_number,
            "Missing shipment_id",
            raw_for_reject,
        )
        return None

    out["shipment_id"] = shipment_id
    out["order_id"] = clean_text(row.get("order_id")) or None

    # customer name
    customer_name = clean_text(row.get("customer_name"))
    if not customer_name:
        review = True
        add_issue(
            "shipment",
            source_file,
            sheet,
            row_number,
            "customer_name",
            row.get("customer_name"),
            "Missing customer_name",
            "Kept blank",
            "",
        )
    out["customer_name"] = customer_name or None

    # phone
    if "phone" in row:
        phone, phone_status = normalize_phone(row.get("phone"))
        if phone_status == "missing":
            review = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "phone",
                row.get("phone"),
                "Missing phone",
                "Kept blank",
                "",
            )
        elif phone_status == "invalid":
            review = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "phone",
                row.get("phone"),
                "Invalid phone",
                "Set blank",
                "",
            )
            phone = None
        elif phone_status == "fixed":
            fixed = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "phone",
                row.get("phone"),
                "Phone normalized",
                "Standardized",
                phone,
            )
        out["phone"] = phone
    else:
        out["phone"] = None

    out["email"] = clean_text(row.get("email")) or None
    out["address"] = clean_text(row.get("address")) or None

    # city
    if "city" in row:
        city, city_status = normalize_city(row.get("city"))
        if city_status == "missing":
            review = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "city",
                row.get("city"),
                "Missing city",
                "Kept blank",
                "",
            )
        elif city_status == "fixed":
            fixed = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "city",
                row.get("city"),
                "City normalized",
                "Standardized",
                city,
            )
        out["city"] = city
    else:
        out["city"] = None

    # country
    country_raw = row.get("country") if "country" in row else None
    country, country_status = normalize_country(country_raw)
    if "country" in row and not clean_text(country_raw):
        fixed = True
        add_issue(
            "shipment",
            source_file,
            sheet,
            row_number,
            "country",
            country_raw,
            "Missing country",
            "Filled Egypt",
            country,
        )
    out["country"] = country

    # SKU
    if "sku" in row:
        sku, sku_status = normalize_sku(row.get("sku"))
        if sku_status == "missing":
            review = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "sku",
                row.get("sku"),
                "Missing SKU",
                "Kept blank",
                "",
            )
        elif sku_status == "fixed":
            fixed = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "sku",
                row.get("sku"),
                "SKU normalized",
                "Standardized",
                sku,
            )
        out["sku"] = sku
    else:
        out["sku"] = None

    out["product_name"] = clean_text(row.get("product_name")) or None

    # quantity
    quantity, quantity_status = normalize_quantity(row.get("quantity"))
    if quantity_status in ("missing", "invalid"):
        add_issue(
            "shipment",
            source_file,
            sheet,
            row_number,
            "quantity",
            row.get("quantity"),
            "Missing or invalid quantity",
            "Rejected",
            "",
        )
        add_rejected(
            "shipment",
            source_file,
            sheet,
            row_number,
            "Missing or invalid quantity",
            raw_for_reject,
        )
        return None

    if quantity_status == "negative":
        fixed = True
        add_issue(
            "shipment",
            source_file,
            sheet,
            row_number,
            "quantity",
            row.get("quantity"),
            "Negative quantity",
            "Set to 0",
            quantity,
        )

    out["quantity"] = quantity

    # weight
    if "weight" in row or "unit" in row:
        weight, weight_status = normalize_weight(row.get("weight"), row.get("unit"))
        if weight_status == "invalid":
            review = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "weight",
                row.get("weight"),
                "Invalid weight",
                "Set blank",
                "",
            )
            weight = None
        elif weight_status == "fixed":
            fixed = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "weight",
                row.get("weight"),
                "Weight normalized",
                "Converted to kg",
                weight,
            )
        out["weight_kg"] = weight
    else:
        out["weight_kg"] = None

    # ship date
    ship_date, ship_date_status = normalize_date(row.get("ship_date"))
    if ship_date_status in ("missing", "invalid"):
        add_issue(
            "shipment",
            source_file,
            sheet,
            row_number,
            "ship_date",
            row.get("ship_date"),
            "Missing or invalid ship_date",
            "Rejected",
            "",
        )
        add_rejected(
            "shipment",
            source_file,
            sheet,
            row_number,
            "Missing or invalid ship_date",
            raw_for_reject,
        )
        return None

    if ship_date_status == "fixed":
        fixed = True
        add_issue(
            "shipment",
            source_file,
            sheet,
            row_number,
            "ship_date",
            row.get("ship_date"),
            "Date normalized",
            "Parsed",
            ship_date,
        )

    out["ship_date"] = ship_date

    # delivery date
    if "delivery_date" in row:
        delivery_date, delivery_status = normalize_date(row.get("delivery_date"))
        if delivery_status == "invalid":
            review = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "delivery_date",
                row.get("delivery_date"),
                "Invalid delivery_date",
                "Set blank",
                "",
            )
            delivery_date = None
        elif delivery_status == "fixed":
            fixed = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "delivery_date",
                row.get("delivery_date"),
                "Delivery date normalized",
                "Parsed",
                delivery_date,
            )
        out["delivery_date"] = delivery_date
    else:
        out["delivery_date"] = None

    out["carrier"] = clean_text(row.get("carrier")) or None

    # status
    status, status_status = normalize_status(row.get("status"))
    if status_status in ("missing", "unknown"):
        review = True
        add_issue(
            "shipment",
            source_file,
            sheet,
            row_number,
            "status",
            row.get("status"),
            "Missing or unknown status",
            f"Mapped to {status}",
            status,
        )
    elif status_status == "fixed":
        fixed = True
        add_issue(
            "shipment",
            source_file,
            sheet,
            row_number,
            "status",
            row.get("status"),
            "Status normalized",
            "Mapped",
            status,
        )
    out["status"] = status

    # amount
    if "amount" in row:
        amount, amount_status = normalize_number(row.get("amount"))
        if amount_status == "invalid":
            review = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "amount",
                row.get("amount"),
                "Invalid amount",
                "Set blank",
                "",
            )
            amount = None
        out["amount"] = amount
    else:
        out["amount"] = None

    # currency
    if "currency" in row:
        currency, currency_status = normalize_currency(row.get("currency"))
        if currency_status == "fixed":
            fixed = True
            add_issue(
                "shipment",
                source_file,
                sheet,
                row_number,
                "currency",
                row.get("currency"),
                "Currency normalized",
                "Standardized",
                currency,
            )
        out["currency"] = currency
    else:
        out["currency"] = None

    if review:
        out["clean_status"] = "NEEDS_REVIEW"
    elif fixed:
        out["clean_status"] = "FIXED"
    else:
        out["clean_status"] = "CLEAN"

    return out


def clean_inventory_row(row: dict, source_file: str, sheet: str, row_number):
    raw_for_reject = {k: v for k, v in row.items() if not str(k).startswith("_")}

    fixed = False
    review = False

    out = {
        "source_file": source_file,
        "source_sheet": sheet,
        "row_number": row_number,
    }

    # SKU
    if "sku" in row:
        sku, sku_status = normalize_sku(row.get("sku"))
        if sku_status == "missing":
            add_issue(
                "inventory",
                source_file,
                sheet,
                row_number,
                "sku",
                row.get("sku"),
                "Missing SKU",
                "Rejected",
                "",
            )
            add_rejected(
                "inventory",
                source_file,
                sheet,
                row_number,
                "Missing SKU",
                raw_for_reject,
            )
            return None

        if sku_status == "fixed":
            fixed = True
            add_issue(
                "inventory",
                source_file,
                sheet,
                row_number,
                "sku",
                row.get("sku"),
                "SKU normalized",
                "Standardized",
                sku,
            )

        out["sku"] = sku
    else:
        add_issue(
            "inventory",
            source_file,
            sheet,
            row_number,
            "sku",
            "",
            "Missing SKU column/value",
            "Rejected",
            "",
        )
        add_rejected(
            "inventory",
            source_file,
            sheet,
            row_number,
            "Missing SKU",
            raw_for_reject,
        )
        return None

    # product name
    product_name = clean_text(row.get("product_name"))
    if not product_name:
        review = True
        add_issue(
            "inventory",
            source_file,
            sheet,
            row_number,
            "product_name",
            row.get("product_name"),
            "Missing product_name",
            "Kept blank",
            "",
        )
    out["product_name"] = product_name or None

    # warehouse
    warehouse = clean_text(row.get("warehouse"))
    if not warehouse:
        review = True
        add_issue(
            "inventory",
            source_file,
            sheet,
            row_number,
            "warehouse",
            row.get("warehouse"),
            "Missing warehouse",
            "Kept blank",
            "",
        )
    out["warehouse"] = warehouse or None

    # quantity
    if "quantity" in row:
        quantity, quantity_status = normalize_quantity(row.get("quantity"))
        if quantity_status in ("missing", "invalid"):
            review = True
            add_issue(
                "inventory",
                source_file,
                sheet,
                row_number,
                "quantity",
                row.get("quantity"),
                "Missing or invalid quantity",
                "Set blank",
                "",
            )
            quantity = None
        elif quantity_status == "negative":
            fixed = True
            add_issue(
                "inventory",
                source_file,
                sheet,
                row_number,
                "quantity",
                row.get("quantity"),
                "Negative quantity",
                "Set to 0",
                quantity,
            )
        out["quantity"] = quantity
    else:
        review = True
        out["quantity"] = None
        add_issue(
            "inventory",
            source_file,
            sheet,
            row_number,
            "quantity",
            "",
            "Missing quantity column/value",
            "Set blank",
            "",
        )

    # unit
    out["unit"] = clean_text(row.get("unit")) or None

    # last updated
    if "last_updated" in row:
        last_updated, date_status = normalize_date(row.get("last_updated"))
        if date_status in ("missing", "invalid"):
            review = True
            add_issue(
                "inventory",
                source_file,
                sheet,
                row_number,
                "last_updated",
                row.get("last_updated"),
                "Missing or invalid last_updated",
                "Set blank",
                "",
            )
            last_updated = None
        elif date_status == "fixed":
            fixed = True
            add_issue(
                "inventory",
                source_file,
                sheet,
                row_number,
                "last_updated",
                row.get("last_updated"),
                "Date normalized",
                "Parsed",
                last_updated,
            )
        out["last_updated"] = last_updated
    else:
        review = True
        out["last_updated"] = None
        add_issue(
            "inventory",
            source_file,
            sheet,
            row_number,
            "last_updated",
            "",
            "Missing last_updated column/value",
            "Set blank",
            "",
        )

    # supplier
    out["supplier"] = clean_text(row.get("supplier")) or None

    # min stock level
    if "min_stock_level" in row:
        min_stock, min_stock_status = normalize_quantity(row.get("min_stock_level"))
        if min_stock_status == "invalid":
            review = True
            add_issue(
                "inventory",
                source_file,
                sheet,
                row_number,
                "min_stock_level",
                row.get("min_stock_level"),
                "Invalid min_stock_level",
                "Set blank",
                "",
            )
            min_stock = None
        out["min_stock_level"] = min_stock
    else:
        out["min_stock_level"] = None

    # stock status
    quantity = out.get("quantity")
    min_stock = out.get("min_stock_level")

    if quantity is None:
        stock_status = "UNKNOWN"
    elif quantity == 0:
        stock_status = "OUT_OF_STOCK"
    elif min_stock is not None and quantity <= min_stock:
        stock_status = "LOW_STOCK"
    else:
        stock_status = "IN_STOCK"

    out["stock_status"] = stock_status

    if review:
        out["clean_status"] = "NEEDS_REVIEW"
    elif fixed:
        out["clean_status"] = "FIXED"
    else:
        out["clean_status"] = "CLEAN"

    return out


# --------------------------------------------------
# File loading
# --------------------------------------------------

def load_file(path: Path):
    frames = []
    suffix = path.suffix.lower()

    if suffix == ".csv":
        df = None
        for encoding in ["utf-8-sig", "utf-8", "cp1256", "latin-1"]:
            try:
                df = pd.read_csv(path, encoding=encoding)
                break
            except Exception:
                continue

        if df is not None:
            df["_source_file"] = path.name
            df["_sheet"] = ""
            frames.append(df)
        else:
            add_issue(
                "file",
                path.name,
                "",
                "",
                "file",
                path.name,
                "Could not read CSV file",
                "Skipped",
                "",
            )

    elif suffix in (".xlsx", ".xls"):
        try:
            sheets = pd.read_excel(path, sheet_name=None)
            for sheet_name, df in sheets.items():
                df["_source_file"] = path.name
                df["_sheet"] = sheet_name
                frames.append(df)
        except Exception as e:
            add_issue(
                "file",
                path.name,
                "",
                "",
                "file",
                path.name,
                f"Could not read Excel file: {e}",
                "Skipped",
                "",
            )

    elif suffix == ".json":
        try:
            try:
                df = pd.read_json(path)
            except ValueError:
                data = json.loads(path.read_text(encoding="utf-8"))
                if isinstance(data, list):
                    df = pd.json_normalize(data)
                else:
                    df = pd.json_normalize([data])

            df["_source_file"] = path.name
            df["_sheet"] = ""
            frames.append(df)
        except Exception as e:
            add_issue(
                "file",
                path.name,
                "",
                "",
                "file",
                path.name,
                f"Could not read JSON file: {e}",
                "Skipped",
                "",
            )

    else:
        add_issue(
            "file",
            path.name,
            "",
            "",
            "file",
            path.name,
            "Unsupported file type",
            "Skipped",
            "",
        )

    return frames


# --------------------------------------------------
# Deduplication
# --------------------------------------------------

def deduplicate(df: pd.DataFrame, entity: str, key_columns):
    if df.empty:
        return df, 0

    df = df.copy()
    df["_completeness"] = df.notna().sum(axis=1)
    df = df.sort_values("_completeness", ascending=False)

    dup_mask = df.duplicated(subset=key_columns, keep="first")

    for _, r in df[dup_mask].iterrows():
        add_issue(
            entity,
            r.get("source_file", ""),
            r.get("source_sheet", ""),
            r.get("row_number", ""),
            ", ".join(key_columns),
            {k: r.get(k) for k in key_columns},
            "Duplicate record",
            "Removed duplicate",
            "",
        )

    removed = int(dup_mask.sum())
    df = df[~dup_mask].drop(columns=["_completeness"])

    return df, removed


def ensure_columns(df: pd.DataFrame, columns):
    df = df.copy()
    for col in columns:
        if col not in df.columns:
            df[col] = None
    return df[columns]


# --------------------------------------------------
# Main pipeline
# --------------------------------------------------

def run_pipeline(input_dir=INPUT_DIR, output_dir=OUTPUT_DIR):
    input_dir = Path(input_dir)
    output_dir = Path(output_dir)
    output_dir.mkdir(parents=True, exist_ok=True)

    ISSUE_LOG.clear()
    REJECTED_RECORDS.clear()

    if not input_dir.exists():
        add_issue(
            "pipeline",
            "",
            "",
            "",
            "input_folder",
            str(input_dir),
            "Input folder does not exist",
            "Stopped",
            "",
        )
        return

    files = sorted(
        [
            p
            for p in input_dir.iterdir()
            if p.is_file() and p.suffix.lower() in (".csv", ".xlsx", ".xls", ".json")
        ]
    )

    if not files:
        add_issue(
            "pipeline",
            "",
            "",
            "",
            "input_folder",
            str(input_dir),
            "No input files found",
            "Stopped",
            "",
        )

    shipment_records = []
    inventory_records = []

    loaded_shipments = 0
    loaded_inventory = 0

    for path in files:
        frames = load_file(path)

        for df in frames:
            entity = detect_entity(df)
            mapped_df = map_columns(df, entity)

            if entity == "shipments":
                for idx, row in mapped_df.iterrows():
                    loaded_shipments += 1
                    rec = clean_shipment_row(
                        row.to_dict(),
                        row.get("_source_file", path.name),
                        row.get("_sheet", ""),
                        idx + 2,
                    )
                    if rec:
                        shipment_records.append(rec)

            elif entity == "inventory":
                for idx, row in mapped_df.iterrows():
                    loaded_inventory += 1
                    rec = clean_inventory_row(
                        row.to_dict(),
                        row.get("_source_file", path.name),
                        row.get("_sheet", ""),
                        idx + 2,
                    )
                    if rec:
                        inventory_records.append(rec)

            else:
                sheet = df["_sheet"].iloc[0] if "_sheet" in df.columns and len(df) > 0 else ""
                add_issue(
                    "file",
                    path.name,
                    sheet,
                    "",
                    "schema",
                    list(map(str, df.columns[:15])),
                    "Unknown entity/schema",
                    "Skipped rows",
                    "",
                )

    shipments_df = pd.DataFrame(shipment_records)
    inventory_df = pd.DataFrame(inventory_records)

    if not shipments_df.empty:
        shipments_df, shipment_duplicates_removed = deduplicate(
            shipments_df,
            "shipment",
            ["shipment_id"],
        )
    else:
        shipment_duplicates_removed = 0

    if not inventory_df.empty:
        inventory_df, inventory_duplicates_removed = deduplicate(
            inventory_df,
            "inventory",
            ["sku", "warehouse"],
        )
    else:
        inventory_duplicates_removed = 0

    shipments_df = ensure_columns(shipments_df, SHIPMENT_OUTPUT_COLUMNS)
    inventory_df = ensure_columns(inventory_df, INVENTORY_OUTPUT_COLUMNS)

    # --------------------------------------------------
    # Write cleaned output
    # --------------------------------------------------
    cleaned_path = output_dir / "cleaned_data.xlsx"

    with pd.ExcelWriter(cleaned_path, engine="openpyxl") as writer:
        shipments_df.to_excel(writer, sheet_name="Shipments", index=False)
        inventory_df.to_excel(writer, sheet_name="Inventory", index=False)

    # --------------------------------------------------
    # Build report
    # --------------------------------------------------
    rejected_shipments = len([r for r in REJECTED_RECORDS if r["entity"] == "shipment"])
    rejected_inventory = len([r for r in REJECTED_RECORDS if r["entity"] == "inventory"])

    total_rows = loaded_shipments + loaded_inventory
    accepted_rows = len(shipments_df) + len(inventory_df)
    rejected_rows = rejected_shipments + rejected_inventory
    duplicates_removed = shipment_duplicates_removed + inventory_duplicates_removed

    quality_score = round((accepted_rows / total_rows * 100), 1) if total_rows else 100.0

    clean_count = int((shipments_df["clean_status"] == "CLEAN").sum()) + int(
        (inventory_df["clean_status"] == "CLEAN").sum()
    )
    fixed_count = int((shipments_df["clean_status"] == "FIXED").sum()) + int(
        (inventory_df["clean_status"] == "FIXED").sum()
    )
    needs_review_count = int((shipments_df["clean_status"] == "NEEDS_REVIEW").sum()) + int(
        (inventory_df["clean_status"] == "NEEDS_REVIEW").sum()
    )

    executive_summary = (
        f"Processed {len(files)} files with {total_rows} rows. "
        f"Accepted {accepted_rows}, rejected {rejected_rows}, removed {duplicates_removed} duplicates. "
        f"Issues logged: {len(ISSUE_LOG)}. Overall quality score: {quality_score}%."
    )

    summary_rows = [
        ("Generated At", pd.Timestamp.now().strftime("%Y-%m-%d %H:%M:%S")),
        ("Total Input Files", len(files)),
        ("Total Rows Processed", total_rows),
        ("Total Shipment Rows Processed", loaded_shipments),
        ("Total Inventory Rows Processed", loaded_inventory),
        ("Accepted Rows", accepted_rows),
        ("Rejected Rows", rejected_rows),
        ("Duplicate Records Removed", duplicates_removed),
        ("Clean Records", clean_count),
        ("Fixed Records", fixed_count),
        ("Needs Review Records", needs_review_count),
        ("Issues Logged", len(ISSUE_LOG)),
        ("Overall Quality Score (%)", quality_score),
        ("Executive Summary", executive_summary),
    ]

    summary_df = pd.DataFrame(summary_rows, columns=["Metric", "Value"])

    if ISSUE_LOG:
        issues_df = pd.DataFrame(ISSUE_LOG)
    else:
        issues_df = pd.DataFrame(
            columns=[
                "entity",
                "source_file",
                "source_sheet",
                "row_number",
                "field",
                "original_value",
                "issue",
                "action",
                "fixed_value",
            ]
        )

    if REJECTED_RECORDS:
        rejected_df = pd.DataFrame(REJECTED_RECORDS)
    else:
        rejected_df = pd.DataFrame(
            columns=[
                "entity",
                "source_file",
                "source_sheet",
                "row_number",
                "reason",
                "raw_data",
            ]
        )

    report_path = output_dir / "repair_report.xlsx"

    with pd.ExcelWriter(report_path, engine="openpyxl") as writer:
        summary_df.to_excel(writer, sheet_name="Summary", index=False)
        issues_df.to_excel(writer, sheet_name="Issue Log", index=False)
        rejected_df.to_excel(writer, sheet_name="Rejected Records", index=False)

    print("Pipeline completed successfully.")
    print(f"Cleaned output: {cleaned_path}")
    print(f"Repair report: {report_path}")


if __name__ == "__main__":
    run_pipeline()
