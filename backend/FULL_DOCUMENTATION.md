# Complete Backend Documentation

## 📋 Table of Contents
1. [Overview](#overview)
2. [Installation](#installation)
3. [Configuration](#configuration)
4. [Running the Backend](#running-the-backend)
5. [API Reference](#api-reference)
6. [Architecture](#architecture)
7. [SSH Integration](#ssh-integration)
8. [Frontend Integration](#frontend-integration)
9. [Database](#database)
10. [Troubleshooting](#troubleshooting)

## 🎯 Overview

A Python Flask backend that provides REST API for managing and monitoring remote Linux systems via SSH. It handles:

- **System Monitoring** - CPU, memory, disk, uptime tracking
- **Disk Space Management** - View and track disk usage across systems
- **System Cleanup** - Automated cleanup of cache, temporary files, and logs
- **SSH Command Execution** - Execute bash commands on remote systems
- **Async Operations** - Non-blocking cleanup tasks using threading
- **Database Storage** - Persistent storage of system data and operation history

## 📦 Installation

### Prerequisites
- Python 3.8 or higher
- pip package manager
- Git (optional)

### Step 1: Create Virtual Environment

**Windows:**
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
```

**macOS/Linux:**
```bash
cd backend
python3 -m venv venv
source venv/bin/activate
```

### Step 2: Install Dependencies

```bash
pip install -r requirements.txt
```

**Installed packages:**
- Flask 3.0.0 - Web framework
- Flask-CORS 4.0.0 - Cross-origin request handling
- Flask-SQLAlchemy 3.1.1 - ORM for database
- python-dotenv 1.0.0 - Environment variables
- paramiko 3.4.0 - SSH client library

### Step 3: Configure Environment

Copy template:
```bash
copy .env.example .env  # Windows
cp .env.example .env    # macOS/Linux
```

Edit `.env`:
```env
FLASK_ENV=development
SECRET_KEY=your-secret-key-change-this
DATABASE_URL=sqlite:///system_manager.db
SSH_PORT=22
SSH_TIMEOUT=30
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## ⚙️ Configuration

### FLASK_ENV
- `development` - Debug mode enabled, auto-reload
- `production` - Optimized, no debug mode

### SECRET_KEY
Used for session management and CSRF protection. Change in production!

```bash
# Generate strong key (Python)
python -c "import secrets; print(secrets.token_hex(32))"
```

### DATABASE_URL
**SQLite (default):**
```env
DATABASE_URL=sqlite:///system_manager.db
```

**PostgreSQL:**
```env
DATABASE_URL=postgresql://user:password@localhost:5432/system_manager
pip install psycopg2-binary
```

### SSH Configuration
- `SSH_PORT` - Default SSH port (22)
- `SSH_TIMEOUT` - Connection timeout in seconds (30)

### CORS
Comma-separated list of allowed origins:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000,https://example.com
```

## 🚀 Running the Backend

### Option 1: Direct Python
```bash
cd backend
python app.py
```

### Option 2: Startup Script

**Windows:**
```powershell
cd backend
.\run.bat
```

**macOS/Linux:**
```bash
cd backend
bash run.sh
```

### Option 3: Docker

```bash
cd backend
docker-compose up
```

### Option 4: Gunicorn (Production)

```bash
pip install gunicorn
gunicorn -w 4 --bind 0.0.0.0:5000 app:create_app('production')
```

**Output:**
```
Running on http://0.0.0.0:5000
Press CTRL+C to quit
```

## 📡 API Reference

### Health Check

**Endpoint:** `GET /health`

**Response:**
```json
{
  "status": "healthy",
  "service": "System Manager Backend"
}
```

### System Management

#### Get All Systems
```http
GET /api/systems
```

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "pcName": "Lab-PC-001",
      "ipAddress": "192.168.1.100",
      "sshPort": 22,
      "status": "online",
      "lastSeen": "2026-01-26T10:30:00",
      "createdAt": "2026-01-20T15:45:30"
    }
  ]
}
```

#### Add New System
```http
POST /api/systems
Content-Type: application/json

{
  "pcName": "Lab-PC-001",
  "ipAddress": "192.168.1.100",
  "username": "admin",
  "password": "password123",
  "sshPort": 22
}
```

**Authentication Options:**

Method 1 - Password:
```json
{
  "pcName": "Server-01",
  "ipAddress": "192.168.1.100",
  "username": "admin",
  "password": "password123"
}
```

Method 2 - Private Key:
```json
{
  "pcName": "Server-01",
  "ipAddress": "192.168.1.100",
  "username": "admin",
  "privateKeyPath": "/path/to/id_rsa"
}
```

**Response (201):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "pcName": "Lab-PC-001",
    "ipAddress": "192.168.1.100",
    "status": "offline"
  }
}
```

#### Get System Details
```http
GET /api/systems/{id}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "pcName": "Lab-PC-001",
    "ipAddress": "192.168.1.100",
    "status": "online"
  }
}
```

#### Get System Status (Real-time)
```http
GET /api/systems/{id}/status
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "systemId": 1,
    "status": "online",
    "uptime": "5 days, 3:45",
    "cpuUsage": 45.2,
    "memoryInfo": {
      "total": "16Gi",
      "used": "8.2Gi",
      "free": "7.8Gi",
      "available": "8.0Gi"
    },
    "diskInfo": [
      {
        "filesystem": "/dev/sda1",
        "total": "500GB",
        "used": "250GB",
        "available": "250GB",
        "usage_percent": 50,
        "mount_point": "/"
      }
    ]
  }
}
```

#### Get Disk Space Info
```http
GET /api/systems/{id}/disk-space
```

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "filesystem": "/dev/sda1",
      "total": "500GB",
      "used": "250GB",
      "available": "250GB",
      "usage_percent": 50,
      "mount_point": "/"
    }
  ]
}
```

#### Test SSH Connection
```http
POST /api/systems/test-connection
Content-Type: application/json

{
  "ipAddress": "192.168.1.100",
  "username": "admin",
  "password": "password123",
  "sshPort": 22
}
```

**Response (200):**
```json
{
  "success": true,
  "message": "Connection successful",
  "data": {
    "uptime": "up 5 days, 3:45, 2 users, load average: 0.50, 0.45, 0.40"
  }
}
```

#### Delete System
```http
DELETE /api/systems/{id}
```

**Response (200):**
```json
{
  "success": true,
  "message": "System deleted"
}
```

### Cleanup Operations

#### Start Cleanup
```http
POST /api/cleanup
Content-Type: application/json

{
  "pcIds": [1, 2, 3],
  "cleanupType": "all"
}
```

**Cleanup Types:**
- `cache` - Clear system cache only
- `temp` - Remove temporary files only
- `logs` - Clean old logs only
- `all` - All of the above

**Response (202):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "systemId": 1,
      "cleanupType": "all",
      "status": "running",
      "spaceFreed": 0,
      "startedAt": "2026-01-26T10:35:00",
      "completedAt": null
    }
  ]
}
```

#### Get Cleanup Status
```http
GET /api/cleanup/{id}
```

**Response (200):**
```json
{
  "success": true,
  "data": {
    "id": 1,
    "systemId": 1,
    "cleanupType": "all",
    "status": "success",
    "spaceFreed": 5368709120,
    "errorMessage": null,
    "startedAt": "2026-01-26T10:35:00",
    "completedAt": "2026-01-26T10:36:30"
  }
}
```

#### Get Cleanup History
```http
GET /api/cleanup/system/{id}?limit=50
```

**Response (200):**
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "systemId": 1,
      "cleanupType": "all",
      "status": "success",
      "spaceFreed": 5368709120,
      "startedAt": "2026-01-26T10:35:00",
      "completedAt": "2026-01-26T10:36:30"
    }
  ]
}
```

## 🏗️ Architecture

### Directory Structure

```
backend/
├── app.py                 # Application factory
├── config.py             # Configuration management
├── models.py             # Database models
├── ssh_executor.py       # SSH execution
├── system_utils.py       # Utilities
└── routes/
    ├── system.py         # System endpoints
    └── cleanup.py        # Cleanup endpoints
```

### Components

**app.py - Application Factory**
- Creates Flask app instance
- Initializes extensions (db, CORS)
- Registers routes
- Sets up error handlers

**config.py - Configuration**
- Environment-based settings
- Development/Production/Testing configs
- Database and SSH configuration

**models.py - Data Models**

```
SystemPC           - System configuration
├── pc_name        - Computer name
├── ip_address     - IP address
├── username       - SSH username
├── password       - SSH password (encrypted)
├── status         - online/offline
└── last_seen      - Last connection time

SystemStatus       - Real-time metrics
├── system_id      - Reference to SystemPC
├── cpu_usage      - CPU percentage
├── memory_usage   - Memory usage
└── recorded_at    - Timestamp

DiskSpace          - Disk information
├── system_id      - Reference to SystemPC
├── mount_point    - Filesystem mount
├── total_space    - Total bytes
├── used_space     - Used bytes
└── usage_percent  - Percentage used

CleanupOperation   - Cleanup logs
├── system_id      - Reference to SystemPC
├── cleanup_type   - Type of cleanup
├── status         - pending/running/success/failed
├── space_freed    - Bytes freed
└── completed_at   - Completion time
```

**ssh_executor.py - SSH Handling**

```python
SSHExecutor
├── connect()           - Establish SSH connection
├── execute_command()   - Run command, return output
└── disconnect()        - Close connection

CommandBuilder
├── get_system_info()
├── get_disk_space()
├── get_cpu_usage()
├── get_memory_usage()
├── clean_cache()
├── clean_temp_files()
└── clean_logs()
```

**system_utils.py - Parsing**

```python
SystemInfoParser
├── parse_disk_space()      - Parse 'df' output
├── parse_memory_usage()    - Parse 'free' output
├── parse_uptime()          - Parse uptime command
├── parse_cpu_usage()       - Parse 'top' output
└── convert_bytes_to_human()  - Format bytes
```

### Request Flow

```
Client Request
    ↓
Flask Route Handler
    ↓
SSH Executor (if needed)
    ↓
Remote System (bash command)
    ↓
Parse Output
    ↓
Database Store
    ↓
JSON Response
```

## 🔐 SSH Integration

### Connection Process

1. **Validate Credentials**
   - Check IP, port, username
   - Verify password or key path

2. **Establish Connection**
   - Use Paramiko SSH client
   - Set timeout (default 30s)
   - Auto-add host key

3. **Execute Command**
   - Send bash command
   - Capture stdout, stderr
   - Get return code

4. **Parse Output**
   - Extract relevant data
   - Convert formats
   - Store in database

### Supported Commands

```bash
# System Info
uname -a
cat /proc/cpuinfo

# Disk Space
df -h

# Memory
free -h

# Uptime
uptime

# CPU Load
top -bn1

# Cleanup - Cache
sync && echo 3 | sudo tee /proc/sys/vm/drop_caches

# Cleanup - Temp files
sudo rm -rf /tmp/* /var/tmp/*

# Cleanup - Logs
sudo find /var/log -type f -name '*.log' -mtime +30 -delete
```

### Error Handling

- Connection timeout → "Connection failed"
- Authentication error → "Authentication failed"
- Command execution error → stderr captured
- SSH exception → Detailed error message

## 🔗 Frontend Integration

### Update API URLs

**frontend/src/utils/api.ts**

```typescript
const getBackendUrl = () => 'http://localhost:5000/api';

export async function callSystemStatusFunction() {
  const response = await fetch(`${getBackendUrl()}/systems`);
  return await response.json();
}

export async function callCleanupFunction(pcIds, cleanupType) {
  const response = await fetch(`${getBackendUrl()}/cleanup`, {
    method: 'POST',
    body: JSON.stringify({ pcIds, cleanupType })
  });
  return await response.json();
}
```

### Running Full Stack

Terminal 1 - Backend:
```bash
cd backend
python app.py
# Running on http://0.0.0.0:5000
```

Terminal 2 - Frontend:
```bash
cd frontend
npm run dev
# Local: http://localhost:5173
```

## 💾 Database

### SQLite (Development)

Default database: `backend/system_manager.db`

```sql
-- Automatically created on first run
-- Contains:
-- - system_pcs
-- - system_status
-- - disk_space
-- - cleanup_operations
```

### PostgreSQL (Production)

Install driver:
```bash
pip install psycopg2-binary
```

Configure in `.env`:
```env
DATABASE_URL=postgresql://user:password@localhost:5432/system_manager
```

### Database Backup

```bash
# SQLite backup
cp system_manager.db system_manager.db.backup

# PostgreSQL dump
pg_dump system_manager > backup.sql

# PostgreSQL restore
psql system_manager < backup.sql
```

## 🆘 Troubleshooting

### Backend Won't Start

**Error: "ModuleNotFoundError: No module named 'flask'"**

Solution:
```bash
pip install -r requirements.txt
```

**Error: "Address already in use"**

Solution - Change port in `app.py`:
```python
if __name__ == '__main__':
    app = create_app()
    app.run(debug=True, host='0.0.0.0', port=5001)  # Changed to 5001
```

### SSH Connection Issues

**"Connection failed" error**

Check:
- IP address is correct
- SSH port (default 22) is open
- Firewall allows SSH
- SSH service is running on target

Test:
```bash
ping 192.168.1.100
ssh -p 22 admin@192.168.1.100
```

**"Authentication failed"**

Check:
- Username is correct
- Password is correct
- Key file path is correct
- User permissions on key file

### Database Issues

**"database is locked" (SQLite)**

Caused by concurrent writes. Solution:
- Use PostgreSQL for production
- Or restart backend

**"connection refused"**

Check:
- PostgreSQL is running
- DATABASE_URL is correct
- User has permissions

### CORS Errors

**"No 'Access-Control-Allow-Origin' header"**

Solution - Update `.env`:
```env
CORS_ORIGINS=http://localhost:5173
```

Then restart backend.

### Performance Issues

**Slow queries:**
- Add database indexes
- Use PostgreSQL instead of SQLite
- Optimize SSH commands

**High memory usage:**
- Use Gunicorn with limited workers
- Check for connection leaks
- Monitor system resources

## 📋 Checklist

- [ ] Python 3.8+ installed
- [ ] Virtual environment created
- [ ] Dependencies installed
- [ ] .env file created and configured
- [ ] SSH access to target systems tested
- [ ] Backend starts without errors
- [ ] Frontend API URLs updated
- [ ] Health check passing
- [ ] Systems can be added
- [ ] Cleanup operations work

## 🔒 Security Checklist

- [ ] Change SECRET_KEY in production
- [ ] Use HTTPS for production
- [ ] Restrict CORS_ORIGINS
- [ ] Use SSH keys instead of passwords
- [ ] Encrypt credentials in database
- [ ] Regular security updates
- [ ] Use strong passwords
- [ ] Enable firewall rules
- [ ] Monitor SSH logs
- [ ] Backup database regularly

## 📞 Support

For issues:
1. Check logs in terminal
2. Verify network connectivity
3. Test SSH connection manually
4. Check .env configuration
5. Review API response format
6. Use test_api.py script

## 📚 Additional Resources

- Flask Documentation: https://flask.palletsprojects.com/
- Paramiko Documentation: https://www.paramiko.org/
- SQLAlchemy Documentation: https://docs.sqlalchemy.org/
- PostgreSQL Documentation: https://www.postgresql.org/docs/
