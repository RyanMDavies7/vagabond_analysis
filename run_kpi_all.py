"""
Scan every client (leaf) account under your MCC, run ALL tracking KPIs,
and write one Excel sheet with one row per account.
"""

import os
import pandas as pd
from packages.google_ads_kpi.auth import get_client
from packages.google_ads_kpi.hierarchy import list_leaf_accounts
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

# Put every KPI function you want to execute in this list
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


def main() -> None:
    client = get_client()

    # 1️⃣ Pull all leaf accounts
    mcc_cid = os.environ["LOGIN_CUSTOMER_ID"]
    leaves = list_leaf_accounts(client, mcc_cid)
    print(f"Found {len(leaves)} leaf accounts under {mcc_cid}")

    # 2️⃣ Run every KPI for each leaf
    rows = []
    for cid, name in leaves.items():
        print(f"▶ {name} ({cid})", end=" … ")
        row = {"customer_id": cid, "account_name": name}

        try:
            for fn in KPI_FUNCS:
                row.update(fn(client, cid))
            print("OK")
        except Exception as exc:
            print("FAIL", exc)
            # Leave KPI fields blank on failure; keep account in sheet
        rows.append(row)

    # 3️⃣ Save results
    pd.DataFrame(rows).to_excel("kpi_all_accounts.xlsx", index=False)
    print("✅ Saved kpi_all_accounts.xlsx with", len(rows), "rows")


if __name__ == "__main__":
    main()
