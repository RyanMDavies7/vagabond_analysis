import os
from dotenv import load_dotenv, find_dotenv
from google.ads.googleads.client import GoogleAdsClient
from google.ads.googleads.errors import GoogleAdsException

load_dotenv(find_dotenv())

# 1. Build an in-memory config dict
config = {
    "developer_token": os.environ["GOOGLE_DEVELOPER_TOKEN"],
    "client_id": os.environ["GOOGLE_CLIENT_ID"],
    "client_secret": os.environ["GOOGLE_CLIENT_SECRET"],
    "refresh_token": os.environ["GOOGLE_REFRESH_TOKEN"],
    "use_proto_plus": True,
    "login_customer_id": os.environ["LOGIN_CUSTOMER_ID"]
}


# ------------------------------------------------------------------------------
# 2. Helper to walk the tree recursively and collect children
# ------------------------------------------------------------------------------
def list_sub_accounts(client, manager_cid: str, level: int = 0, seen=None):
    """
    Walk customer → customer_client hierarchy, print a tree,
    and return {leaf_cid: descriptive_name}.
    """
    if seen is None:
        seen = set()

    ga_service = client.get_service("GoogleAdsService")
    query = """
      SELECT
        customer_client.client_customer,
        customer_client.descriptive_name,
        customer_client.manager,
        customer_client.level
      FROM customer_client
      WHERE customer_client.status = 'ENABLED'
    """

    leaf_accounts = {}
    stream = ga_service.search_stream(customer_id=manager_cid, query=query)

    for batch in stream:
        for row in batch.results:
            # "customers/719-275-3145" → "7192753145"
            cid = row.customer_client.client_customer.split("/")[1].replace("-", "")
            name = row.customer_client.descriptive_name
            is_manager = row.customer_client.manager
            indent = "  " * level
            print(f"{indent}- {name} ({cid}){' [M]' if is_manager else ''}")

            if cid in seen:        # guard against loops
                continue
            seen.add(cid)

            if is_manager:
                leaf_accounts.update(
                    list_sub_accounts(client, cid, level + 1, seen)
                )
            else:
                leaf_accounts[cid] = name

    return leaf_accounts

# ------------------------------------------------------------------------------
# 3. Main: authenticate then print the tree
# ------------------------------------------------------------------------------
if __name__ == "__main__":
    try:
        client = GoogleAdsClient.load_from_dict(config)
        print("✅ Auth OK – listing hierarchy under", config["login_customer_id"], "\n")
        leaves = list_sub_accounts(client, config["login_customer_id"])
        print("\nFound", len(leaves), "non-manager (leaf) accounts.")
    except GoogleAdsException as ex:
        print("❌ Google Ads API call failed:")
        for err in ex.failure.errors:
            print(f"  • {err.error_code}: {err.message}")
        raise