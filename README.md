# 🛡️ DocGuard — Metadata-Aware Documentation Guardian Agent

DocGuard is an AI agent that validates code and documentation against DataHub metadata. It catches issues early, prevents broken pipelines, and ensures documentation stays up-to-date.

## 🚀 Features

- **Code Linter**: Validates SQL tables, columns, and functions against DataHub metadata
- **Doc Validator**: Checks documentation for missing sections, deprecated terms, and metadata mismatches
- **GitHub Integration**: Automatically comments on PRs with issues and suggestions
- **Real-time Validation**: Runs on every pull request
- **Production Ready**: Deployed on Render with monitoring

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Metadata**: DataHub
- **Deployment**: Render
- **Container**: Docker

## 📦 Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/emyasenc/docguard-agent.git
   cd docguard-agent