"""Label management tools for Google Ads API."""

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._ads_api import resource_types, service_types
from ads_mcp.tools.mutations.common import _get_client, _handle_google_ads_error
from google.ads.googleads.errors import GoogleAdsException


@mcp.tool()
def create_label(customer_id: str, name: str, description: str = "", login_customer_id: str | None = None) -> dict[str, str]:
  """Creates a label. Args: customer_id: Google Ads customer ID. name: Label name. description: Optional. login_customer_id: MCC ID if managed."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("LabelService")
  label = resource_types.Label(name=name)
  if description: label.description = description
  operation = service_types.LabelOperation(create=label)
  try:
    response = service.mutate_labels(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def apply_label_to_campaign(customer_id: str, campaign_resource_name: str, label_resource_name: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Applies a label to a campaign."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignLabelService")
  operation = service_types.CampaignLabelOperation(create=resource_types.CampaignLabel(campaign=campaign_resource_name, label=label_resource_name))
  try:
    response = service.mutate_campaign_labels(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def apply_label_to_ad_group(customer_id: str, ad_group_resource_name: str, label_resource_name: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Applies a label to an ad group."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupLabelService")
  operation = service_types.AdGroupLabelOperation(create=resource_types.AdGroupLabel(ad_group=ad_group_resource_name, label=label_resource_name))
  try:
    response = service.mutate_ad_group_labels(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def apply_label_to_ad(customer_id: str, ad_group_ad_resource_name: str, label_resource_name: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Applies a label to an ad."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupAdLabelService")
  operation = service_types.AdGroupAdLabelOperation(create=resource_types.AdGroupAdLabel(ad_group_ad=ad_group_ad_resource_name, label=label_resource_name))
  try:
    response = service.mutate_ad_group_ad_labels(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def remove_label_from_campaign(customer_id: str, campaign_label_resource_name: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Removes a label from a campaign."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignLabelService")
  operation = service_types.CampaignLabelOperation(remove=campaign_label_resource_name)
  try:
    response = service.mutate_campaign_labels(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"removed": response.results[0].resource_name}
