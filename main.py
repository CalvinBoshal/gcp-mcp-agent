import os
from fastmcp import FastMCP
from src import asset_server, billing_server

# ---------------------------------------------------------------------------
# 1. Resolve credentials — must happen before any Google client is instantiated
# ---------------------------------------------------------------------------
key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcp-service-account.json")
credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), key_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# ---------------------------------------------------------------------------
# 2. Create the root MCP server
# ---------------------------------------------------------------------------
mcp = FastMCP("BillingAgent")

# ---------------------------------------------------------------------------
# 3. Health-check tool on the root server
# ---------------------------------------------------------------------------
@mcp.tool()
def check_status() -> str:
    """Tells the AI if the root agent is awake and functioning."""
    return "The BillingAgent is awake, secure, and ready for duty!"

# ---------------------------------------------------------------------------
# 4. Mount sub-servers (tools become available with their natural names)
# ---------------------------------------------------------------------------

mcp.mount(asset_server, namespace="assets")
mcp.mount(billing_server, namespace="billing")

# ---------------------------------------------------------------------------
# 5. Entry point
# ---------------------------------------------------------------------------
if __name__ == "__main__":
    mcp.run()
