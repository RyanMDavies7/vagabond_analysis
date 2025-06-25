# packages/google_ads_kpi/hierarchy.py
"""
Hierarchy utilities: identify all *leaf* (non-manager) accounts that sit
under a given manager/MCC.

Typical use:
    from google_ads_kpi.auth import get_client
    from google_ads_kpi.hierarchy import list_leaf_accounts

    client = get_client()
    leaves = list_leaf_accounts(client, "9168266268")   # manager CID
    print(leaves)   # {'7192753145': 'Scarlett Gaming', ...}
"""

from google.api_core.retry import Retry, if_exception_type
from google.api_core import exceptions

# Retry spec reused across GAQL calls
DEFAULT_RETRY = Retry(
    predicate=if_exception_type(
        exceptions.ServiceUnavailable,
        exceptions.DeadlineExceeded,
    ),
    initial=2.0, maximum=32.0, multiplier=2.0, deadline=60.0,
)

def list_leaf_accounts(client, manager_cid: str) -> dict[str, str]:
    """
    Recursively walk the customer_client tree starting at `manager_cid`
    and return {leaf_cid: descriptive_name} for every non-manager child.

    manager_cid  – 10-digit string, no dashes
    """
    ga_service = client.get_service("GoogleAdsService")

    # GAQL grabs client CID, name and manager flag
    query = """
      SELECT
        customer_client.client_customer,
        customer_client.descriptive_name,
        customer_client.manager
      FROM customer_client
      WHERE customer_client.status = 'ENABLED'
    """

    leaves: dict[str, str] = {}
    visited: set[str] = set()

    def _walk(cid: str):
        if cid in visited:
            return
        visited.add(cid)

        for row in ga_service.search(
            customer_id=cid,
            query=query,
            retry=DEFAULT_RETRY,
            timeout=15.0,
        ):
            child_cid = (
                row.customer_client.client_customer  # "customers/1234567890"
                .split("/")[1]
                .replace("-", "")
            )
            name = row.customer_client.descriptive_name
            if row.customer_client.manager:
                _walk(child_cid)              # recurse into sub-manager
            else:
                leaves[child_cid] = name      # store leaf

    _walk(manager_cid)
    return leaves
