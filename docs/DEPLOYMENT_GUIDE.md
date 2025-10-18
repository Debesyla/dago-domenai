# DAGO Deployment Guide

Complete guide for deploying DAGO Domain Analyzer to a production server.

## 📋 Prerequisites

### Server Requirements
- **OS**: Ubuntu 20.04+ or Debian 11+ (recommended)
- **RAM**: 2GB minimum, 4GB+ recommended
- **Disk**: 20GB+ (for database and logs)
- **Python**: 3.9+
- **PostgreSQL**: 12+

### Local Requirements
- Git repository with latest changes committed
- SSH access to your server
- Server hostname/IP address

---

## 🚀 Deployment Methods

### Method 1: Git Clone (Recommended for Production)

#### On Your Server

```bash
# 1. SSH into your server
ssh your-user@your-server.com

# 2. Update system packages
sudo apt update && sudo apt upgrade -y

# 3. Install required system packages
sudo apt install -y python3 python3-pip python3-venv postgresql postgresql-contrib git

# 4. Create application directory
sudo mkdir -p /opt/dago
sudo chown $USER:$USER /opt/dago
cd /opt/dago

# 5. Clone the repository
git clone https://github.com/Debesyla/dago-domenai.git
cd dago-domenai

# 6. Create Python virtual environment
python3 -m venv .venv
source .venv/bin/activate

# 7. Install Python dependencies
pip install --upgrade pip
pip install -r requirements.txt

# 8. Configure database (see Database Setup section below)
```

---

### Method 2: SCP/RSYNC (Alternative)

```bash
# From your local machine
cd /Users/dan/Documents/IT/dago/dago-cloud

# Option A: Using rsync (recommended - excludes unnecessary files)
rsync -avz \
  --exclude '.venv' \
  --exclude '__pycache__' \
  --exclude '*.pyc' \
  --exclude '.git' \
  --exclude 'logs/*' \
  --exclude 'exports/*' \
  --exclude '.pytest_cache' \
  dago-domenai/ your-user@your-server.com:/srv/dago-domenai/

# Option B: Using scp
scp -r dago-domenai/ your-user@your-server.com:/opt/dago/
```

---

## 🗄️ Database Setup

### On Your Server

```bash
# 1. Create PostgreSQL user and database
sudo -u postgres psql << EOF
CREATE USER domenai WITH PASSWORD 'YOUR_SECURE_PASSWORD_HERE';
CREATE DATABASE domenai OWNER domenai;
GRANT ALL PRIVILEGES ON DATABASE domenai TO domenai;
\q
EOF

# 2. Run database schema
cd /srv/dago-domenai
psql "postgresql://domenai:YOUR_SECURE_PASSWORD_HERE@localhost:5432/domenai" -f db/schema.sql

# 3. Verify database
psql "postgresql://domenai:YOUR_SECURE_PASSWORD_HERE@localhost:5432/domenai" -c "\dt"
```

---

## ⚙️ Configuration

### 1. Environment Variables (Recommended)

Create `.env` file in the project root:

```bash
cd /srv/dago-domenai
cat > .env << 'EOF'
# Database Configuration
DATABASE_URL=postgresql://domenai:YOUR_SECURE_PASSWORD_HERE@localhost:5432/domenai

# Application Settings
ENV=production
DEBUG=false

# Optional: Custom logging
LOG_LEVEL=INFO
EOF

# Secure the .env file
chmod 600 .env
```

### 2. Update config.yaml

```bash
nano config.yaml
```

Update these sections:
```yaml
env: production
debug: false

database:
  postgres_url: "postgresql://domenai:YOUR_SECURE_PASSWORD_HERE@localhost:5432/domenai"
  save_results: true

logging:
  level: INFO
  log_dir: /srv/dago-domenai/logs
```

---

## 🧪 Test the Installation

```bash
cd /srv/dago-domenai
source .venv/bin/activate

# Test 1: Check Python dependencies
python -c "import yaml, psycopg2, aiohttp; print('✅ Dependencies OK')"

# Test 2: Database connection
python -c "from src.utils.db import init_db; init_db('postgresql://domenai:PASSWORD@localhost:5432/domenai'); print('✅ Database OK')"

# Test 3: Run quick-whois on a single domain
python -m src.orchestrator --domain debesyla.lt --profiles quick-whois

# Test 4: Run unit tests
pytest tests/unit/ -v
```

