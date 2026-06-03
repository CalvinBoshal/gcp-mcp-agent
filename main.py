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

# ---------------------------------------------------------------------
# # 3.5. Resource Layer — Exposing the Ambient Environment Map
# ---------------------------------------------------------------------
@mcp.resource("frugally://gcp/topology-map")
def get_gcp_topology() -> str:
    """
    Exposes a read-only, structural map of the active GCP architecture.
    Provides the AI with continuous background awareness of managed assets.
    """
    import json
    
    # In production, this pulls from a lightweight local cache database.
    # It acts as the "printed floor plan" for our Agentic Architect.
    topology = {
        "governed_environment": "GCP Multi-Project Cluster",
        "status": "Healthy",
        "active_projects": [
            {
                "id": "billing-agent-lab",
                "billing_enabled": True,
                "monitored_services": ["Compute Engine", "Cloud Storage", "Vertex AI"],
                "regions": ["us-central1", "europe-west1"]
            },
            {
                "id": "project-af726956-0770-41a5-849",
                "billing_enabled": True,
                "monitored_services": ["Compute Engine", "BigQuery"],
                "regions": ["us-central1"]
            }
        ],
        "architectural_policies": {
            "approved_compute_zones": ["us-central1-a", "europe-west1-b"],
            "max_allowed_idle_days": 7,
            "enforced_tags": ["env:production", "cost-center:finops"]
        }
    }
    
    return json.dumps(topology, indent=2)

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
