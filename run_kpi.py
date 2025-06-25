"""
Run every Tracking KPI for one CUSTOMER_ID
and write a single-row Excel sheet.
"""

import os
import pandas as pd
from packages.google_ads_kpi.auth import get_client
from packages.kpis.tracking import (
    kpi_enabled_conversion_actions,
    kpi_primary_is_purchase,
    kpi_last_click_present,
    kpi_enhanced_conversions,
    kpi_call_tracking,
    kpi_store_visits,
    kpi_auto_tagging,
    kpi_offline_import,
)

# list of callables to execute in order
KPI_FUNCS = [
    kpi_enabled_conversion_actions,
    kpi_primary_is_purchase,
    kpi_last_click_present,
    kpi_enhanced_conversions,
    kpi_call_tracking,
    kpi_store_visits,
    kpi_auto_tagging,
    kpi_offline_import,
]


def main():
    cid = os.getenv("CUSTOMER_ID")
    if not cid:
        raise SystemExit("Set CUSTOMER_ID in your .env")

    client = get_client()

    # Run each KPI and merge the dicts into one row
    row = {}
    for fn in KPI_FUNCS:
        row.update(fn(client, cid))

    pd.DataFrame([row]).to_excel("kpi_output.xlsx", index=False)
    print(f"✅ Wrote kpi_output.xlsx with {len(KPI_FUNCS)} KPIs")


if __name__ == "__main__":
    main()
