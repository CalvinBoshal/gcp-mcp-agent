import os
import csv
from fastmcp import FastMCP
from google.cloud import billing_v1
from google.cloud import asset_v1  # <-- NEW
from google.cloud import resourcemanager_v3 # <-- NEW


# 1. Show the script where the "Passport" is located
# Use absolute path to ensure it's found regardless of where the server is run from
key_path = os.getenv("GOOGLE_APPLICATION_CREDENTIALS", "gcp-service-account.json")
credentials_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), key_path)
os.environ["GOOGLE_APPLICATION_CREDENTIALS"] = credentials_path

# 2. Initialize the Server
mcp = FastMCP("BillingAgent")

# 3. Our original test tool
@mcp.tool()
def check_status() -> str:
    """Tells the AI if the Agent is awake and functioning."""
    return "The BillingAgent is awake, secure, and ready for duty!"

# 4. NEW TOOL: The Google Cloud Billing Connector
@mcp.tool()
def get_billing_accounts() -> str:
    """Fetches the Google Cloud billing accounts associated with the credentials."""
    try:
        # Create a client that uses our passport to talk to Google
        client = billing_v1.CloudBillingClient()
        
        # Ask Google for a list of our billing accounts
        request = billing_v1.ListBillingAccountsRequest()
        page_result = client.list_billing_accounts(request=request)

        # Organize the results
        accounts = []
        for response in page_result:
            accounts.append(f"Account Name: {response.display_name}, ID: {response.name}")

        if not accounts:
            return "No billing accounts found for these credentials."

        return "Found the following Google Cloud billing accounts:\n" + "\n".join(accounts)
        
    except Exception as e:
        return f"Error connecting to Google Cloud: {str(e)}"

# 5. NEW TOOL: See what projects are spending money on this account
@mcp.tool()
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
            projects.append(f"Project ID: {response.project_id} (Billing Enabled: {response.billing_enabled})")

        if not projects:
            return "No projects found linked to this billing account."

        return "Found the following connected projects:\n" + "\n".join(projects)
        
    except Exception as e:
        return f"Error fetching projects: {str(e)}"

# 6. NEW TOOL 1: The Lightweight Indexer (Safe for AI memory)
@mcp.tool()
def list_project_resources(project_id: str) -> str:
    """
    Fetches a lightweight list of active resources in a Google Cloud project.
    
    INSTRUCTION FOR AI: After receiving this list, quickly analyze it. If you see 
    any resources that are typically high-cost or high-security risks (like 
    Databases, Load Balancers, or large VMs), proactively alert the human and 
    tell them WHY it looks suspicious. Do NOT use the deep fetch tool on them 
    until the human explicitly gives you permission.
    """
    try:
        client = asset_v1.AssetServiceClient()
        
        if not project_id.startswith("projects/"):
            project_id = f"projects/{project_id}"
            
        request = asset_v1.SearchAllResourcesRequest(scope=project_id)
        page_result = client.search_all_resources(request=request)

        resources = []
        # We can safely bump this back up to 100 because the text is very short!
        for i, resource in enumerate(page_result):
            if i >= 100:
                resources.append("... (List truncated at 100 items. Be more specific if needed.)")
                break
            
            # We must give the AI the exact, raw Google "name" string so it can use it later
            resources.append(
                f"Display Name: {resource.display_name or 'N/A'} | Type: {resource.asset_type}\n"
                f"Exact Resource Name: {resource.name}\n"
                f"---"
            )

        if not resources:
            return f"No active resources found in {project_id}."

        return f"Resource List for {project_id}:\n\n" + "\n".join(resources)
        
    except Exception as e:
        return f"Error fetching resource list: {str(e)}"

# 7. NEW TOOL: The Project Master Key
@mcp.tool()
def get_project_details(project_id: str) -> str:
    """Fetches detailed metadata about a project, including its ID, parent organization/folder, and labels."""
    try:
        client = resourcemanager_v3.ProjectsClient()
        
        # Ensure the ID is in the correct format (projects/ID)
        if not project_id.startswith("projects/"):
            project_id = f"projects/{project_id}"
            
        request = resourcemanager_v3.GetProjectRequest(name=project_id)
        project = client.get_project(request=request)

        # Extract parent (Organization or Folder)
        parent = project.parent if project.parent else "No parent found (Top Level)"
        # Extract labels if they exist
        labels = dict(project.labels) if project.labels else "None"

        return (
            f"Project Details for {project.project_id}:\n"
            f"Display Name: {project.display_name}\n"
            f"Status: {project.state}\n"
            f"Parent: {parent}\n"
            f"Create Time: {project.create_time}\n"
            f"Labels: {labels}"
        )

    except Exception as e:
        return f"Error fetching project details: {str(e)}"

