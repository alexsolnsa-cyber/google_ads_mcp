# Copyright 2025 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

"""Campaign mutation tools for Google Ads API."""

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._ads_api import common_types
from ads_mcp.tools._ads_api import enum_types
from ads_mcp.tools._ads_api import resource_types
from ads_mcp.tools._ads_api import service_types
from ads_mcp.tools.mutations.common import _get_client
from ads_mcp.tools.mutations.common import _handle_google_ads_error
from ads_mcp.tools.mutations.common import _resolve_enum
from fastmcp.exceptions import ToolError
from google.ads.googleads.errors import GoogleAdsException
from google.protobuf import field_mask_pb2


def _build_bidding_strategy(strategy, target_cpa_micros=None, target_roas=None):
  strategy_upper = strategy.upper().replace(" ", "_")
  if strategy_upper == "TARGET_SPEND":
    return "target_spend", common_types.TargetSpend(), ["target_spend.target_spend_micros"]
  elif strategy_upper == "MAXIMIZE_CONVERSIONS":
    mc = common_types.MaximizeConversions()
    if target_cpa_micros: mc.target_cpa_micros = target_cpa_micros
    return "maximize_conversions", mc, ["maximize_conversions.target_cpa_micros"]
  elif strategy_upper == "MAXIMIZE_CONVERSION_VALUE":
    mcv = common_types.MaximizeConversionValue()
    if target_roas: mcv.target_roas = target_roas
    return "maximize_conversion_value", mcv, ["maximize_conversion_value.target_roas"]
  elif strategy_upper == "MANUAL_CPC":
    return "manual_cpc", common_types.ManualCpc(enhanced_cpc_enabled=False), ["manual_cpc.enhanced_cpc_enabled"]
  elif strategy_upper == "ENHANCED_CPC":
    return "manual_cpc", common_types.ManualCpc(enhanced_cpc_enabled=True), ["manual_cpc.enhanced_cpc_enabled"]
  elif strategy_upper == "TARGET_CPA":
    if not target_cpa_micros: raise ToolError("target_cpa_micros is required for TARGET_CPA.")
    return "target_cpa", common_types.TargetCpa(target_cpa_micros=target_cpa_micros), ["target_cpa.target_cpa_micros"]
  elif strategy_upper == "TARGET_ROAS":
    if not target_roas: raise ToolError("target_roas is required for TARGET_ROAS.")
    return "target_roas", common_types.TargetRoas(target_roas=target_roas), ["target_roas.target_roas"]
  else:
    raise ToolError(f"Invalid bidding strategy: {strategy!r}. Valid: TARGET_SPEND, MAXIMIZE_CONVERSIONS, MAXIMIZE_CONVERSION_VALUE, MANUAL_CPC, ENHANCED_CPC, TARGET_CPA, TARGET_ROAS.")


