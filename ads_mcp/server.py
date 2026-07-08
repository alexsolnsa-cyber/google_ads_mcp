"""The server for the Google Ads API MCP."""

import asyncio
import os

from ads_mcp.coordinator import mcp_server
from ads_mcp.scripts.generate_views import update_views_yaml
from ads_mcp.tools import accounts, docs, keyword_planner, reporting
from ads_mcp.tools._utils import get_ads_client
import dotenv

dotenv.load_dotenv()

tools = [reporting, accounts, docs, keyword_planner]

if os.getenv("ADS_MCP_ENABLE_MUTATIONS", "false").lower() == "true":
  from ads_mcp.tools import mutations
  tools.extend([
      mutations.budget, mutations.campaign, mutations.ad_group,
      mutations.ad, mutations.criterion, mutations.sitelink,
      mutations.callout, mutations.snippet, mutations.schedule,
      mutations.audience, mutations.demographic, mutations.labels,
      mutations.shared_lists, mutations.promotion, mutations.conversion,
      mutations.experiment,
  ])


def main():
  asyncio.run(update_views_yaml())
  get_ads_client()
  port = int(os.environ.get("PORT", 8000))
  print(f"mcp server starting on port {port}...")
  mcp_server.run(transport="streamable-http", host="0.0.0.0", port=port, show_banner=False)


if __name__ == "__main__":
  main()