# 8. NEW TOOL: The Policy Auditor (IAM Security)
@mcp.tool()
def get_project_iam_policy(project_id: str) -> str:
    """Fetches the IAM security policies (who has access and what roles) for a specific Google Cloud project."""
    try:
        client = resourcemanager_v3.ProjectsClient()
        
        # Strip the "projects/" prefix if the AI accidentally includes it
        clean_project_id = project_id.replace("projects/", "")
        
        # The AI autocomplete made a slight error here, passing a dictionary is the safest way
        request = {"resource": f"projects/{clean_project_id}"}
        policy = client.get_iam_policy(request=request)

        bindings_info = []
        for binding in policy.bindings:
            role = binding.role
            members = ", ".join(binding.members)
            bindings_info.append(f"Role: {role}\nMembers: {members}\n---")

        if not bindings_info:
            return f"No IAM policy bindings found for {clean_project_id}."

        return f"IAM Security Policies for {clean_project_id}:\n\n" + "\n".join(bindings_info)
        
    except Exception as e:
        return f"Error fetching IAM policy: {str(e)}"

# 9. NEW TOOL 2: The Deep Fetcher (Human-in-the-Loop)
@mcp.tool()
def get_deep_resource_config(project_id: str, exact_resource_name: str) -> str:
    """
    Fetches the deep JSON configuration for ONE specific resource.
    CRITICAL INSTRUCTION: ONLY use this tool if the human explicitly asks you 
    to check the "deep config", "size", or "details" of a specific resource. 
    Do NOT use this tool autonomously.
    """
    try:
        client = asset_v1.AssetServiceClient()
        
        if not project_id.startswith("projects/"):
            project_id = f"projects/{project_id}"

        # We query Google for this exact resource name, and use the magic read_mask="*"
        request = asset_v1.SearchAllResourcesRequest(
            scope=project_id,
            query=f'name="{exact_resource_name}"',
            read_mask="*"
        )
        page_result = client.search_all_resources(request=request)
        
        for resource in page_result:
            details = f"Deep Config for {resource.display_name or resource.name}:\n"
            
            if resource.additional_attributes:
                attrs = {k: str(v) for k, v in resource.additional_attributes.items()}
                details += f"Settings: {attrs}\n"
            else:
                details += "No deep configuration attributes available for this specific resource type."
                
            return details # Return immediately after finding the exact match

        return "Resource not found or deep configuration unavailable."
        
    except Exception as e:
        return f"Error fetching deep config: {str(e)}"
    
# 8. NEW TOOL: The Enterprise CSV Exporter (CORRECTED)
@mcp.tool()
def export_resources_to_csv(project_id: str, file_path: str) -> str:
    """
    Exports the complete list of project resources to a local CSV file on the user's computer.
    Use this when the human asks for a spreadsheet, report, or CSV export.
    """
    try:
        client = asset_v1.AssetServiceClient()
        
        if not project_id.startswith("projects/"):
            project_id = f"projects/{project_id}"
            
        request = asset_v1.SearchAllResourcesRequest(scope=project_id)
        page_result = client.search_all_resources(request=request)

        # Ensure the folder exists if the user provides a deep path
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        # Open the file and write the data
        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            
            # 1. Write the Header Row
            writer.writerow(["Display Name", "Asset Type", "Location", "Labels", "Exact Resource Name"])

            count = 0
            # 2. Write the Data Rows
            for resource in page_result:
                # PROPERLY CASTING THE LABELS HERE:
                labels_str = ", ".join([f"{k}:{v}" for k, v in dict(resource.labels).items()]) if resource.labels else "None"
                
                writer.writerow([
                    resource.display_name or "N/A",
                    resource.asset_type,
                    resource.location or "Global",
                    labels_str,
                    resource.name
                ])
                count += 1

        return f"Success! I have exported {count} resources to the file: {file_path}"
        
    except Exception as e:
        return f"Error exporting to CSV: {str(e)}"

if __name__ == "__main__":
    mcp.run()
