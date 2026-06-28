"""Shared negative keyword list tools for Google Ads API."""

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._ads_api import common_types, enum_types, resource_types, service_types
from ads_mcp.tools.mutations.common import _get_client, _handle_google_ads_error
from google.ads.googleads.errors import GoogleAdsException


@mcp.tool()
def create_shared_negative_keyword_list(customer_id: str, name: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Creates a shared negative keyword list. Args: customer_id: Google Ads customer ID. name: List name. login_customer_id: MCC ID if managed."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("SharedSetService")
  operation = service_types.SharedSetOperation(create=resource_types.SharedSet(name=name, type_=enum_types.SharedSetTypeEnum.SharedSetType.NEGATIVE_KEYWORDS))
  try:
    response = service.mutate_shared_sets(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def add_keywords_to_shared_list(customer_id: str, shared_set_resource_name: str, keywords: list[str], login_customer_id: str | None = None) -> dict[str, list[str]]:
  """Adds keywords to a shared negative list. Args: customer_id: Google Ads customer ID. shared_set_resource_name: From create_shared_negative_keyword_list. keywords: List of keyword strings. login_customer_id: MCC ID if managed."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("SharedCriterionService")
  operations = [service_types.SharedCriterionOperation(create=resource_types.SharedCriterion(shared_set=shared_set_resource_name, keyword=common_types.KeywordInfo(text=kw, match_type=enum_types.KeywordMatchTypeEnum.KeywordMatchType.BROAD))) for kw in keywords]
  try:
    response = service.mutate_shared_criteria(customer_id=customer_id, operations=operations)
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_names": [r.resource_name for r in response.results]}


@mcp.tool()
def attach_shared_list_to_campaign(customer_id: str, campaign_resource_name: str, shared_set_resource_name: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Links a shared negative keyword list to a campaign."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignSharedSetService")
  operation = service_types.CampaignSharedSetOperation(create=resource_types.CampaignSharedSet(campaign=campaign_resource_name, shared_set=shared_set_resource_name))
  try:
    response = service.mutate_campaign_shared_sets(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def remove_shared_list_from_campaign(customer_id: str, campaign_shared_set_resource_name: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Unlinks a shared list from a campaign."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignSharedSetService")
  operation = service_types.CampaignSharedSetOperation(remove=campaign_shared_set_resource_name)
  try:
    response = service.mutate_campaign_shared_sets(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"removed": response.results[0].resource_name}
