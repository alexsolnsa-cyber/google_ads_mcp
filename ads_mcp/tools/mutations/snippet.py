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

"""Structured snippet extension mutation tools for Google Ads API."""

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._ads_api import common_types
from ads_mcp.tools._ads_api import enum_types
from ads_mcp.tools._ads_api import resource_types
from ads_mcp.tools._ads_api import service_types
from ads_mcp.tools.mutations.common import _get_client
from ads_mcp.tools.mutations.common import _handle_google_ads_error
from google.ads.googleads.errors import GoogleAdsException


@mcp.tool()
def create_structured_snippet_asset(
    customer_id: str,
    header: str,
    values: list[str],
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Creates a structured snippet asset.

  Structured snippets show a header and list of values below your ad.

  Args:
      customer_id: Google Ads customer ID (digits only).
      header: The snippet header. Must be one of the predefined headers:
        Amenities, Brands, Courses, Degree programs, Destinations,
        Featured hotels, Insurance coverage, Models, Neighborhoods,
        Service catalog, Shows, Styles, Types.
      values: List of values for the header (3-10 values, max 25 chars each).
        Example for "Courses": ["Speaking", "Writing", "Reading", "Listening"]
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the created asset resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AssetService")

  asset = resource_types.Asset(
      structured_snippet_asset=common_types.StructuredSnippetAsset(
          header=header,
          values=values,
      ),
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
def attach_snippet_to_campaign(
    customer_id: str,
    campaign_resource_name: str,
    asset_resource_name: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Attaches a structured snippet asset to a campaign.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Resource name of the campaign.
      asset_resource_name: Resource name from create_structured_snippet_asset.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the created campaign_asset resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignAssetService")

  campaign_asset = resource_types.CampaignAsset(
      campaign=campaign_resource_name,
      asset=asset_resource_name,
      field_type=enum_types.AssetFieldTypeEnum.AssetFieldType.STRUCTURED_SNIPPET,
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
def attach_snippet_to_ad_group(
    customer_id: str,
    ad_group_resource_name: str,
    asset_resource_name: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Attaches a structured snippet asset to an ad group.

  Args:
      customer_id: Google Ads customer ID (digits only).
      ad_group_resource_name: Resource name of the ad group.
      asset_resource_name: Resource name from create_structured_snippet_asset.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the created ad_group_asset resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupAssetService")

  ad_group_asset = resource_types.AdGroupAsset(
      ad_group=ad_group_resource_name,
      asset=asset_resource_name,
      field_type=enum_types.AssetFieldTypeEnum.AssetFieldType.STRUCTURED_SNIPPET,
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
def remove_snippet_from_campaign(
    customer_id: str,
    campaign_asset_resource_name: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Removes a structured snippet from a campaign.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_asset_resource_name: Full resource name of the campaign asset.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the removed resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignAssetService")
  operation = service_types.CampaignAssetOperation(remove=campaign_asset_resource_name)
  try:
    response = service.mutate_campaign_assets(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"removed": response.results[0].resource_name}


@mcp.tool()
def remove_snippet_from_ad_group(
    customer_id: str,
    ad_group_asset_resource_name: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Removes a structured snippet from an ad group.

  Args:
      customer_id: Google Ads customer ID (digits only).
      ad_group_asset_resource_name: Full resource name of the ad group asset.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the removed resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupAssetService")
  operation = service_types.AdGroupAssetOperation(remove=ad_group_asset_resource_name)
  try:
    response = service.mutate_ad_group_assets(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"removed": response.results[0].resource_name}
