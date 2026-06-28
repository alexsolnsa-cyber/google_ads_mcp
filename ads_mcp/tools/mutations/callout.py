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

"""Callout extension mutation tools for Google Ads API."""

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._ads_api import common_types
from ads_mcp.tools._ads_api import enum_types
from ads_mcp.tools._ads_api import resource_types
from ads_mcp.tools._ads_api import service_types
from ads_mcp.tools.mutations.common import _get_client
from ads_mcp.tools.mutations.common import _handle_google_ads_error
from google.ads.googleads.errors import GoogleAdsException


@mcp.tool()
def create_callout_asset(
    customer_id: str,
    callout_text: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Creates a callout asset (short text shown below ads).

  Args:
      customer_id: Google Ads customer ID (digits only).
      callout_text: The callout text (max 25 chars, e.g., "اختبار مجاني",
        "تقييم فوري", "24/7 Support").
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the created asset resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AssetService")

  asset = resource_types.Asset(
      callout_asset=common_types.CalloutAsset(callout_text=callout_text),
  )

  operation = service_types.AssetOperation(create=asset)

  try:
    response = service.mutate_assets(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def attach_callout_to_campaign(
    customer_id: str,
    campaign_resource_name: str,
    asset_resource_name: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Attaches a callout asset to a campaign.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Resource name of the campaign.
      asset_resource_name: Resource name of the callout asset
        from create_callout_asset.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the created campaign_asset resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignAssetService")

  campaign_asset = resource_types.CampaignAsset(
      campaign=campaign_resource_name,
      asset=asset_resource_name,
      field_type=enum_types.AssetFieldTypeEnum.AssetFieldType.CALLOUT,
  )

  operation = service_types.CampaignAssetOperation(create=campaign_asset)

  try:
    response = service.mutate_campaign_assets(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def attach_callout_to_ad_group(
    customer_id: str,
    ad_group_resource_name: str,
    asset_resource_name: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Attaches a callout asset to an ad group.

  Args:
      customer_id: Google Ads customer ID (digits only).
      ad_group_resource_name: Resource name of the ad group.
      asset_resource_name: Resource name of the callout asset
        from create_callout_asset.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the created ad_group_asset resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupAssetService")

  ad_group_asset = resource_types.AdGroupAsset(
      ad_group=ad_group_resource_name,
      asset=asset_resource_name,
      field_type=enum_types.AssetFieldTypeEnum.AssetFieldType.CALLOUT,
  )

  operation = service_types.AdGroupAssetOperation(create=ad_group_asset)

  try:
    response = service.mutate_ad_group_assets(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def remove_callout_from_campaign(
    customer_id: str,
    campaign_asset_resource_name: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Removes a callout from a campaign.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_asset_resource_name: Full resource name of the campaign asset.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the removed resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignAssetService")

  operation = service_types.CampaignAssetOperation(
      remove=campaign_asset_resource_name
  )

  try:
    response = service.mutate_campaign_assets(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"removed": response.results[0].resource_name}


@mcp.tool()
def remove_callout_from_ad_group(
    customer_id: str,
    ad_group_asset_resource_name: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Removes a callout from an ad group.

  Args:
      customer_id: Google Ads customer ID (digits only).
      ad_group_asset_resource_name: Full resource name of the ad group asset.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the removed resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupAssetService")

  operation = service_types.AdGroupAssetOperation(
      remove=ad_group_asset_resource_name
  )

  try:
    response = service.mutate_ad_group_assets(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"removed": response.results[0].resource_name}
