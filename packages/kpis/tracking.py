# kpi_core/tracking.py
import datetime
from packages.google_ads_kpi.query import paged_search, DEFAULT_RETRY
from google.ads.googleads.errors import GoogleAdsException


# ──────────────────────────────────────────────────────────────────────────────
# Helper: pull every conversion-action once so we don’t hit the API repeatedly
# ──────────────────────────────────────────────────────────────────────────────
def _get_conversion_actions(ga_service, cid: str):
    query = """
      SELECT
        conversion_action.id,
        conversion_action.name,
        conversion_action.type,
        conversion_action.status,
        conversion_action.primary_for_goal,
        conversion_action.value_settings.default_value,
        conversion_action.attribution_model_settings.attribution_model
      FROM conversion_action
    """
    return list(paged_search(ga_service, cid, query, timeout=15.0))


# ──────────────────────────────────────────────────────────────────────────────
# KPI 1 – Enabled conversion actions & how many have values
# ──────────────────────────────────────────────────────────────────────────────
def kpi_enabled_conversion_actions(client, customer_id: str, days: int = 30):
    ga_service = client.get_service("GoogleAdsService")

    action_q = """
      SELECT conversion_action.status,
             conversion_action.value_settings.default_value
      FROM conversion_action
      WHERE conversion_action.status = 'ENABLED'
    """
    enabled, with_value = 0, 0
    for row in paged_search(ga_service, customer_id, action_q):
        enabled += 1
        if row.conversion_action.value_settings.default_value:
            with_value += 1

    return {
        "customer_id": customer_id,
        "enabled_actions": enabled,
        "enabled_with_value": with_value,
    }


# ──────────────────────────────────────────────────────────────────────────────
# KPI 2 – Primary conversion must contain “purchase”
# ──────────────────────────────────────────────────────────────────────────────
def kpi_primary_is_purchase(client, customer_id: str):
    ga_service = client.get_service("GoogleAdsService")
    actions = _get_conversion_actions(ga_service, customer_id)

    primary = [
        a.conversion_action.name.lower()
        for a in actions
        if a.conversion_action.primary_for_goal
        and a.conversion_action.status.name == "ENABLED"
    ]
    ok = any("purchase" in n for n in primary)

    return {
        "customer_id": customer_id,
        "primary_is_purchase": ok,
        "primary_actions": ", ".join(primary) or "none",
    }


# ──────────────────────────────────────────────────────────────────────────────
# KPI 3 – Any goals still on Last-Click?
# ──────────────────────────────────────────────────────────────────────────────
def kpi_last_click_present(client, customer_id: str):
    ga_service = client.get_service("GoogleAdsService")
    actions = _get_conversion_actions(ga_service, customer_id)

    last_click = [
        a.conversion_action.name
        for a in actions
        if (
                a.conversion_action.attribution_model_settings.attribution_model == "LAST_CLICK"
                and a.conversion_action.status.name == "ENABLED"
        )
    ]
    return {
        "customer_id": customer_id,
        "has_last_click_goals": bool(last_click),
        "last_click_list": ", ".join(last_click) or "none",
    }


# ──────────────────────────────────────────────────────────────────────────────
# KPI 4 – Enhanced conversions enabled at account level?
# ──────────────────────────────────────────────────────────────────────────────
def kpi_enhanced_conversions(client, customer_id: str):
    ga = client.get_service("GoogleAdsService")
    query = """
      SELECT
        customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled
      FROM customer
      LIMIT 1
    """
    response = ga.search(
        customer_id=customer_id,
        query=query,
        retry=DEFAULT_RETRY,
        timeout=15.0,
    )

    row = next(iter(response), None)  # ← fix

    enabled = (
        row.customer.conversion_tracking_setting.enhanced_conversions_for_leads_enabled
        if row else False
    )

    return {
        "customer_id": customer_id,
        "enhanced_conversions_on": bool(enabled),
    }


# ──────────────────────────────────────────────────────────────────────────────
# KPI 5 – Call-tracking conversion actions present?
# ──────────────────────────────────────────────────────────────────────────────
def kpi_call_tracking(client, customer_id: str):
    ga_service = client.get_service("GoogleAdsService")
    actions = _get_conversion_actions(ga_service, customer_id)

    calls = [
        a.conversion_action.name
        for a in actions
        if a.conversion_action.type.name.startswith("CALL_")
        and a.conversion_action.status.name == "ENABLED"
    ]
    return {
        "customer_id": customer_id,
        "call_tracking_present": bool(calls),
        "call_goal_list": ", ".join(calls) or "none",
    }


# ──────────────────────────────────────────────────────────────────────────────
# KPI 6 – Store-visit goal present?
# ──────────────────────────────────────────────────────────────────────────────
def kpi_store_visits(client, customer_id: str):
    ga_service = client.get_service("GoogleAdsService")
    actions = _get_conversion_actions(ga_service, customer_id)

    stores = [
        a.conversion_action.name
        for a in actions
        if a.conversion_action.type.name == "STORE_VISIT"
        and a.conversion_action.status.name == "ENABLED"
    ]
    return {
        "customer_id": customer_id,
        "store_visits_present": bool(stores),
        "store_visit_list": ", ".join(stores) or "none",
    }


# ──────────────────────────────────────────────────────────────────────────────
# KPI 7 – Auto-tagging on?
# ──────────────────────────────────────────────────────────────────────────────
def kpi_auto_tagging(client, customer_id: str):
    ga_service = client.get_service("GoogleAdsService")

    query = """
      SELECT customer.auto_tagging_enabled
      FROM customer
      LIMIT 1
    """

    row = next(
        iter(
            ga_service.search(
                customer_id=customer_id,
                query=query,
                retry=DEFAULT_RETRY,
                timeout=15.0,
            )
        ),
        None,
    )

    enabled = row.customer.auto_tagging_enabled if row else False
    return {
        "customer_id": customer_id,
        "auto_tagging_enabled": bool(enabled),
    }

# ──────────────────────────────────────────────────────────────────────────────
# KPI 8 – Offline conversion import success (past 30 days)
# ──────────────────────────────────────────────────────────────────────────────
def kpi_offline_import(client, customer_id: str, check_jobs: int = 20):
    """Count last N offline-import jobs and how many succeeded."""
    ga = client.get_service("GoogleAdsService")

    query = f"""
      SELECT
        offline_user_data_job.status
      FROM offline_user_data_job
      WHERE offline_user_data_job.type = 'STORE_SALES_UPLOAD_FIRST_PARTY'
      ORDER BY offline_user_data_job.id DESC
      LIMIT {check_jobs}
    """

    jobs = list(paged_search(ga, customer_id, query, timeout=15.0))
    success = [j for j in jobs if j.offline_user_data_job.status.name == "SUCCESS"]

    return {
        "customer_id": customer_id,
        "offline_jobs_checked": len(jobs),
        "offline_success": len(success),
        "offline_import_ok": bool(success),
    }

