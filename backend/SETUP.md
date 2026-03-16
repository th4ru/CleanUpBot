# Flask Backend Setup Guide

## Installation Steps

### 1. Navigate to Backend
```powershell
cd backend
```

### 2. Create Virtual Environment
```powershell
python -m venv venv
```

### 3. Activate Virtual Environment
```powershell
# On Windows
venv\Scripts\activate

# On macOS/Linux
source venv/bin/activate
```

### 4. Install Dependencies
```powershell
pip install -r requirements.txt
```

### 5. Create .env File
Create a file named `.env` in the backend directory:

```env
FLASK_ENV=development
SECRET_KEY=super-secret-key-change-this-in-production
DATABASE_URL=sqlite:///system_manager.db
SSH_PORT=22
SSH_TIMEOUT=30
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### 6. Run Backend
```powershell
python app.py
```

Backend will be running at `http://localhost:5000`

## Frontend Configuration

Update `frontend/src/utils/api.ts` to use the backend:

```typescript
const getBackendUrl = () => 'http://localhost:5000/api';

export async function callSystemStatusFunction() {
  const apiUrl = `${getBackendUrl()}/systems`;
  // ... rest of implementation
}

export async function callCleanupFunction(pcIds: string[], cleanupType: string) {
  const apiUrl = `${getBackendUrl()}/cleanup`;
  // ... rest of implementation
}
```

## Testing Connection

```bash
# Test if backend is running
curl http://localhost:5000/health

# Get all systems
curl http://localhost:5000/api/systems

# Add new system
curl -X POST http://localhost:5000/api/systems \
  -H "Content-Type: application/json" \
  -d '{"pcName":"PC1","ipAddress":"192.168.1.100","username":"admin"}'
```

## Troubleshooting

**Module not found errors:**
```bash
pip install -r requirements.txt
```

**Port already in use:**
Edit `app.py` last line: `app.run(debug=True, host='0.0.0.0', port=5001)`

**SSH connection fails:**
- Verify IP address and credentials
- Check if SSH is enabled on target system
- Verify firewall allows SSH (port 22)
- Test with: `POST /api/systems/test-connection`

## Production Deployment

For production, update config:

```python
# Use production config
app = create_app('production')

# Use PostgreSQL instead of SQLite
DATABASE_URL=postgresql://user:pass@host:5432/db

# Set strong secret key
SECRET_KEY=<generate-strong-key>

# Run with gunicorn
gunicorn -w 4 app:create_app('production')
```

## Database Initialization

Tables are created automatically on first run. To reset database:

```bash
# Delete the database
rm system_manager.db

# Restart app - tables will be recreated
python app.py
```

## API Endpoints Summary

| Method | Endpoint | Purpose |
|--------|----------|---------|
| GET | `/api/systems` | List all systems |
| POST | `/api/systems` | Add new system |
| GET | `/api/systems/<id>` | Get system details |
| GET | `/api/systems/<id>/status` | Get real-time status |
| GET | `/api/systems/<id>/disk-space` | Get disk info |
| DELETE | `/api/systems/<id>` | Remove system |
| POST | `/api/cleanup` | Start cleanup |
| GET | `/api/cleanup` | List cleanup ops |
| GET | `/health` | Health check |

## Stopping Backend

Press `Ctrl+C` in the terminal running the backend.

## Next Steps

1. Start backend: `python app.py`
2. Update frontend API URLs
3. Test connections
4. Add systems in frontend
5. Run cleanup operations
