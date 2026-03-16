# Backend Quick Reference Guide

## 🚀 START HERE

### Run Backend (Choose One)

**Windows:**
```powershell
cd backend
run.bat
```

**Linux/macOS:**
```bash
cd backend
bash run.sh
```

**Docker:**
```bash
cd backend
docker-compose up
```

**Access:** http://localhost:5000

---

## 📡 API Quick Reference

### System Management

```bash
# List all systems
curl http://localhost:5000/api/systems

# Add a system
curl -X POST http://localhost:5000/api/systems \
  -H "Content-Type: application/json" \
  -d '{
    "pcName": "MyPC",
    "ipAddress": "192.168.1.100",
    "username": "admin",
    "password": "password"
  }'

# Get system details
curl http://localhost:5000/api/systems/1

# Get real-time status
curl http://localhost:5000/api/systems/1/status

# Get disk space
curl http://localhost:5000/api/systems/1/disk-space

# Delete system
curl -X DELETE http://localhost:5000/api/systems/1
```

### Cleanup Operations

```bash
# Start cleanup
curl -X POST http://localhost:5000/api/cleanup \
  -H "Content-Type: application/json" \
  -d '{
    "pcIds": [1],
    "cleanupType": "all"
  }'

# Check cleanup status
curl http://localhost:5000/api/cleanup/1

# List all cleanups
curl http://localhost:5000/api/cleanup

# Get system cleanup history
curl http://localhost:5000/api/cleanup/system/1
```

---

## 📂 File Structure

```
backend/
├── app.py                 ← Main application
├── config.py              ← Settings
├── models.py              ← Database models
├── ssh_executor.py        ← SSH client
├── system_utils.py        ← Utilities
├── routes/
│   ├── system.py          ← System endpoints
│   └── cleanup.py         ← Cleanup endpoints
├── requirements.txt       ← Dependencies
├── .env.example           ← Config template
├── run.bat/run.sh         ← Startup scripts
├── Dockerfile             ← Docker config
└── test_api.py            ← Tests
```

---

## ⚙️ Configuration (.env)

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///system_manager.db
SSH_PORT=22
SSH_TIMEOUT=30
CORS_ORIGINS=http://localhost:5173
```

---

## 🧪 Testing

```bash
# Test all endpoints
cd backend
python test_api.py

# Test server health
curl http://localhost:5000/health
```

---

## 📋 API Endpoints

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/systems` | List systems |
| POST | `/api/systems` | Add system |
| GET | `/api/systems/{id}` | Get details |
| DELETE | `/api/systems/{id}` | Delete |
| GET | `/api/systems/{id}/status` | Real-time status |
| GET | `/api/systems/{id}/disk-space` | Disk info |
| GET | `/api/systems/{id}/history` | History |
| POST | `/api/systems/test-connection` | Test SSH |
| POST | `/api/cleanup` | Start cleanup |
| GET | `/api/cleanup/{id}` | Get status |
| GET | `/api/cleanup` | List all |
| GET | `/api/cleanup/system/{id}` | System history |
| GET | `/health` | Health check |

---

## 🔐 SSH Authentication

**Password:**
```json
{
  "ipAddress": "192.168.1.100",
  "username": "admin",
  "password": "password123"
}
```

**Private Key:**
```json
{
  "ipAddress": "192.168.1.100",
  "username": "admin",
  "privateKeyPath": "/path/to/id_rsa"
}
```

---

## 📊 Response Format

All endpoints return:
```json
{
  "success": true,
  "data": { /* endpoint-specific data */ },
  "error": null
}
```

---

## 🆘 Troubleshooting

| Problem | Solution |
|---------|----------|
| Backend won't start | `pip install -r requirements.txt` |
| Port 5000 in use | Change port in app.py |
| SSH connection fails | Verify IP, port, credentials |
| CORS error | Update CORS_ORIGINS in .env |
| Database error | Delete .db file, restart |

---

## 🔗 Frontend Integration

Update `frontend/src/utils/api.ts`:
```typescript
const getBackendUrl = () => 'http://localhost:5000/api';
```

---

## 📚 Documentation

| File | Content |
|------|---------|
| START_HERE.md | Quick start |
| SETUP.md | Installation |
| API.md | API reference |
| INTEGRATION.md | Frontend setup |
| FULL_DOCUMENTATION.md | Complete guide |
| FEATURES.md | Feature list |

---

## 💻 Key Commands

```bash
# Start backend
python app.py

# Install deps
pip install -r requirements.txt

# Create venv
python -m venv venv

# Activate venv (Windows)
venv\Scripts\activate

# Activate venv (Linux/macOS)
source venv/bin/activate

# Test API
python test_api.py

# Run with Docker
docker-compose up
```

---

## 🎯 Supported Cleanup Types

- `cache` - System cache
- `temp` - Temp files
- `logs` - Old logs
- `all` - All above

---

## ✨ Features

✅ SSH command execution
✅ Real-time monitoring
✅ Disk space tracking
✅ Automated cleanup
✅ Database persistence
✅ Async operations
✅ Error handling
✅ Docker support

---

## 🚀 Quick Start Commands

```bash
# Windows
cd backend && run.bat

# Linux/macOS
cd backend && bash run.sh

# Docker
cd backend && docker-compose up

# Direct
cd backend && python app.py
```

---

## 📞 Quick Help

- **Start:** `run.bat` or `run.sh`
- **Test:** `python test_api.py`
- **Docs:** Read FULL_DOCUMENTATION.md
- **Health:** `curl http://localhost:5000/health`

---

## 🎓 Usage Flow

1. Start backend (`run.bat`)
2. Add system (`POST /api/systems`)
3. Get status (`GET /api/systems/{id}/status`)
4. Start cleanup (`POST /api/cleanup`)
5. Check progress (`GET /api/cleanup/{id}`)

---

## 📊 Database Models

**SystemPC** - System configuration
**SystemStatus** - Real-time metrics  
**DiskSpace** - Disk info
**CleanupOperation** - Cleanup logs

---

## 🔧 Environment Setup

```bash
# Create venv
python -m venv venv

# Activate (Windows)
venv\Scripts\activate

# Install
pip install -r requirements.txt

# Configure
copy .env.example .env

# Run
python app.py
```

---

## 💡 Common Tasks

```bash
# Add system
POST /api/systems

# Monitor
GET /api/systems/{id}/status

# Cleanup
POST /api/cleanup

# Track
GET /api/cleanup/{id}
```

---

## 🎉 Done!

Backend is ready. Start with `run.bat` or `run.sh`

**Questions?** Check the documentation files!
