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

csv_path = "/Users/elenasurovtseva/integration_assignment_meiro/data.csv"
transformed_rows = []
total_rows = 0

with open(csv_path, newline="", encoding="utf-8") as f:
    reader = csv.DictReader(f)
    for row in reader:
        total_rows += 1
        if validate_row(row):
            transformed_rows.append(transform_row(row))

header = {"Authorization": f"Bearer 1bb52ffc-7b48-4dec-834f-ee30a375abab"}
url = "https://intg-engineer-server-929282497502.europe-west1.run.app/banners/show"

if transformed_rows:
    body = {
        "VisitorCookies": transformed_rows[0]["customer_cookies"],
        "BannerId": transformed_rows[0]["customer_banner_id"]
    }
    response = requests.post(url, headers=header, json=body)
    print(response.status_code)
    print(response.text)
