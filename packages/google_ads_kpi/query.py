"""
query.py – convenience wrappers for Google Ads GAQL calls
"""

from google.api_core.retry import Retry, if_exception_type
from google.api_core import exceptions


# --------------------------------------------------------------------------- #
# Default retry: handles transient 503/504                                         #
# --------------------------------------------------------------------------- #
DEFAULT_RETRY = Retry(
    predicate=if_exception_type(
        exceptions.ServiceUnavailable,      # 503
        exceptions.DeadlineExceeded         # 504 / socket timeout
    ),
    initial=2.0,        # seconds
    maximum=32.0,
    multiplier=2.0,     # exponential back-off
    deadline=60.0       # total wall-time per call
)


def paged_search(
    ga_service,
    customer_id: str,
    query: str,
    *,
    page_size: int = 1000,
    retry=DEFAULT_RETRY,
    timeout: float = 15.0,
):
    """
    Generator yielding GAQL rows, using paged `search()` not `search_stream()`.

    Args:
        ga_service    : client.get_service("GoogleAdsService")
        customer_id   : leaf CID (numeric str, no dashes)
        query         : GAQL string
        retry, timeout: gRPC call options

    Yields:
        google.ads.googleads.v* resources (rows)
    """
    response = ga_service.search(
        customer_id=customer_id,
        query=query,
        retry=retry,
        timeout=timeout,
    )
    for row in response:
        yield row
