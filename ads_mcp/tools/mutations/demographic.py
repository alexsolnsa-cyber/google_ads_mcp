"""Demographic targeting tools for Google Ads API."""

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._ads_api import common_types, enum_types, resource_types, service_types
from ads_mcp.tools.mutations.common import _get_client, _handle_google_ads_error, _resolve_enum
from google.ads.googleads.errors import GoogleAdsException


@mcp.tool()
def set_age_targeting(customer_id: str, campaign_resource_name: str, age_range: str, bid_modifier: float | None = None, negative: bool = False, login_customer_id: str | None = None) -> dict[str, str]:
  """Adds age range targeting. Args: customer_id: Google Ads customer ID. campaign_resource_name: Campaign resource. age_range: AGE_RANGE_18_24/AGE_RANGE_25_34/AGE_RANGE_35_44/AGE_RANGE_45_54/AGE_RANGE_55_64/AGE_RANGE_65_UP/AGE_RANGE_UNDETERMINED. bid_modifier: Optional (1.2=+20%). negative: True to exclude. login_customer_id: MCC ID if managed."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignCriterionService")
  criterion = resource_types.CampaignCriterion(campaign=campaign_resource_name, negative=negative, age_range=common_types.AgeRangeInfo(type_=_resolve_enum(enum_types.AgeRangeTypeEnum.AgeRangeType, age_range, "age_range")))
  if bid_modifier is not None: criterion.bid_modifier = bid_modifier
  operation = service_types.CampaignCriterionOperation(create=criterion)
  try:
    response = service.mutate_campaign_criteria(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def set_gender_targeting(customer_id: str, campaign_resource_name: str, gender: str, bid_modifier: float | None = None, negative: bool = False, login_customer_id: str | None = None) -> dict[str, str]:
  """Adds gender targeting. Args: customer_id: Google Ads customer ID. campaign_resource_name: Campaign resource. gender: MALE/FEMALE/UNDETERMINED. bid_modifier: Optional. negative: True to exclude. login_customer_id: MCC ID if managed."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignCriterionService")
  criterion = resource_types.CampaignCriterion(campaign=campaign_resource_name, negative=negative, gender=common_types.GenderInfo(type_=_resolve_enum(enum_types.GenderTypeEnum.GenderType, gender, "gender")))
  if bid_modifier is not None: criterion.bid_modifier = bid_modifier
  operation = service_types.CampaignCriterionOperation(create=criterion)
  try:
    response = service.mutate_campaign_criteria(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def set_income_targeting(customer_id: str, campaign_resource_name: str, income_range: str, bid_modifier: float | None = None, negative: bool = False, login_customer_id: str | None = None) -> dict[str, str]:
  """Adds income range targeting. Args: customer_id: Google Ads customer ID. campaign_resource_name: Campaign resource. income_range: INCOME_RANGE_0_50/50_60/60_70/70_80/80_90/90_100/UNDETERMINED. bid_modifier: Optional. negative: True to exclude. login_customer_id: MCC ID if managed."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignCriterionService")
  criterion = resource_types.CampaignCriterion(campaign=campaign_resource_name, negative=negative, income_range=common_types.IncomeRangeInfo(type_=_resolve_enum(enum_types.IncomeRangeTypeEnum.IncomeRangeType, income_range, "income_range")))
  if bid_modifier is not None: criterion.bid_modifier = bid_modifier
  operation = service_types.CampaignCriterionOperation(create=criterion)
  try:
    response = service.mutate_campaign_criteria(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def set_parental_status_targeting(customer_id: str, campaign_resource_name: str, parental_status: str, bid_modifier: float | None = None, negative: bool = False, login_customer_id: str | None = None) -> dict[str, str]:
  """Adds parental status targeting. Args: customer_id: Google Ads customer ID. campaign_resource_name: Campaign resource. parental_status: PARENT/NOT_A_PARENT/UNDETERMINED. bid_modifier: Optional. negative: True to exclude. login_customer_id: MCC ID if managed."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignCriterionService")
  criterion = resource_types.CampaignCriterion(campaign=campaign_resource_name, negative=negative, parental_status=common_types.ParentalStatusInfo(type_=_resolve_enum(enum_types.ParentalStatusTypeEnum.ParentalStatusType, parental_status, "parental_status")))
  if bid_modifier is not None: criterion.bid_modifier = bid_modifier
  operation = service_types.CampaignCriterionOperation(create=criterion)
  try:
    response = service.mutate_campaign_criteria(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}
