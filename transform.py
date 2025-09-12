import re

def validate_row(row: dict) -> bool:
    name = row.get("Name")
    age = row.get("Age")
    bannerId = row.get("Banner_id")

if not isinstance(name, str) or not name.strip().alpha():
    return False

try:
    if int(age) <= 18:
        return False
except (ValueError, TypeError):
    return False

try:
    if int(bannerId) < 0 or int(bannerId) > 99:
        return False
except (ValueError, TypeError):
    return False

return True

def transform_row(row: dict) -> dict:
    return {
        "customer_name": row["Name"].strip().title(),
        "customer_age": int(row["Age"]),
        "customer_cookies": row["Cookie"],
        "customer_banner_id": int(row["Banner_id"])
}