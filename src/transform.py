import re
import sys
sys.path.append("/Library/Frameworks/Python.framework/Versions/3.10/lib/python3.10/site-packages")
import requests
import csv

def validate_row(row: dict) -> bool:
    name = row.get("Name")
    age = row.get("Age")
    bannerId = row.get("Banner_id")
    cookie = row.get("Cookie")

    if not isinstance(name, str) or not name.strip():
        return False
    if not all(c.isalpha() or c.isspace() for c in name.strip()):
        return False
    try:
        age_int = int(age)
        if age_int <= 0:
            return False
    except (ValueError, TypeError):
        return False
    try:
        banner_int = int(bannerId)
        if banner_int < 0 or banner_int > 99:
            return False
    except (ValueError, TypeError):
        return False

    if not isinstance(cookie, str) or not cookie.strip():
        return False
    return True

def transform_row(row: dict) -> dict:
    return {
        "customer_name": row["Name"].strip().title(),
        "customer_age": int(row["Age"]),
        "customer_cookies": row["Cookie"],
        "customer_banner_id": int(row["Banner_id"])
}

# Test code removed - functionality moved to csv_connector.py
