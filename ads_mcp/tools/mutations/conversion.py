"""Conversion action management tools for Google Ads API."""

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._ads_api import enum_types, resource_types, service_types
from ads_mcp.tools.mutations.common import _get_client, _handle_google_ads_error, _resolve_enum
from google.ads.googleads.errors import GoogleAdsException
from google.protobuf import field_mask_pb2


@mcp.tool()
def create_conversion_action(customer_id: str, name: str, category: str = "PURCHASE", conversion_type: str = "WEBPAGE", value_per_conversion: float | None = None, login_customer_id: str | None = None) -> dict[str, str]:
  """Creates a conversion action. Args: customer_id: Google Ads ID. name: Action name. category: PURCHASE/SIGNUP/LEAD/PAGE_VIEW/DEFAULT/OTHER. conversion_type: WEBPAGE/AD_CALL/CLICK_TO_CALL/IMPORT. value_per_conversion: Optional fixed value. login_customer_id: MCC ID."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("ConversionActionService")
  action = resource_types.ConversionAction(name=name, category=_resolve_enum(enum_types.ConversionActionCategoryEnum.ConversionActionCategory, category, "category"), type_=_resolve_enum(enum_types.ConversionActionTypeEnum.ConversionActionType, conversion_type, "conversion_type"), status=enum_types.ConversionActionStatusEnum.ConversionActionStatus.ENABLED)
  if value_per_conversion is not None:
    action.value_settings.default_value = value_per_conversion
    action.value_settings.always_use_default_value = True
  operation = service_types.ConversionActionOperation(create=action)
  try:
    response = service.mutate_conversion_actions(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def update_conversion_action_status(customer_id: str, conversion_action_resource_name: str, status: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Updates a conversion action's status. Args: customer_id: Google Ads ID. conversion_action_resource_name: Full resource name. status: ENABLED/PAUSED/HIDDEN. login_customer_id: MCC ID."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("ConversionActionService")
  action = resource_types.ConversionAction(resource_name=conversion_action_resource_name, status=_resolve_enum(enum_types.ConversionActionStatusEnum.ConversionActionStatus, status, "status"))
  operation = service_types.ConversionActionOperation(update=action)
  operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
  try:
    response = service.mutate_conversion_actions(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}