---

## 🏃 Running Scans

### Interactive Scan

```bash
cd /srv/dago-domenai
source .venv/bin/activate

# Quick registration check
python -m src.orchestrator domains.txt --profiles quick-whois

# Standard scan
python -m src.orchestrator domains.txt --profiles standard
```

### Background Scan (Production)

```bash
# Start scan in background with nohup
nohup python -m src.orchestrator domains.txt --profiles quick-whois \
  > logs/scan_$(date +%Y%m%d_%H%M%S).log 2>&1 &

# Get the process ID
echo $!

# Monitor progress
tail -f logs/scan_*.log

# Stop the scan
pkill -f "python.*orchestrator"
```

---

## 🔄 Systemd Service (Recommended for Production)

Create a systemd service for scheduled scans:

```bash
sudo nano /etc/systemd/system/dago-scan.service
```

```ini
[Unit]
Description=DAGO Domain Analyzer Scan
After=network.target postgresql.service

[Service]
Type=simple
User=your-username
WorkingDirectory=/srv/dago-domenai
Environment="PATH=/srv/dago-domenai/.venv/bin"
ExecStart=/srv/dago-domenai/.venv/bin/python -m src.orchestrator /opt/dago/domains.txt --profiles quick-whois
Restart=on-failure
RestartSec=300

# Logging
StandardOutput=append:/srv/dago-domenai/logs/service.log
StandardError=append:/srv/dago-domenai/logs/service-error.log

[Install]
WantedBy=multi-user.target
```

Enable and manage the service:

```bash
# Reload systemd
sudo systemctl daemon-reload

# Enable service (start on boot)
sudo systemctl enable dago-scan

# Start service
sudo systemctl start dago-scan

# Check status
sudo systemctl status dago-scan

# View logs
journalctl -u dago-scan -f
```

---

## ⏰ Cron Jobs (Alternative to Systemd)

For scheduled periodic scans:

```bash
crontab -e
```

Add entries:

```bash
# Run quick-whois scan daily at 2 AM
0 2 * * * cd /srv/dago-domenai && source .venv/bin/activate && python -m src.orchestrator domains.txt --profiles quick-whois >> logs/cron_$(date +\%Y\%m\%d).log 2>&1

# Run full standard scan weekly (Sunday 3 AM)
0 3 * * 0 cd /srv/dago-domenai && source .venv/bin/activate && python -m src.orchestrator domains.txt --profiles standard >> logs/weekly_$(date +\%Y\%m\%d).log 2>&1

# Cleanup old exports (keep last 30 days)
0 4 * * * find /srv/dago-domenai/exports -name "*.json" -mtime +30 -delete
0 4 * * * find /srv/dago-domenai/logs -name "*.log" -mtime +30 -delete
```

---

## 📊 Monitoring & Maintenance

### Check Scan Progress

```bash
# Use the monitor script
cd /srv/dago-domenai
./monitor_scan.sh

# Or manually check database
psql "postgresql://domenai:PASSWORD@localhost:5432/domenai" -c "
SELECT 
    COUNT(*) as total_domains,
    COUNT(*) FILTER (WHERE is_registered = true) as registered,
    COUNT(*) FILTER (WHERE is_active = true) as active
FROM domains;
"
```

### View Recent Results

```bash
# Latest exports
ls -lht /srv/dago-domenai/exports/ | head -10

# Database queries
psql "postgresql://domenai:PASSWORD@localhost:5432/domenai" -c "
SELECT domain_name, is_registered, is_active, last_checked 
FROM domains 
ORDER BY last_checked DESC 
LIMIT 10;
"
```

### Log Rotation

```bash
sudo nano /etc/logrotate.d/dago
```

```
/srv/dago-domenai/logs/*.log {
    daily
    rotate 30
    compress
    delaycompress
    missingok
    notifempty
    create 0644 your-username your-username
}
```

---

## 🔒 Security Best Practices

