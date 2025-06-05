"""Generates an Excel audit sheet for one account using the template."""
import os, openpyxl
from google_ads_kpi.google_client import get_client
from google_ads_kpi.kpi import conversion_tracking_active

TEMPLATE_PATH = os.getenv("AUDIT_TEMPLATE", "template.xlsx")  # path to your template
OUTPUT_PATH = os.getenv("AUDIT_OUT", "audit_out.xlsx")
CUSTOMER_ID = os.environ["CUSTOMER_ID"]

client = get_client()
result = conversion_tracking_active(client, CUSTOMER_ID)

wb = openpyxl.load_workbook(TEMPLATE_PATH)
ws = wb["Audit"]

ws["B4"].value = "Yes" if result["has_conversions"] else "No"
ws["C4"].value = result["conversion_sum"]
ws["D4"].value = result["last_date"] or "–"

wb.save(OUTPUT_PATH)
print(f"✅ Wrote {OUTPUT_PATH}")