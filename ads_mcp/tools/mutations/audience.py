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

"""Audience segment mutation tools for Google Ads API."""

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
def add_audience_to_campaign(
    customer_id: str,
    campaign_resource_name: str,
    audience_resource_name: str,
    bid_modifier: float | None = None,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Adds an audience segment to a campaign (observation or targeting mode).

  Use GAQL to find audience resource names:
  SELECT user_list.resource_name, user_list.name FROM user_list
  SELECT user_interest.resource_name, user_interest.name FROM user_interest

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_resource_name: Resource name of the campaign.
      audience_resource_name: Resource name of the audience segment
        (e.g., "customers/123/userLists/456" for remarketing lists,
        or "customers/123/userInterests/789" for in-market/affinity).
      bid_modifier: Optional bid modifier (e.g., 1.2 = +20%, 0.8 = -20%).
        Only applies in Observation mode.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the created criterion resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignCriterionService")

  # Determine audience type from resource name
  if "userLists" in audience_resource_name:
    criterion = resource_types.CampaignCriterion(
        campaign=campaign_resource_name,
        user_list=common_types.UserListInfo(
            user_list=audience_resource_name,
        ),
    )
  elif "userInterests" in audience_resource_name:
    criterion = resource_types.CampaignCriterion(
        campaign=campaign_resource_name,
        user_interest=common_types.UserInterestInfo(
            user_interest_category=audience_resource_name,
        ),
    )
  else:
    criterion = resource_types.CampaignCriterion(
        campaign=campaign_resource_name,
        audience=common_types.AudienceInfo(
            audience=audience_resource_name,
        ),
    )

  if bid_modifier is not None:
    criterion.bid_modifier = bid_modifier

  operation = service_types.CampaignCriterionOperation(create=criterion)

  try:
    response = service.mutate_campaign_criteria(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def add_audience_to_ad_group(
    customer_id: str,
    ad_group_resource_name: str,
    audience_resource_name: str,
    bid_modifier: float | None = None,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Adds an audience segment to an ad group.

  Args:
      customer_id: Google Ads customer ID (digits only).
      ad_group_resource_name: Resource name of the ad group.
      audience_resource_name: Resource name of the audience segment
        (e.g., "customers/123/userLists/456" for remarketing lists,
        or "customers/123/userInterests/789" for in-market/affinity).
      bid_modifier: Optional bid modifier (e.g., 1.2 = +20%, 0.8 = -20%).
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the created criterion resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupCriterionService")

  if "userLists" in audience_resource_name:
    criterion = resource_types.AdGroupCriterion(
        ad_group=ad_group_resource_name,
        user_list=common_types.UserListInfo(
            user_list=audience_resource_name,
        ),
    )
  elif "userInterests" in audience_resource_name:
    criterion = resource_types.AdGroupCriterion(
        ad_group=ad_group_resource_name,
        user_interest=common_types.UserInterestInfo(
            user_interest_category=audience_resource_name,
        ),
    )
  else:
    criterion = resource_types.AdGroupCriterion(
        ad_group=ad_group_resource_name,
        audience=common_types.AudienceInfo(
            audience=audience_resource_name,
        ),
    )

  if bid_modifier is not None:
    criterion.bid_modifier = bid_modifier

  operation = service_types.AdGroupCriterionOperation(create=criterion)

  try:
    response = service.mutate_ad_group_criteria(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def remove_audience_from_campaign(
    customer_id: str,
    campaign_id: str,
    criterion_id: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Removes an audience segment from a campaign.

  Args:
      customer_id: Google Ads customer ID (digits only).
      campaign_id: Campaign ID (digits only).
      criterion_id: Criterion ID of the audience to remove.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the removed resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignCriterionService")

  resource_name = service.campaign_criterion_path(
      customer_id, campaign_id, criterion_id
  )
  operation = service_types.CampaignCriterionOperation(remove=resource_name)

  try:
    response = service.mutate_campaign_criteria(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"removed": response.results[0].resource_name}


@mcp.tool()
def remove_audience_from_ad_group(
    customer_id: str,
    ad_group_id: str,
    criterion_id: str,
    login_customer_id: str | None = None,
) -> dict[str, str]:
  """Removes an audience segment from an ad group.

  Args:
      customer_id: Google Ads customer ID (digits only).
      ad_group_id: Ad group ID (digits only).
      criterion_id: Criterion ID of the audience to remove.
      login_customer_id: MCC account ID if customer is managed.

  Returns:
      Dict with the removed resource_name.
  """
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupCriterionService")

  resource_name = service.ad_group_criterion_path(
      customer_id, ad_group_id, criterion_id
  )
  operation = service_types.AdGroupCriterionOperation(remove=resource_name)

  try:
    response = service.mutate_ad_group_criteria(
        customer_id=customer_id, operations=[operation]
    )
  except GoogleAdsException as e:
    _handle_google_ads_error(e)

  return {"removed": response.results[0].resource_name}
