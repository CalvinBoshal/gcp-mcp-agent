import os
import csv
# pyrefly: ignore [missing-import]
from fastmcp import FastMCP
from google.cloud import asset_v1
from google.cloud import resourcemanager_v3

# ---------------------------------------------------------------------------
# Asset & Infrastructure Sub-Server
# Mounted by main.py via: mcp.mount("assets", asset_server)
# ---------------------------------------------------------------------------
asset_server = FastMCP("AssetSub")


@asset_server.tool()
def check_status() -> str:
    """Tells the AI if the Asset sub-server is awake and functioning."""
    return "Frugally Asset Engine is awake, secure, and ready for duty!"


@asset_server.tool()
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
        for i, resource in enumerate(page_result):
            if i >= 100:
                resources.append("... (List truncated at 100 items. Be more specific if needed.)")
                break
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


@asset_server.tool()
def get_project_details(project_id: str) -> str:
    """Fetches detailed metadata about a project, including its ID, parent organization/folder, and labels."""
    try:
        client = resourcemanager_v3.ProjectsClient()

        if not project_id.startswith("projects/"):
            project_id = f"projects/{project_id}"

        request = resourcemanager_v3.GetProjectRequest(name=project_id)
        project = client.get_project(request=request)

        parent = project.parent if project.parent else "No parent found (Top Level)"
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


@asset_server.tool()
def get_project_iam_policy(project_id: str) -> str:
    """Fetches the IAM security policies (who has access and what roles) for a specific Google Cloud project."""
    try:
        client = resourcemanager_v3.ProjectsClient()

        # Strip the "projects/" prefix if the AI accidentally includes it
        clean_project_id = project_id.replace("projects/", "")

        # Passing a dictionary is the safest way to call get_iam_policy
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


@asset_server.tool()
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

        # Query for the exact resource by name and pull all fields
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
            return details  # Return immediately after finding the exact match

        return "Resource not found or deep configuration unavailable."

    except Exception as e:
        return f"Error fetching deep config: {str(e)}"


@asset_server.tool()
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

        # Ensure the output directory exists
        directory = os.path.dirname(file_path)
        if directory and not os.path.exists(directory):
            os.makedirs(directory)

        with open(file_path, mode='w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(["Display Name", "Asset Type", "Location", "Labels", "Exact Resource Name"])

            count = 0
            for resource in page_result:
                labels_str = (
                    ", ".join([f"{k}:{v}" for k, v in dict(resource.labels).items()])
                    if resource.labels else "None"
                )
                writer.writerow([
                    resource.display_name or "N/A",
                    resource.asset_type,
                    resource.location or "Global",
                    labels_str,
                    resource.name
                ])
                count += 1

        return f"Success! Exported {count} resources to: {file_path}"

    except Exception as e:
        return f"Error exporting to CSV: {str(e)}"