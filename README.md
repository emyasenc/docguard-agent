# 🛡️ DocGuard Agent

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg)](LICENSE)
[![Python](https://img.shields.io/badge/Python-3.11%2B-blue)](https://python.org)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.115-green)](https://fastapi.tiangolo.com)
[![Deployed on Render](https://img.shields.io/badge/Deployed-Render-purple)](https://render.com)

DocGuard is an **AI agent** that acts as a guardian for your data pipelines. It automatically validates code and documentation against your **DataHub metadata**—catching issues before they break your production systems.

## 🚀 Why DocGuard?

Data teams spend up to **30% of their time** fixing broken pipelines caused by:
- ❌ SQL queries referencing non-existent tables
- ❌ Using deprecated functions
- ❌ Outdated or missing documentation

**DocGuard fixes this.** It runs on every Pull Request (PR), scanning your code and docs, and posts a comment with clear issues and suggestions.

### 🎯 How It Works

1.  **You open a Pull Request** in your GitHub repository.
2.  **DocGuard's webhook is triggered** and analyzes the changed files.
3.  It queries **DataHub** to get the "source of truth" for your data stack (schemas, tables, and columns).
4.  It validates your code and documentation against this metadata:
    -   **Linter Agent**: Flags unknown tables, `SELECT *` queries, and `DELETE` without `WHERE`.
    -   **Doc Validator Agent**: Checks for missing documentation sections and deprecated terms.
5.  **DocGuard posts a comment** on your PR with a detailed report and actionable suggestions.

## ✨ Features

-   **🔍 Code Linting**: Validates SQL, Python, and other code against DataHub's real metadata.
-   **📝 Documentation Validation**: Checks your `.md` files for required sections and deprecated terminology.
-   **🤖 GitHub Integration**: Automatically comments on Pull Requests with a clear report.
-   **⚙️ Production-Ready**: Built with FastAPI, async Python, and comprehensive error handling.
-   **🧪 Tested**: Includes a test suite to ensure reliability.

## 🛠️ Tech Stack

-   **Backend**: Python 3.11+ with FastAPI
-   **Metadata Source**: DataHub (MCP Server, DataHub Skills, or Agent Context Kit)
-   **Integration**: GitHub API (Webhooks)
-   **Deployment**: Docker, Docker Compose, and Render
-   **Testing**: Pytest

## 🏗️ Project Structure

```bash
docguard-agent/
├── src/
│   ├── agents/           # Linter & Doc Validator logic
│   ├── api/              # FastAPI endpoints & models
│   ├── core/             # Config, exceptions, logging, security
│   └── services/         # DataHub & GitHub API clients
├── tests/                # Pytest suite
├── docs/                 # Architecture and API references
├── scripts/              # Setup and deployment helpers
├── LICENSE               # Apache 2.0
├── README.md             # You are here
├── requirements.txt      # Python dependencies
├── Dockerfile            # Containerization
├── docker-compose.yml    # Local development
└── render.yaml           # Deploy to Render
```

## 🚀 Quick Start

### Prerequisites
- Python 3.11+
- Docker (optional, for local DataHub)
- A GitHub account and a `GITHUB_TOKEN`

### Installation & Setup

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/emyasenc/docguard-agent.git
    cd docguard-agent
    ```

2.  **Create a virtual environment and install dependencies:**
    ```bash
    python3 -m venv venv
    source venv/bin/activate  # On Linux/macOS
    pip install -r requirements.txt
    ```

3.  **Set up environment variables** (copy `.env.example` to `.env` and fill in your keys):
    ```bash
    DATAHUB_ENDPOINT=http://localhost:8080
    DATAHUB_TOKEN=your_datahub_token
    GITHUB_TOKEN=your_github_personal_access_token
    GITHUB_WEBHOOK_SECRET=your_webhook_secret
    ENVIRONMENT=development
    ```

4.  **Spin up a local DataHub instance** (for testing):
    ```bash
    pip install acryl-datahub
    datahub docker quickstart
    ```
    *The UI will be available at `http://localhost:9002` (login: `datahub`/`datahub`).*

5.  **Run the application:**
    ```bash
    uvicorn src.main:app --reload
    ```
    *The FastAPI app will be available at `http://localhost:8000/docs`.*

## 🔧 Configuration

The application is configured via environment variables:

| Variable | Description |
| :--- | :--- |
| `DATAHUB_ENDPOINT` | Your DataHub instance URL (e.g., `http://localhost:8080`). |
| `DATAHUB_TOKEN` | Your DataHub Personal Access Token. |
| `GITHUB_TOKEN` | Your GitHub Personal Access Token (needs `repo` and `pull_request` scopes). |
| `GITHUB_WEBHOOK_SECRET` | Secret to verify GitHub webhook signatures. |
| `ENVIRONMENT` | Set to `production` for deployed instances. |

## 📈 Use with DataHub

DocGuard is built to be a **meaningful contributor** to DataHub's context graph. It doesn't just read metadata; it actively uses it to protect your data stack. In the future, it could even write back validation results to DataHub, creating a closed-loop quality system.

This project demonstrates a powerful pattern: **using DataHub as the central source of truth for automated quality gates in your CI/CD pipeline.**

## 🧪 Testing

Run the test suite to ensure everything is working:
```bash
pytest tests/ -v
```

## 📄 License

This project is licensed under the **Apache 2.0 License**. See the [LICENSE](LICENSE) file for details.

---
Built with ❤️ by Emma Yasenchak — ML Engineer & Data Scientist
