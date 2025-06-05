# --- name: Conversion tracking active?
# description: Fills one-row audit Excel and returns it for download.
# inputs:
#   customer_id:
#     label: Google Ads CID
#     type: string
#   template_file:
#     label: Excel template (.xlsx)
#     type: file
#     required: true
#   lookback_days:
#     type: integer
#     default: 30
# ---
import tempfile, openpyxl
from wm import files
from google_ads_kpi.google_client import get_client
from google_ads_kpi.kpi import conversion_tracking_active

def main(customer_id: str, template_file: files.File, lookback_days: int = 30):
    client = get_client()
    result = conversion_tracking_active(client, customer_id, lookback_days)

    with tempfile.NamedTemporaryFile(suffix=".xlsx", delete=False) as tmp:
        wb = openpyxl.load_workbook(template_file.path)
        ws = wb["Audit"]
        ws["B4"].value = "Yes" if result["has_conversions"] else "No"
        ws["C4"].value = result["conversion_sum"]
        ws["D4"].value = result["last_date"] or "–"
        wb.save(tmp.name)

    return files.File(tmp.name, name=f"audit_{customer_id}.xlsx")