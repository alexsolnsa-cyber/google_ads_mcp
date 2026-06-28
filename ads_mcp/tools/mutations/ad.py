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

"""Ad mutation tools for Google Ads API."""

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._ads_api import common_types
from ads_mcp.tools._ads_api import enum_types
from ads_mcp.tools._ads_api import resource_types
from ads_mcp.tools._ads_api import service_types
from ads_mcp.tools.mutations.common import _get_client
from ads_mcp.tools.mutations.common import _handle_google_ads_error
from ads_mcp.tools.mutations.common import _resolve_enum
from google.ads.googleads.errors import GoogleAdsException
from google.protobuf import field_mask_pb2


@mcp.tool()
def create_responsive_search_ad(
    customer_id: str,
    ad_group_resource_name: str,
    headlines: list,
    descriptions: list,
    final_url: str,
    path1: str = "",
    path2: str = "",
    status: str = "ENABLED",
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Creates a Responsive Search Ad in an ad group with optional headline/description pinning.

  Args:
      customer_id: Google Ads customer ID (digits only).
      ad_group_resource_name: Resource name from create_ad_group.
      headlines: List of headlines (3-15, max 30 chars each). Each can be:
        - A string: "headline text" (no pinning)
        - A dict: {"text": "headline text", "pinned_field": "HEADLINE_1"}
          Valid pinned_field values: HEADLINE_1, HEADLINE_2, HEADLINE_3
      descriptions: List of descriptions (2-4, max 90 chars each). Each can be:
        - A string: "description text" (no pinning)
        - A dict: {"text": "description text", "pinned_field": "DESCRIPTION_1"}
          Valid pinned_field values: DESCRIPTION_1, DESCRIPTION_2
      final_url: Landing page URL.
      path1: Display URL path1 (max 15 chars, optional).
      path2: Display URL path2 (max 15 chars, optional).
      status: ENABLED or PAUSED. Default ENABLED.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the ad_group_ad resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupAdService")

  headline_assets = []
  for h in headlines:
    if isinstance(h, str):
      headline_assets.append(common_types.AdTextAsset(text=h))
    else:
      asset = common_types.AdTextAsset(text=h["text"])
      if h.get("pinned_field"):
        asset.pinned_field = _resolve_enum(
            enum_types.ServedAssetFieldTypeEnum.ServedAssetFieldType,
            h["pinned_field"],
            "pinned_field",
        )
      headline_assets.append(asset)

  description_assets = []
  for d in descriptions:
    if isinstance(d, str):
      description_assets.append(common_types.AdTextAsset(text=d))
    else:
      asset = common_types.AdTextAsset(text=d["text"])
      if d.get("pinned_field"):
        asset.pinned_field = _resolve_enum(
            enum_types.ServedAssetFieldTypeEnum.ServedAssetFieldType,
            d["pinned_field"],
            "pinned_field",
        )
      description_assets.append(asset)

  rsa_info = common_types.ResponsiveSearchAdInfo(
      headlines=headline_assets,
      descriptions=description_assets,
  )
  if path1:
    rsa_info.path1 = path1
  if path2:
    rsa_info.path2 = path2

  ad = resource_types.Ad(
      final_urls=[final_url],
      responsive_search_ad=rsa_info,
  )

  ad_group_ad = resource_types.AdGroupAd(
      ad_group=ad_group_resource_name,
      status=_resolve_enum(
          enum_types.AdGroupAdStatusEnum.AdGroupAdStatus, status, "status"
      ),
      ad=ad,
  )

  operation = service_types.AdGroupAdOperation(create=ad_group_ad)
  try:
    response = service.mutate_ad_group_ads(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  resource_name = response.results[0].resource_name
  return {"resource_name": resource_name}


@mcp.tool()
def update_ad_status(
    customer_id: str,
    ad_group_ad_resource_name: str,
    status: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Updates an ad's status (enable or pause).

  Args:
      customer_id: Google Ads customer ID (digits only).
      ad_group_ad_resource_name: Full resource name of the ad
        (e.g., "customers/123/adGroupAds/456~789").
      status: New status: ENABLED or PAUSED.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the updated ad resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupAdService")

  ad_group_ad = resource_types.AdGroupAd(
      resource_name=ad_group_ad_resource_name,
      status=_resolve_enum(
          enum_types.AdGroupAdStatusEnum.AdGroupAdStatus, status, "status"
      ),
  )

  operation = service_types.AdGroupAdOperation(update=ad_group_ad)
  operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))

  try:
    response = service.mutate_ad_group_ads(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def remove_ad(
    customer_id: str,
    ad_group_id: str,
    ad_id: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Removes an ad from an ad group.

  Args:
      customer_id: Google Ads customer ID (digits only).
      ad_group_id: Ad group ID (digits only).
      ad_id: Ad ID to remove (digits only).
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the removed resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupAdService")

  resource_name = service.ad_group_ad_path(customer_id, ad_group_id, ad_id)
  operation = service_types.AdGroupAdOperation(remove=resource_name)

  try:
    response = service.mutate_ad_group_ads(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"removed": response.results[0].resource_name}
