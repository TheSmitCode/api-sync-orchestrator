# API Sync Orchestrator

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.104%2B-yellow)](https://fastapi.tiangolo.com/)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-black?logo=vercel)](https://vercel.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A lightweight, JSON-configurable Python tool for orchestrating API data syncs—pull from multiple sources (e.g., Stripe, Shopify), transform with simple rules, and push to targets like Airtable or Postgres. Perfect for ETL without the bloat: CLI for devs, web API for non-techies. Inspired by real-world Upwork gigs for e-comm/CRM integrations.

## 🚀 Why Use This?
Tired of writing one-off scripts for API glue? This handles:
- **Multi-Source Syncs**: Fetch from REST APIs with auth (Bearer, API keys).
- **JSON Transformations**: User-defined rules (add fields, filter, map) via validated configs—no code changes.
- **Scheduling**: Cron-like jobs with APScheduler (e.g., every 5min).
- **Error-Resilient**: Retries, JSON logs, and audit trails for debugging.
- **Targets**: Airtable, Google Sheets, Postgres, or custom webhooks.

Built for indie hackers & freelancers: Quick to deploy on Vercel for live dashboards, or run locally as CLI.

## 🎯 Quick Example
Define a sync in `sync_config.json`:
```json
{
  "sources": [
    {
      "api": "stripe",
      "endpoint": "/v1/invoices",
      "auth": {"type": "bearer", "token": "sk_test_..."},
      "params": {"limit": 10}
    }
  ],
  "transform": {
    "add_field": {"timestamp": "{{ now() }}"},
    "filter": {"status": "paid"}
  },
  "target": {
    "type": "airtable",
    "base_id": "appXXXX",
    "table": "Invoices",
    "api_key": "keyXXXX"
  },
  "schedule": "*/5 * * * *",
  "retries": 3
}
Run: python sync.py --dry-run (test), python sync.py (full). Output: Audit in logs/audit_*.json.
🛠 Tech Stack

Core: Python 3.8+, requests for API calls, json for configs.
API Layer: FastAPI for REST endpoints (e.g., /sync, /logs).
Scheduling: APScheduler for cron jobs.
Targets: Manual for MVP; add pyairtable, gspread, psycopg2 for real (optional in requirements.txt).
Deploy: Vercel (serverless) or Docker for prod.

📋 Installation & Quick Start
Easy One-Command Setup (Rust first for Pydantic v2 build, then pips):

Windows: .\setup.ps1 (PowerShell).
Mac/Linux: bash setup.sh.

It creates venv, installs deps (pips after Rust), copies .env.example to .env, and tests with dry-run.
Manual (if preferred):

Clone:textgit clone https://github.com/TheSmitCode/api-sync-orchestrator.git && cd api-sync-orchestrator
Rust (required for Pydantic v2 build):
Windows: winget install Rustlang.Rustup.
Mac/Linux: curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh.

Venv & Deps:textpython -m venv .venv
.venv\Scripts\activate  # Windows; source .venv/bin/activate for Mac/Linux
pip install --upgrade pip
pip install -r requirements.txt
.env Setup:
Copy .env.example to .env.
Edit .env with real keys (Stripe, Airtable).

Test:textpython sync.py --dry-run  # Test without "pushing"
python sync.py  # Full sync (dummy mode)
Scheduler:textpython scheduler.py  # Runs on cron from JSON (every 5 mins)
API:textpython main.py  # Starts server at http://127.0.0.1:8000
curl http://127.0.0.1:8000/health  # {"status": "healthy"}
curl.exe -X POST "http://127.0.0.1:8000/sync" -H "Content-Type: application/json" --data-binary "@test-sync.json"  # Complete audit

Templates Included: E-comm (Stripe → Shopify), CRM (HubSpot → Airtable). Fork & customize!
🤝 Contributing

PRs welcome: Add new sources (e.g., GitHub API) or targets.
Issues: Report bugs or request features (e.g., GraphQL support).
Stars/Forks: Help spread the word—aiming for 100+ from r/Python & Upwork shares!
📄 License
MIT—free for commercial use. See LICENSE.

Built by TheSmitCode – Turning Upwork pains into open-source wins. Feedback? Open an issue! 🚀