# DAGO Domain Analyzer

**Automated domain analysis tool** for bulk website health checks, SEO audits, and technical monitoring.

## What It Does

Analyzes domains through **21 configurable profiles** covering:
- 🌐 **DNS & Network**: A records, nameservers, IP geolocation
- 🔒 **Security**: SSL certificates, HTTPS redirects, certificate expiry
- 📄 **SEO & Content**: Robots.txt, sitemaps, meta tags, structured data
- 🔍 **Technical**: HTTP status, redirects, WHOIS, domain registration
- 🤖 **Intelligence**: Content analysis, page speed, accessibility

## Quick Start

```bash
# 1. Setup
git clone https://github.com/Debesyla/dago-domenai.git
cd dago-domenai
python3 -m venv .venv && source .venv/bin/activate
pip install -r requirements.txt

# 2. Configure database (PostgreSQL)
./db/setup.sh

# 3. Run analysis
python -m src.orchestrator domains.txt --profiles quick-check
```

## Features

✅ **Profile-based execution** - Run quick-check, standard, technical-audit, or custom profiles  
✅ **Async processing** - Fast parallel checks with configurable concurrency  
✅ **PostgreSQL storage** - Structured results with JSON fields and indexed views  
✅ **Export formats** - JSON and CSV exports with summary statistics  
✅ **Smart dependencies** - Automatic profile dependency resolution  

## Usage Examples

```bash
# Quick filtering (registration + activity checks)
python -m src.orchestrator domains.txt --profiles quick-check

# Standard analysis (DNS, SSL, redirects, robots)
python -m src.orchestrator domains.txt --profiles standard

# Custom profile combination
python -m src.orchestrator domains.txt --profiles dns,ssl,seo-basic

# Single domain check
python -m src.orchestrator --domain example.com --profiles complete
```

## Documentation

- **[Setup Guide](docs/SETUP.MD)** - Installation and configuration
- **[Launch Plan](docs/LAUNCH_PLAN.md)** - Development roadmap
- **[Changelog](CHANGELOG.md)** - Version history
- **[Testing Guide](tests/README.md)** - Running tests

## Requirements

- Python 3.9+
- PostgreSQL 12+
- Dependencies: aiohttp, psycopg2, dnspython

## Version

**v1.0.0** - Production Ready (October 2025)

## License

MIT