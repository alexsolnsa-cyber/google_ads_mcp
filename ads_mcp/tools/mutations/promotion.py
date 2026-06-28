"""Promotion extension tools for Google Ads API."""

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._ads_api import common_types, enum_types, resource_types, service_types
from ads_mcp.tools.mutations.common import _get_client, _handle_google_ads_error, _resolve_enum
from google.ads.googleads.errors import GoogleAdsException


@mcp.tool()
def create_promotion_asset(customer_id: str, promotion_target: str, final_url: str, percent_off: int | None = None, money_amount_off_micros: int | None = None, money_amount_off_currency: str = "SAR", language_code: str = "ar", start_date: str = "", end_date: str = "", login_customer_id: str | None = None) -> dict[str, str]:
  """Creates a promotion extension. Args: customer_id: Google Ads ID. promotion_target: Promo text. final_url: URL. percent_off: % discount. money_amount_off_micros: Fixed discount. money_amount_off_currency: Currency. language_code: ar/en. start_date/end_date: YYYY-MM-DD. login_customer_id: MCC ID."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AssetService")
  promo = common_types.PromotionAsset(promotion_target=promotion_target, language_code=language_code)
  if percent_off: promo.percent_off = percent_off
  elif money_amount_off_micros: promo.money_amount_off = common_types.Money(amount_micros=money_amount_off_micros, currency_code=money_amount_off_currency)
  if start_date: promo.start_date = start_date
  if end_date: promo.end_date = end_date
  asset = resource_types.Asset(promotion_asset=promo, final_urls=[final_url])
  operation = service_types.AssetOperation(create=asset)
  try:
    response = service.mutate_assets(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def attach_promotion_to_campaign(customer_id: str, campaign_resource_name: str, asset_resource_name: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Attaches a promotion to a campaign."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignAssetService")
  operation = service_types.CampaignAssetOperation(create=resource_types.CampaignAsset(campaign=campaign_resource_name, asset=asset_resource_name, field_type=enum_types.AssetFieldTypeEnum.AssetFieldType.PROMOTION))
  try:
    response = service.mutate_campaign_assets(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def attach_promotion_to_ad_group(customer_id: str, ad_group_resource_name: str, asset_resource_name: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Attaches a promotion to an ad group."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("AdGroupAssetService")
  operation = service_types.AdGroupAssetOperation(create=resource_types.AdGroupAsset(ad_group=ad_group_resource_name, asset=asset_resource_name, field_type=enum_types.AssetFieldTypeEnum.AssetFieldType.PROMOTION))
  try:
    response = service.mutate_ad_group_assets(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def remove_promotion_from_campaign(customer_id: str, campaign_asset_resource_name: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Removes a promotion from a campaign."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("CampaignAssetService")
  operation = service_types.CampaignAssetOperation(remove=campaign_asset_resource_name)
  try:
    response = service.mutate_campaign_assets(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"removed": response.results[0].resource_name}
