# 🧠 domenai — Domain Intelligence Backend

## Overview
This project is a **backend and task queue** for analyzing websites/domains automatically.  
It is designed to store, queue, and run background checks (tasks) on a list of domains (like `example.com`), saving the results for each task in a structured PostgreSQL database.

Later, a **frontend dashboard** or **API layer** will visualize or expose this data.

---

## 💡 Purpose

To build a self-hosted intelligence engine that can:
1. Keep a database of domains.
2. Run multiple background checks (called *tasks*).
3. Save the results (status, CMS, company, sitemap, etc.).
4. Eventually expose these results via a dashboard or API.

---

## 🏗️ Current Stack

| Component | Description |
|------------|-------------|
| **VPS** | Hostinger VPS (Ubuntu) |
| **Database** | PostgreSQL (`domenai` database, `domenai` user) |
| **Python backend** | Worker scripts performing the checks |
| **Virtual environment** | Python `venv` in `/srv/domenai/venv` |
| **Languages known by developer** | PHP, JavaScript, MySQL (new to Python/Postgres) |

---

## 🧱 Database Schema

### 1. `domains`
Stores unique domain entries.

| Column | Type | Description |
|---------|------|-------------|
| `id` | SERIAL | Primary key |
| `domain_name` | VARCHAR(255) | e.g. `"example.com"` |
| `created_at` | TIMESTAMP | Creation timestamp |
| `updated_at` | TIMESTAMP | Updated timestamp |

### 2. `tasks`
Static list of what types of checks can be done.

| Column | Type | Description |
|---------|------|-------------|
| `id` | SERIAL | Primary key |
| `name` | VARCHAR(100) | Machine-readable identifier (e.g. `"check_status"`) |
| `description` | TEXT | Human-readable info |

Example `tasks`:

| id | name | description |
|----|------|--------------|
| 1 | check_status | Check if domain is active or returns error |
| 2 | check_cms | Detect which CMS the site uses |
| 3 | check_sitemap | Check for sitemap.xml |
| 4 | check_company | Match domain to company data |
| 5 | analyze_type | AI-based guess what the domain is for |

### 3. `results`
Stores the actual output of tasks run on domains.

| Column | Type | Description |
|---------|------|-------------|
| `id` | SERIAL | Primary key |
| `domain_id` | INT | FK → `domains.id` |
| `task_id` | INT | FK → `tasks.id` |
| `status` | VARCHAR(50) | e.g. `"success"`, `"error"`, `"timeout"` |
| `data` | JSONB | Arbitrary task result data |
| `checked_at` | TIMESTAMP | When the check ran |

---

## 🧩 Current Progress (as of setup)

✅ PostgreSQL database initialized  
✅ Schema and base `tasks` inserted  
✅ Python environment (`venv`) created  
✅ Connection tested with `db_test_insert.py` (inserted `test.lt`)  

---

## 🔄 Next Development Phases

### **Phase 1 – Task Runner System**

Goal: create one Python script per task (or a modular runner) that:
- Fetches pending domains from DB.
- Runs the check (e.g., fetch HTTP, detect CMS).
- Inserts a `results` row for that domain + task.

#### 1. Example task scripts
- `tasks/check_status.py` → use `requests` to check domain, record HTTP code, redirect, response time.
- `tasks/check_cms.py` → fetch homepage HTML, look for CMS signatures (WordPress, Shopify, etc.).
- `tasks/check_sitemap.py` → check if `https://domain/sitemap.xml` exists.
- `tasks/check_company.py` → placeholder, maybe call API later.
- `tasks/analyze_type.py` → later use OpenAI or local LLM for classification.

#### 2. Queue management
Simple at first: a script like `run_all.py` loops through all domains and runs all tasks.
Later: integrate with `cron` or Celery/RQ for async workers.

---

### **Phase 2 – API Layer (Optional Early MVP)**

Implement a lightweight **FastAPI** or **Flask** app:
- Endpoint `/domains` → list domains
- Endpoint `/results` → list latest results
- Optional: `/trigger?domain=example.com` → enqueue checks

---

### **Phase 3 – Frontend Dashboard**

A simple PHP or JS-based frontend to:
- Display domains and their latest results.
- Allow adding new domains for checking.
- Optional filtering and task progress views.

Possible stacks:
- Static HTML + REST API
- PHP frontend reading directly from DB
- Later, maybe Next.js or 11ty integration

---

### **Phase 4 – Automation & Scaling**

- Run checks automatically every X hours via cron (`crontab -e`)
- Optimize task parallelization
- Introduce caching / proxy to avoid over-requesting
- Optional Dockerization for portability

---

## ⚙️ Folder Structure (suggested)

/srv/domenai/
├── venv/ # Python virtual environment
├── db_test_insert.py # test script that inserts sample data
├── tasks/
│ ├── check_status.py # first worker script
│ ├── check_cms.py
│ ├── ...
├── run_all.py # main orchestrator / cron entry
├── config.py # connection settings, shared constants
├── PROJECT_PLAN.md # this file
└── README.md # shorter version for public repo


---

## 🔐 Credentials (current dev setup)

| Variable | Value |
|-----------|--------|
| DB name | `domenai` |
| DB user | `domenai` |
| DB password | `larakniaukialiauliauliau` |
| Host | `localhost` |

*(For development only — change before production deployment!)*

---

## 🧭 How the System Flows

[1] Add domain to DB
↓
[2] For each task in "tasks"
↓
[3] Python worker executes the check
↓
[4] Insert result row in "results"
↓
[5] Dashboard or API displays data


---

## 🚀 Next Immediate Steps (for VS Code)

1. **Open the folder via SSH in VS Code**
code --remote ssh root@srv1059521:/srv/domenai

*(Or use “Remote - SSH” extension → Connect to Host → open `/srv/domenai`)*

2. Inside VS Code:
- Create `tasks/check_status.py`
- Create `config.py` for DB credentials
- Test running it from integrated terminal:
  ```
  source venv/bin/activate
  python tasks/check_status.py
  ```

3. After first script works → expand to `run_all.py` orchestration.

---

## 🧰 Optional Tools for Copilot / LLM agents

Copilot or another AI assistant can:
- Suggest completion for each `tasks/*.py` file.
- Generate SQL queries.
- Help debug `psycopg2` connections.
- Write simple REST endpoints.

Prompt examples to feed into Copilot:
> “Generate a Python script that connects to PostgreSQL using config.py and checks if a domain returns HTTP 200.”

> “List the last 10 failed tasks from the results table.”

---

## 🏁 Summary

- You now have a working foundation: PostgreSQL + Python + schema + base data.  
- Next: build real check scripts in `/srv/domenai/tasks/`.  
- Then: orchestrate them with a scheduler (manual, cron, or later Celery).  
- Finally: add a small dashboard (PHP or JS) for visualization.

This document ensures any AI assistant (or developer) understands where we are and what comes next.

