import os
from google.ads.googleads.client import GoogleAdsClient

def get_client(login_customer_id: str | None = None) -> GoogleAdsClient:
    """Instantiate a GoogleAdsClient using env vars (see .env.example)."""
    config = {
        "developer_token": os.environ["GOOGLE_DEVELOPER_TOKEN"],
        "client_id":       os.environ["GOOGLE_CLIENT_ID"],
        "client_secret":   os.environ["GOOGLE_CLIENT_SECRET"],
        "refresh_token":   os.environ["GOOGLE_REFRESH_TOKEN"],
    }
    if login_customer_id:
        config["login_customer_id"] = login_customer_id
    return GoogleAdsClient.load_from_dict(config, version="15")