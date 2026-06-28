"""Campaign experiment tools for Google Ads API."""

from ads_mcp.coordinator import mcp_server as mcp
from ads_mcp.tools._ads_api import enum_types, resource_types, service_types
from ads_mcp.tools.mutations.common import _get_client, _handle_google_ads_error
from google.ads.googleads.errors import GoogleAdsException
from google.protobuf import field_mask_pb2


@mcp.tool()
def create_experiment(customer_id: str, name: str, description: str = "", suffix: str = " - Experiment", experiment_type: str = "SEARCH_CUSTOM", start_date: str = "", end_date: str = "", login_customer_id: str | None = None) -> dict[str, str]:
  """Creates a campaign experiment. Args: customer_id: Google Ads ID. name: Experiment name. description: Optional. suffix: Added to experiment campaign name. experiment_type: SEARCH_CUSTOM/DISPLAY_CUSTOM. start_date/end_date: YYYY-MM-DD. login_customer_id: MCC ID."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("ExperimentService")
  experiment = resource_types.Experiment(name=name, suffix=suffix, type_=enum_types.ExperimentTypeEnum.ExperimentType.SEARCH_CUSTOM if experiment_type == "SEARCH_CUSTOM" else enum_types.ExperimentTypeEnum.ExperimentType.DISPLAY_CUSTOM, status=enum_types.ExperimentStatusEnum.ExperimentStatus.SETUP)
  if description: experiment.description = description
  if start_date: experiment.start_date = start_date
  if end_date: experiment.end_date = end_date
  operation = service_types.ExperimentOperation(create=experiment)
  try:
    response = service.mutate_experiments(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}


@mcp.tool()
def update_experiment_status(customer_id: str, experiment_resource_name: str, status: str, login_customer_id: str | None = None) -> dict[str, str]:
  """Updates experiment status. Args: customer_id: Google Ads ID. experiment_resource_name: Full resource name. status: ENABLED/PROMOTED/REMOVED/GRADUATED. login_customer_id: MCC ID."""
  ads_client = _get_client(login_customer_id)
  service = ads_client.get_service("ExperimentService")
  experiment = resource_types.Experiment(resource_name=experiment_resource_name, status=enum_types.ExperimentStatusEnum.ExperimentStatus[status.upper()])
  operation = service_types.ExperimentOperation(update=experiment)
  operation.update_mask.CopyFrom(field_mask_pb2.FieldMask(paths=["status"]))
  try:
    response = service.mutate_experiments(customer_id=customer_id, operations=[operation])
  except GoogleAdsException as e:
    _handle_google_ads_error(e)
  return {"resource_name": response.results[0].resource_name}
