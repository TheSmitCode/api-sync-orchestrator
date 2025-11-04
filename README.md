# API Sync Orchestrator

[![Python](https://img.shields.io/badge/Python-3.8%2B-blue)](https://www.python.org/)
[![FastAPI](https://img.shields.io/badge/FastAPI-0.100%2B-yellow)](https://fastapi.tiangolo.com/)
[![Vercel](https://img.shields.io/badge/Deploy-Vercel-black?logo=vercel)](https://vercel.com/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green)](LICENSE)

A lightweight, JSON-configurable Python tool for orchestrating API data syncs—pull from multiple sources (e.g., Stripe, Shopify), transform with simple rules, and push to targets like Airtable or Postgres. Perfect for ETL without the bloat: CLI for devs, web API for non-techies. Inspired by real-world Upwork gigs for e-comm/CRM integrations.

## 🚀 Why Use This?
Tired of writing one-off scripts for API glue? This handles:
- **Multi-Source Syncs**: Fetch from REST APIs with auth (Bearer, API keys).
- **JSON Transformations**: User-defined rules (add fields, filter, map) via Pydantic-validated configs—no code changes.
- **Scheduling**: Cron-like jobs with APScheduler (e.g., every 5min).
- **Error-Resilient**: Retries, JSON logs, and audit trails for debugging.
- **Targets**: Airtable, Google Sheets, Postgres, or custom webhooks.

Built for indie hackers & freelancers: Quick to deploy on Vercel for live dashboards, or run locally as CLI.

## 🎯 Quick Example
Define a sync in `config.json`:
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
  "schedule": "*/5 * * * *",  // Every 5 minutes
  "retries": 3
}
```

Run: `python sync.py --config config.json`  
Output: Synced records in Airtable + `logs/sync_audit.json` with details.

For web mode: `uvicorn main:app --reload` → POST `/sync` with config payload.

## 🛠 Tech Stack
- **Core**: Python 3.8+, `requests` for API calls, `json` + Pydantic for configs/validation.
- **API Layer**: FastAPI for REST endpoints (e.g., `/sync`, `/logs`).
- **Scheduling**: APScheduler for cron jobs.
- **Targets**: Integrations via `airtable-python-wrapper`, `psycopg2` (Postgres), `gspread` (Sheets).
- **Deploy**: Vercel (serverless) or Docker for prod.

No bloat—under 500 LOC for MVP.

## 📋 Installation & Quick Start
1. Clone: `git clone https://github.com/TheSmitCode/api-sync-orchestrator.git && cd api-sync-orchestrator`
2. Setup: `pip install -r requirements.txt` (includes fastapi, uvicorn, pydantic, apscheduler, requests)
3. Config: Copy `config.example.json` → `config.json` & add your keys.
4. CLI: `python sync.py --config config.json --dry-run` (test without pushing).
5. Web: `uvicorn main:app --host 0.0.0.0 --port 8000`
6. Schedule: `python scheduler.py` (runs background jobs).
7. Deploy to Vercel: Push to GitHub → Connect repo in Vercel dashboard (auto-deploys API).

**Templates Included**: E-comm (Stripe → Shopify), CRM (HubSpot → Airtable). Fork & customize!

## 🤝 Contributing
- PRs welcome: Add new sources (e.g., GitHub API) or targets.
- Issues: Report bugs or request features (e.g., GraphQL support).
- Stars/Forks: Help spread the word—aiming for 100+ from r/Python & Upwork shares!

## 📄 License
MIT—free for commercial use. See [LICENSE](LICENSE).

---

*Built by [TheSmitCode] – Turning Upwork pains into open-source wins. Feedback? Open an issue! 🚀*
