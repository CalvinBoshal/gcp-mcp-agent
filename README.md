# GCP FinOps & SecOps Agent (MCP) ☁️🤖

A fully autonomous, Human-in-the-Loop (HITL) AI Agent built to map, audit, and analyze Google Cloud Platform infrastructure. 

Instead of treating LLMs as simple chatbots, this project uses the **Model Context Protocol (FastMCP)** to decouple the AI "brain" from its "hands," equipping it with surgical Python tools to directly interact with GCP APIs.

## 🚀 Key Capabilities
* **Infrastructure Mapping:** Actively indexes active GCP resources via the Cloud Asset API.
* **Security Auditing:** Analyzes IAM policies to flag over-privileged Service Accounts or exposed endpoints.
* **Human-in-the-Loop Execution:** Strict docstring prompt engineering prevents the AI from autonomously pulling massive/sensitive deep configuration payloads without explicit human permission.
* **Reporting:** Dynamically exports clean, pivotable `.csv` audit spreadsheets to the local machine.

## 🛠️ Tech Stack
* **Framework:** FastMCP (Model Context Protocol)
* **Cloud:** Google Cloud Platform (Asset, Resource Manager, and Catalog APIs)
* **Language:** Python 3.10+
* **Security:** Designed for strict Read-Only Service Account Sandboxing

## ⚙️ Quick Start

1. **Clone the repo:**
   ```bash
   git clone https://github.com/CalvinBoshal/gcp-mcp-agent.git
   cd gcp-mcp-agent