### 1. Firewall Configuration

```bash
# Allow SSH
sudo ufw allow 22/tcp

# Allow PostgreSQL only from localhost (default)
# No external access needed for single-server setup

# Enable firewall
sudo ufw enable
```

### 2. Database Security

```bash
# Edit PostgreSQL config
sudo nano /etc/postgresql/*/main/pg_hba.conf
```

Ensure these lines for local connections:
```
local   all             domenai                                 md5
host    all             domenai         127.0.0.1/32            md5
```

```bash
# Restart PostgreSQL
sudo systemctl restart postgresql
```

### 3. File Permissions

```bash
cd /srv/dago-domenai

# Secure configuration files
chmod 600 .env config.yaml

# Secure database credentials
chmod 700 db/

# Make directories writable for logs and exports
chmod 755 logs exports
```

---

## 🔄 Updating the Application

### Pull Latest Changes

```bash
cd /srv/dago-domenai

# Backup database first
pg_dump "postgresql://domenai:PASSWORD@localhost:5432/domenai" > backup_$(date +%Y%m%d).sql

# Pull latest code
git pull origin main

# Update dependencies if needed
source .venv/bin/activate
pip install -r requirements.txt --upgrade

# Run database migrations if any
psql "postgresql://domenai:PASSWORD@localhost:5432/domenai" -f db/schema.sql

# Restart service
sudo systemctl restart dago-scan
```

---

## 🐛 Troubleshooting

### Issue: Database Connection Failed

```bash
# Check PostgreSQL is running
sudo systemctl status postgresql

# Test connection manually
psql "postgresql://domenai:PASSWORD@localhost:5432/domenai" -c "SELECT 1;"

# Check logs
sudo tail -f /var/log/postgresql/postgresql-*-main.log
```

### Issue: Module Not Found

```bash
# Ensure virtual environment is activated
source /srv/dago-domenai/.venv/bin/activate

# Reinstall dependencies
pip install -r requirements.txt --force-reinstall
```

### Issue: Permission Denied

```bash
# Fix ownership
sudo chown -R your-username:your-username /srv/dago-domenai

# Fix permissions
chmod -R 755 /srv/dago-domenai
chmod 600 /srv/dago-domenai/.env
```

---

## 📈 Performance Optimization

### 1. Database Tuning

```bash
sudo nano /etc/postgresql/*/main/postgresql.conf
```

Recommended settings for domain scanning:
```ini
shared_buffers = 256MB
effective_cache_size = 1GB
maintenance_work_mem = 128MB
work_mem = 16MB
max_connections = 100
```

Restart PostgreSQL:
```bash
sudo systemctl restart postgresql
```

### 2. Concurrent Scanning

For faster processing, modify `config.yaml`:
```yaml
network:
  concurrency: 50  # Adjust based on server resources
  request_timeout: 10
```

### 3. Database Indexes

Indexes are already created by `db/schema.sql`, but verify:
```sql
-- Check existing indexes
\di

-- Should see indexes on:
-- - domains(domain_name)
-- - domains(is_registered)
-- - domains(is_active)
-- - results(domain_id)
-- - results(checked_at)
```

---

## 📞 Support & Resources

- **Documentation**: `/srv/dago-domenai/docs/`
- **Logs**: `/srv/dago-domenai/logs/`
- **Config**: `/srv/dago-domenai/config.yaml`
- **Database Schema**: `/srv/dago-domenai/db/schema.sql`

---

## ✅ Deployment Checklist

- [ ] Server meets minimum requirements
- [ ] PostgreSQL installed and configured
- [ ] Python 3.9+ installed
- [ ] Code deployed to `/srv/dago-domenai`
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] Database created and schema loaded
- [ ] `.env` file configured with secure credentials
- [ ] `config.yaml` updated for production
- [ ] Test scan completed successfully
- [ ] Monitoring script working
- [ ] Systemd service or cron job configured
- [ ] Log rotation configured
- [ ] Firewall configured
- [ ] File permissions secured
- [ ] Backup strategy in place

---

**🎉 Your DAGO deployment is complete!**

For questions or issues, check the logs in `/srv/dago-domenai/logs/`
