# pyrefly: ignore [missing-import]
from google.cloud import billing_v1
from fastmcp import FastMCP

# ---------------------------------------------------------------------------
# Billing Sub-Server
# Mounted by main.py via: mcp.mount("billing", billing_server)
# ---------------------------------------------------------------------------
billing_server = FastMCP("BillingSub")


@billing_server.tool()
def get_billing_accounts() -> str:
    """Fetches the Google Cloud billing accounts associated with the credentials."""
    try:
        client = billing_v1.CloudBillingClient()
        request = billing_v1.ListBillingAccountsRequest()
        page_result = client.list_billing_accounts(request=request)

        accounts = []
        for response in page_result:
            accounts.append(f"Account Name: {response.display_name}, ID: {response.name}")

        if not accounts:
            return "No billing accounts found for these credentials."

        return "Found the following Google Cloud billing accounts:\n" + "\n".join(accounts)

    except Exception as e:
        return f"Error connecting to Google Cloud: {str(e)}"


@billing_server.tool()
def get_billing_projects(account_id: str) -> str:
    """Fetches the Google Cloud projects attached to a specific billing account ID."""
    try:
        client = billing_v1.CloudBillingClient()

        # Google's API expects the format "billingAccounts/YOUR_ID"
        if not account_id.startswith("billingAccounts/"):
            account_id = f"billingAccounts/{account_id}"

        request = billing_v1.ListProjectBillingInfoRequest(name=account_id)
        page_result = client.list_project_billing_info(request=request)

        projects = []
        for response in page_result:
            projects.append(
                f"Project ID: {response.project_id} (Billing Enabled: {response.billing_enabled})"
            )

        if not projects:
            return "No projects found linked to this billing account."

        return "Found the following connected projects:\n" + "\n".join(projects)

    except Exception as e:
        return f"Error fetching projects: {str(e)}"
