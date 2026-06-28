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


def _build_bidding_strategy(
    strategy: str,
    target_cpa_micros: int | None = None,
    target_roas: float | None = None,
):
  """Builds a bidding strategy for campaign creation/update.

  Returns a tuple of (field_name, value, field_mask_paths).
  field_mask_paths contains explicit subfield paths required by the API
  for update operations.
  """
  strategy_upper = strategy.upper().replace(" ", "_")

  if strategy_upper == "TARGET_SPEND":
    return (
        "target_spend",
        common_types.TargetSpend(),
        ["target_spend.target_spend_micros"],
    )
  elif strategy_upper == "MAXIMIZE_CONVERSIONS":
    mc = common_types.MaximizeConversions()
    paths = ["maximize_conversions.target_cpa_micros"]
    if target_cpa_micros:
      mc.target_cpa_micros = target_cpa_micros
    return "maximize_conversions", mc, paths
  elif strategy_upper == "MAXIMIZE_CONVERSION_VALUE":
    mcv = common_types.MaximizeConversionValue()
    paths = ["maximize_conversion_value.target_roas"]
    if target_roas:
      mcv.target_roas = target_roas
    return "maximize_conversion_value", mcv, paths
  elif strategy_upper == "MANUAL_CPC":
    return (
        "manual_cpc",
        common_types.ManualCpc(enhanced_cpc_enabled=False),
        ["manual_cpc.enhanced_cpc_enabled"],
    )
  elif strategy_upper == "ENHANCED_CPC":
    return (
        "manual_cpc",
        common_types.ManualCpc(enhanced_cpc_enabled=True),
        ["manual_cpc.enhanced_cpc_enabled"],
    )
  elif strategy_upper == "TARGET_CPA":
    if not target_cpa_micros:
      raise ToolError("target_cpa_micros is required for TARGET_CPA strategy.")
    return (
        "target_cpa",
        common_types.TargetCpa(target_cpa_micros=target_cpa_micros),
        ["target_cpa.target_cpa_micros"],
    )
  elif strategy_upper == "TARGET_ROAS":
    if not target_roas:
      raise ToolError("target_roas is required for TARGET_ROAS strategy.")
    return (
        "target_roas",
        common_types.TargetRoas(target_roas=target_roas),
        ["target_roas.target_roas"],
    )
  else:
    valid = [
        "TARGET_SPEND", "MAXIMIZE_CONVERSIONS",
        "MAXIMIZE_CONVERSION_VALUE", "MANUAL_CPC",
        "ENHANCED_CPC", "TARGET_CPA", "TARGET_ROAS",
    ]
    raise ToolError(
        f"Invalid bidding strategy: {strategy!r}. "
        f"Valid values: {', '.join(valid)}."
    )