@mcp.tool()
def create_search_campaign(customer_id: str, name: str, budget_resource_name: str, bidding_strategy: str = "TARGET_SPEND", target_cpa_micros: int | None = None, target_roas: float | None = None, status: str = "PAUSED", target_google_search: bool = True, target_search_network: bool = False, target_content_network: bool = False, login_customer_id: str | None = None) -> dict[str, str]:
  """Creates a Search campaign. Args: customer_id: Google Ads customer ID. name: Campaign name. budget_resource_name: From create_campaign_budget. bidding_strategy: TARGET_SPEND/MAXIMIZE_CONVERSIONS/MAXIMIZE_CONVERSION_VALUE/MANUAL_CPC/ENHANCED_CPC/TARGET_CPA/TARGET_ROAS. target_cpa_micros: For TARGET_CPA/MAXIMIZE_CONVERSIONS. target_roas: For TARGET_ROAS/MAXIMIZE_CONVERSION_VALUE. status: PAUSED or ENABLED. login_customer_id: MCC account ID if managed."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")
  strategy_field, strategy_value, _ = _build_bidding_strategy(bidding_strategy, target_cpa_micros, target_roas)
  eu_status = enum_types.EuPoliticalAdvertisingStatusEnum.EuPoliticalAdvertisingStatus.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING
  campaign = resource_types.Campaign(name=name, campaign_budget=budget_resource_name, status=_resolve_enum(enum_types.CampaignStatusEnum.CampaignStatus, status, "status"), advertising_channel_type=enum_types.AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH, contains_eu_political_advertising=eu_status)
  setattr(campaign, strategy_field, strategy_value)
  campaign.network_settings.target_google_search = target_google_search
  campaign.network_settings.target_search_network = target_search_network
  campaign.network_settings.target_content_network = target_content_network
  campaign.network_settings.target_partner_search_network = False
  operation = service_types.CampaignOperation(create=campaign)
  try:
    response = service.mutate_campaigns(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def update_campaign_bidding_strategy(customer_id: str, campaign_resource_name: str, bidding_strategy: str, target_cpa_micros: int | None = None, target_roas: float | None = None, login_customer_id: str | None = None) -> dict[str, str]:
  """Updates a campaign's bidding strategy. Args: customer_id: Google Ads customer ID. campaign_resource_name: Full resource name. bidding_strategy: TARGET_SPEND/MAXIMIZE_CONVERSIONS/MAXIMIZE_CONVERSION_VALUE/MANUAL_CPC/ENHANCED_CPC/TARGET_CPA/TARGET_ROAS. target_cpa_micros: For TARGET_CPA/MAXIMIZE_CONVERSIONS. target_roas: For TARGET_ROAS/MAXIMIZE_CONVERSION_VALUE. login_customer_id: MCC account ID if managed."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")
  strategy_field, strategy_value, mask_paths = _build_bidding_strategy(bidding_strategy, target_cpa_micros, target_roas)
  campaign = resource_types.Campaign(resource_name=campaign_resource_name)
  setattr(campaign, strategy_field, strategy_value)
  operation = service_types.CampaignOperation(update=campaign)
  operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=mask_paths))
  try:
    response = service.mutate_campaigns(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def update_campaign_status(customer_id: str, campaign_resource_name: str, status: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Updates a campaign's status. Args: customer_id: Google Ads customer ID. campaign_resource_name: Full resource name. status: ENABLED or PAUSED. login_customer_id: MCC account ID if managed."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")
  campaign = resource_types.Campaign(resource_name=campaign_resource_name, status=_resolve_enum(enum_types.CampaignStatusEnum.CampaignStatus, status, "status"))
  operation = service_types.CampaignOperation(update=campaign)
  operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
  try:
    response = service.mutate_campaigns(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def update_campaign_name(
    customer_id: str,
    campaign_resource_name: str,
    name: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Renames a campaign.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Full resource name of the campaign.
      name: New campaign name.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the updated campaign resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")

  campaign = resource_types.Campaign(
      resource_name=campaign_resource_name,
      name=name,
  )

  operation = service_types.CampaignOperation(update=campaign)
  operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["name"]))

  try:
    response = service.mutate_campaigns(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def update_campaign_ad_rotation(
    customer_id: str,
    campaign_resource_name: str,
    ad_rotation_mode: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Updates a campaign's ad rotation mode.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Full resource name of the campaign.
      ad_rotation_mode: How ads are rotated. Valid values:
        OPTIMIZE - Google optimizes for best performing ads (recommended).
        ROTATE_INDEFINITELY - Ads are shown evenly (for A/B testing).
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the updated campaign resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")

  rotation_type = _resolve_enum(
      enum_types.AdServingOptimizationStatusEnum.AdServingOptimizationStatus,
      ad_rotation_mode,
      "ad_rotation_mode",
  )

  campaign = resource_types.Campaign(
      resource_name=campaign_resource_name,
      ad_serving_optimization_status=rotation_type,
  )

  operation = service_types.CampaignOperation(update=campaign)
  operation.update_mask.CopyFrom(
      field_mask_pb2.FieldMask(paths=["ad_serving_optimization_status"])
  )

  try:
    response = service.mutate_campaigns(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def update_campaign_geo_target_type(customer_id: str, campaign_resource_name: str, positive_geo_target_type: str | None = None, negative_geo_target_type: str | None = None, login_customer_id: str | None = None) -> dict[str, str]:
  """Updates a campaign's geo targeting mode. Args: customer_id: Google Ads customer ID. campaign_resource_name: Full resource name. positive_geo_target_type: PRESENCE_OR_INTEREST/SEARCH_INTEREST/PRESENCE. negative_geo_target_type: PRESENCE_OR_INTEREST/PRESENCE. login_customer_id: MCC account ID if managed."""
  if not positive_geo_target_type and not negative_geo_target_type:
    raise ToolError("At least one geo target type must be provided.")
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")
  campaign = resource_types.Campaign(resource_name=campaign_resource_name)
  paths = []
  if positive_geo_target_type:
    campaign.geo_target_type_setting.positive_geo_target_type = _resolve_enum(enum_types.PositiveGeoTargetTypeEnum.PositiveGeoTargetType, positive_geo_target_type, "positive_geo_target_type")
    paths.append("geo_target_type_setting.positive_geo_target_type")
  if negative_geo_target_type:
    campaign.geo_target_type_setting.negative_geo_target_type = _resolve_enum(enum_types.NegativeGeoTargetTypeEnum.NegativeGeoTargetType, negative_geo_target_type, "negative_geo_target_type")
    paths.append("geo_target_type_setting.negative_geo_target_type")
  operation = service_types.CampaignOperation(update=campaign)
  operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=paths))
  try:
    response = service.mutate_campaigns(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def update_campaign_tracking_template(
    customer_id: str,
    campaign_resource_name: str,
    tracking_url_template: str | None = None,
    final_url_suffix: str | None = None,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Updates a campaign's URL tracking template and/or final URL suffix.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Full resource name of the campaign.
      tracking_url_template: URL template with ValueTrack tags (e.g.,
        "{lpurl}?utm_source=google&utm_medium=cpc&utm_term={keyword}").
        Pass empty string to clear.
      final_url_suffix: Parameters appended directly to final URLs (e.g.,
        "utm_campaign=brand&utm_content={adgroupid}").
        Pass empty string to clear.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the updated campaign resource_name.
  """
  if tracking_url_template is None and final_url_suffix is None:
    raise ToolError(
        "At least one of tracking_url_template or final_url_suffix must be provided."
    )

  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")

  campaign = resource_types.Campaign(resource_name=campaign_resource_name)
  field_mask_paths = []

  if tracking_url_template is not None:
    campaign.tracking_url_template = tracking_url_template
    field_mask_paths.append("tracking_url_template")

  if final_url_suffix is not None:
    campaign.final_url_suffix = final_url_suffix
    field_mask_paths.append("final_url_suffix")

  operation = service_types.CampaignOperation(update=campaign)
  operation.update_mask.CopyFrom(
      field_mask_pb2.FieldMask(paths=field_mask_paths)
  )

  try:
    response = service.mutate_campaigns(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def update_campaign_dates(
    customer_id: str,
    campaign_resource_name: str,
    start_date: str | None = None,
    end_date: str | None = None,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Updates a campaign's start and/or end date.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Full resource name of the campaign.
      start_date: Start date in YYYYMMDD format (e.g., "20250901").
      end_date: End date in YYYYMMDD format (e.g., "20251231").
        Pass empty string to remove end date (run indefinitely).
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the updated campaign resource_name.
  """
  if start_date is None and end_date is None:
    raise ToolError(
        "At least one of start_date or end_date must be provided."
    )

  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")

  campaign = resource_types.Campaign(resource_name=campaign_resource_name)
  field_mask_paths = []

  if start_date is not None:
    campaign.start_date = start_date
    field_mask_paths.append("start_date")

  if end_date is not None:
    campaign.end_date = end_date
    field_mask_paths.append("end_date")

  operation = service_types.CampaignOperation(update=campaign)
  operation.update_mask.CopyFrom(
      field_mask_pb2.FieldMask(paths=field_mask_paths)
  )

  try:
    response = service.mutate_campaigns(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def update_campaign_network_settings(
    customer_id: str,
    campaign_resource_name: str,
    target_google_search: bool | None = None,
    target_search_network: bool | None = None,
    target_content_network: bool | None = None,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Updates network settings on an existing campaign.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Full resource name of the campaign.
      target_google_search: Show ads on Google Search.
      target_search_network: Show ads on search partner sites.
        Recommended False — Search Partners historically show lower CVR.
      target_content_network: Show ads on Google Display Network.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the updated campaign resource_name.
  """
  if all(
      v is None
      for v in [target_google_search, target_search_network, target_content_network]
  ):
    raise ToolError("At least one network setting must be provided.")

  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")

  campaign = resource_types.Campaign(resource_name=campaign_resource_name)
  field_mask_paths = []

  if target_google_search is not None:
    campaign.network_settings.target_google_search = target_google_search
    field_mask_paths.append("network_settings.target_google_search")

  if target_search_network is not None:
    campaign.network_settings.target_search_network = target_search_network
    field_mask_paths.append("network_settings.target_search_network")

  if target_content_network is not None:
    campaign.network_settings.target_content_network = target_content_network
    field_mask_paths.append("network_settings.target_content_network")

  operation = service_types.CampaignOperation(update=campaign)
  operation.update_mask.CopyFrom(
      field_mask_pb2.FieldMask(paths=field_mask_paths)
  )

  try:
    response = service.mutate_campaigns(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}
