from dotenv import load_dotenv, find_dotenv
import os
from google.ads.googleads.client import GoogleAdsClient

load_dotenv(find_dotenv())

def get_client() -> GoogleAdsClient:
    """Return an authenticated Google Ads client (uses manager login)."""
    cfg = {
        "developer_token":  os.getenv("GOOGLE_DEVELOPER_TOKEN"),
        "client_id":        os.getenv("GOOGLE_CLIENT_ID"),
        "client_secret":    os.getenv("GOOGLE_CLIENT_SECRET"),
        "refresh_token":    os.getenv("GOOGLE_REFRESH_TOKEN"),
        "use_proto_plus":   True,
        "login_customer_id": os.getenv("LOGIN_CUSTOMER_ID"),  # manager CID
    }
    return GoogleAdsClient.load_from_dict(cfg)
