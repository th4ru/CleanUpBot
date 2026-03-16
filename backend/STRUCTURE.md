# Backend Folder Structure

```
backend/
│
├── app.py                    # Flask application factory and entry point
├── config.py                 # Configuration management
├── models.py                 # SQLAlchemy database models
├── ssh_executor.py           # SSH client using Paramiko for remote command execution
├── system_utils.py           # Utilities for parsing system information
│
├── routes/                   # API endpoints
│   ├── __init__.py          # Route registration
│   ├── system.py            # System monitoring endpoints
│   └── cleanup.py           # Cleanup operation endpoints
│
├── requirements.txt          # Python dependencies
├── .env.example             # Environment variables template
├── .gitignore               # Git ignore file
│
├── run.bat                  # Windows startup script
├── run.sh                   # Linux/macOS startup script
│
├── Dockerfile               # Docker container configuration
├── docker-compose.yml       # Docker Compose for easy deployment
│
├── README.md                # Project overview and features
├── SETUP.md                 # Installation and setup guide
├── API.md                   # API documentation
├── INTEGRATION.md           # Frontend integration guide
│
└── test_api.py             # API testing script
```

## Quick Start

### Windows
```powershell
cd backend
run.bat
```

### macOS/Linux
```bash
cd backend
bash run.sh
```

### Docker
```bash
cd backend
docker-compose up
```

## Key Features

✅ **SSH Command Execution** - Execute bash commands on remote systems
✅ **System Monitoring** - Real-time CPU, memory, disk monitoring
✅ **Automated Cleanup** - Clean cache, temp files, logs
✅ **Database Tracking** - SQLite/PostgreSQL support
✅ **Async Operations** - Non-blocking cleanup tasks
✅ **CORS Enabled** - Frontend integration ready
✅ **Comprehensive Logging** - Error tracking and debugging

## API Endpoints

### Systems
- `GET /api/systems` - List all systems
- `POST /api/systems` - Add new system
- `GET /api/systems/{id}/status` - Get real-time status
- `GET /api/systems/{id}/disk-space` - Get disk info
- `DELETE /api/systems/{id}` - Remove system

### Cleanup
- `POST /api/cleanup` - Start cleanup operation
- `GET /api/cleanup/{id}` - Check cleanup status
- `GET /api/cleanup/system/{id}` - Get cleanup history

## Environment Variables

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///system_manager.db
SSH_PORT=22
SSH_TIMEOUT=30
CORS_ORIGINS=http://localhost:5173
```

## SSH Support

The backend can execute SSH commands on remote Linux systems:

**Supported Operations:**
- System information retrieval (CPU, memory, disk)
- Disk space analysis
- Cache cleanup
- Temporary file removal
- Log file rotation

**Authentication Methods:**
- Password-based SSH
- Private key authentication

## Dependencies

- Flask - Web framework
- Flask-CORS - Cross-origin support
- Flask-SQLAlchemy - ORM
- Paramiko - SSH client
- python-dotenv - Environment management

## Database Models

1. **SystemPC** - Managed systems configuration
2. **SystemStatus** - Real-time system metrics
3. **DiskSpace** - Disk usage information
4. **CleanupOperation** - Cleanup operation logs

## Production Ready

- Docker containerization
- Error handling and logging
- Database migrations support
- CORS configuration
- Environment-based settings
- Security best practices

## Integration with Frontend

The frontend can call these main functions:

```typescript
// Get system status
callSystemStatusFunction()

// Start cleanup
callCleanupFunction(pcIds, cleanupType)

// Get disk space
callDiskSpaceFunction(systemId)
```

See INTEGRATION.md for detailed setup.
