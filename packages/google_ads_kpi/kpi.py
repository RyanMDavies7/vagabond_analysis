"""Pure KPI calculation functions."""
from datetime import date, timedelta
from google.ads.googleads.client import GoogleAdsClient

def conversion_tracking_active(client: GoogleAdsClient, customer_id: str, days:int=30) -> dict:
    """Checks if any conversions fired in the last `days` days for the account."""
    since = (date.today() - timedelta(days=days)).isoformat()
    query = f"""
        SELECT
          segments.date,
          metrics.conversions
        FROM customer
        WHERE segments.date >= '{since}'
          AND metrics.conversions > 0
        LIMIT 1
    """
    service = client.get_service("GoogleAdsService")
    rows = [row for batch in service.search_stream(customer_id=customer_id, query=query) for row in batch.results]
    return {
        "customer_id": customer_id,
        "has_conversions": bool(rows),
        "last_date": str(rows[0].segments.date) if rows else None,
        "conversion_sum": sum(int(r.metrics.conversions) for r in rows)
    }