@mcp.tool()
def create_search_campaign(
    customer_id: str,
    name: str,
    budget_resource_name: str,
    bidding_strategy: str = "TARGET_SPEND",
    target_cpa_micros: int | None = None,
    target_roas: float | None = None,
    status: str = "PAUSED",
    target_google_search: bool = True,
    target_search_network: bool = False,
    target_content_network: bool = False,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Creates a Search campaign with configurable bidding strategy.

  Args:
      customer_id: Google Ads customer ID (digits only).
      name: Campaign name (e.g., "GoIELTS - Search - Main").
      budget_resource_name: Resource name from create_campaign_budget.
      bidding_strategy: Bidding strategy type. Valid values:
        TARGET_SPEND, MAXIMIZE_CONVERSIONS, MAXIMIZE_CONVERSION_VALUE,
        MANUAL_CPC, ENHANCED_CPC, TARGET_CPA, TARGET_ROAS.
        Default TARGET_SPEND.
      target_cpa_micros: Target CPA in micros. Required for TARGET_CPA,
        optional for MAXIMIZE_CONVERSIONS (e.g., 5000000 = $5.00).
      target_roas: Target ROAS value. Required for TARGET_ROAS,
        optional for MAXIMIZE_CONVERSION_VALUE (e.g., 4.0 = 400%).
      status: PAUSED or ENABLED. Default PAUSED.
      target_google_search: Show on Google Search. Default True.
      target_search_network: Show on search partners. Default False.
      target_content_network: Show on Display Network. Default False.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the campaign resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")

  strategy_field, strategy_value, _ = _build_bidding_strategy(
      bidding_strategy, target_cpa_micros, target_roas
  )

  eu_political_enum = (
      enum_types.EuPoliticalAdvertisingStatusEnum.EuPoliticalAdvertisingStatus
  )
  eu_status = eu_political_enum.DOES_NOT_CONTAIN_EU_POLITICAL_ADVERTISING

  campaign = resource_types.Campaign(
      name=name,
      campaign_budget=budget_resource_name,
      status=_resolve_enum(
          enum_types.CampaignStatusEnum.CampaignStatus, status, "status"
      ),
      advertising_channel_type=(
          enum_types.AdvertisingChannelTypeEnum.AdvertisingChannelType.SEARCH
      ),
      contains_eu_political_advertising=eu_status,
  )
  setattr(campaign, strategy_field, strategy_value)

  campaign.network_settings.target_google_search = target_google_search
  campaign.network_settings.target_search_network = target_search_network
  campaign.network_settings.target_content_network = target_content_network
  campaign.network_settings.target_partner_search_network = False

  operation = service_types.CampaignOperation(create=campaign)
  try:
    response = service.mutate_campaigns(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  resource_name = response.results[0].resource_name
  return {"resource_name": resource_name}


@mcp.tool()
def update_campaign_bidding_strategy(
    customer_id: str,
    campaign_resource_name: str,
    bidding_strategy: str,
    target_cpa_micros: int | None = None,
    target_roas: float | None = None,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Updates a campaign's bidding strategy.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Full resource name of the campaign.
      bidding_strategy: New bidding strategy. Valid values:
        TARGET_SPEND, MAXIMIZE_CONVERSIONS, MAXIMIZE_CONVERSION_VALUE,
        MANUAL_CPC, ENHANCED_CPC, TARGET_CPA, TARGET_ROAS.
      target_cpa_micros: Target CPA in micros. Required for TARGET_CPA,
        optional for MAXIMIZE_CONVERSIONS (e.g., 5000000 = $5.00).
      target_roas: Target ROAS value. Required for TARGET_ROAS,
        optional for MAXIMIZE_CONVERSION_VALUE (e.g., 4.0 = 400%).
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the updated campaign resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")

  strategy_field, strategy_value, mask_paths = _build_bidding_strategy(
      bidding_strategy, target_cpa_micros, target_roas
  )

  campaign = resource_types.Campaign(
      resource_name=campaign_resource_name,
  )
  setattr(campaign, strategy_field, strategy_value)

  operation = service_types.CampaignOperation(update=campaign)
  operation.update_mask.CopyFrom(
      field_mask_pb2.FieldMask(paths=mask_paths)
  )

  try:
    response = service.mutate_campaigns(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def update_campaign_status(
    customer_id: str,
    campaign_resource_name: str,
    status: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Updates a campaign's status.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Full resource name of the campaign.
      status: New status: ENABLED or PAUSED.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the updated campaign resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")

  campaign = resource_types.Campaign(
      resource_name=campaign_resource_name,
      status=_resolve_enum(
          enum_types.CampaignStatusEnum.CampaignStatus, status, "status"
      ),
  )

  operation = service_types.CampaignOperation(update=campaign)
  operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))

  try:
    response = service.mutate_campaigns(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def update_campaign_geo_target_type(
    customer_id: str,
    campaign_resource_name: str,
    positive_geo_target_type: str | None = None,
    negative_geo_target_type: str | None = None,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Updates a campaign's geo targeting mode (location options).

  Controls whether ads show to people *in* targeted locations vs
  people *in or interested in* targeted locations.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Full resource name of the campaign (e.g.,
        "customers/123/campaigns/456").
      positive_geo_target_type: Targeting mode for included locations.
        PRESENCE_OR_INTEREST - People in, regularly in, or who've shown interest
        in your targeted locations (default). SEARCH_INTEREST - People searching
        for your targeted locations. PRESENCE - People in or regularly in your
        targeted locations only.
      negative_geo_target_type: Targeting mode for excluded locations.
        PRESENCE_OR_INTEREST - Don't show to people in, regularly in, or
        interested in excluded locations. PRESENCE - Don't show to people in or
        regularly in excluded locations.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the updated campaign resource_name.
  """
  if not positive_geo_target_type and not negative_geo_target_type:
    raise ToolError(
        "At least one of positive_geo_target_type or "
        "negative_geo_target_type must be provided."
    )

  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignService")

  campaign = resource_types.Campaign(resource_name=campaign_resource_name)
  field_mask_paths = []

  if positive_geo_target_type:
    pos_type = _resolve_enum(
        enum_types.PositiveGeoTargetTypeEnum.PositiveGeoTargetType,
        positive_geo_target_type,
        "positive_geo_target_type",
    )
    campaign.geo_target_type_setting.positive_geo_target_type = pos_type
    field_mask_paths.append("geo_target_type_setting.positive_geo_target_type")

  if negative_geo_target_type:
    neg_type = _resolve_enum(
        enum_types.NegativeGeoTargetTypeEnum.NegativeGeoTargetType,
        negative_geo_target_type,
        "negative_geo_target_type",
    )
    campaign.geo_target_type_setting.negative_geo_target_type = neg_type
    field_mask_paths.append("geo_target_type_setting.negative_geo_target_type")

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
