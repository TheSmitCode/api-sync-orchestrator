API Sync Orchestrator

A lightweight, JSON-configurable Python tool for orchestrating API data syncs — pull from multiple sources (e.g., Stripe, Shopify), transform with simple rules, and push to targets like Airtable or Postgres.

Perfect for ETL without the bloat: CLI for devs, web API for non-techies.
Inspired by real-world Upwork gigs for e-comm/CRM integrations.

🚀 Why Use This?

Tired of writing one-off scripts for API glue? This handles:

✅ Multi-Source Syncs – Fetch from REST APIs with auth (Bearer, API keys)
✅ JSON Transformations – User-defined rules (add fields, filter, map) via validated configs—no code changes
✅ Scheduling – Cron-like jobs with APScheduler (e.g., every 5min)
✅ Error-Resilient – Retries, JSON logs, and audit trails for debugging
✅ Targets – Airtable, Google Sheets, Postgres, or custom webhooks

Built for indie hackers & freelancers: quick to deploy on Vercel for live dashboards or run locally as CLI.

🎯 Quick Example

sync_config.json

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

🛠 Tech Stack

Core: Python 3.11+

Requests: For API calls

Pydantic v2: Schema validation

FastAPI: REST layer

APScheduler: Cron scheduling

Deploy: Vercel, Docker, or bare-metal

📋 Installation & Setup
🪄 Option 1 — Easy Setup (Recommended)

Run the setup script (auto-installs everything, including Rust if missing):

Windows
.\setup.ps1

macOS / Linux
bash setup.sh


What it does:

Checks Python version (recommends 3.11 or 3.12)

Installs Rust toolchain (required by Pydantic v2)

Creates virtual environment .venv

Installs requirements.txt

Runs a dry test

🧩 Option 2 — Manual Setup
git clone https://github.com/TheSmitCode/api-sync-orchestrator.git
cd api-sync-orchestrator

# Install Rust (only once)
winget install Rustlang.Rustup  # Windows
# or
curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh  # macOS/Linux

# Setup Python
py -3.12 -m venv .venv
.\.venv\Scripts\activate  # Windows
pip install --upgrade pip
pip install -r requirements.txt


⚠️ If using Windows, ensure Visual Studio Build Tools 2022 is installed (includes cl.exe compiler).

🧪 Test & Run
python sync.py --dry-run     # Simulate sync
python sync.py               # Full sync
python scheduler.py          # Run scheduled jobs
python main.py               # Start API server


Visit: http://127.0.0.1:8000

🧱 Templates Included

Stripe → Airtable

Shopify → Google Sheets

HubSpot → CRM

🤝 Contributing

Add new sources: e.g., GitHub, Salesforce

Raise issues: Feature requests or bug reports

Star the repo: Help reach 100+ on r/Python & Upwork!

📄 License

MIT — free for commercial and personal use.

Built by TheSmitCode — turning Upwork pains into open-source wins 🚀