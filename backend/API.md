# System Manager - Backend

A Python Flask backend for managing and monitoring remote systems via SSH.

## Features

- **SSH Command Execution** - Execute bash/shell commands on remote systems
- **System Monitoring** - Real-time CPU, memory, and disk monitoring
- **System Cleanup** - Automated cleanup of cache, temp files, and logs
- **Database Tracking** - Store system information and operation history
- **Async Operations** - Non-blocking cleanup operations with threading
- **CORS Support** - Integrated CORS for frontend integration

## Quick Start

```bash
# Setup
cd backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Configure
cp .env.example .env  # Edit with your settings

# Run
python app.py
```

Server runs on `http://localhost:5000`

## Environment Variables

```env
FLASK_ENV=development
SECRET_KEY=your-secret-key
DATABASE_URL=sqlite:///system_manager.db
SSH_PORT=22
SSH_TIMEOUT=30
CORS_ORIGINS=http://localhost:5173
```

## API Documentation

### Systems

**GET /api/systems** - List all systems
```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "pcName": "Server-01",
      "ipAddress": "192.168.1.100",
      "status": "online",
      "lastSeen": "2026-01-26T10:30:00"
    }
  ]
}
```

**POST /api/systems** - Add system
```json
{
  "pcName": "Server-01",
  "ipAddress": "192.168.1.100",
  "username": "admin",
  "password": "password",
  "sshPort": 22
}
```

**GET /api/systems/{id}/status** - Get system status
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
      "free": "7.8Gi"
    }
  }
}
```

### Cleanup

**POST /api/cleanup** - Start cleanup
```json
{
  "pcIds": [1, 2, 3],
  "cleanupType": "all"
}
```

**GET /api/cleanup/{id}** - Check status
```json
{
  "success": true,
  "data": {
    "id": 1,
    "systemId": 1,
    "cleanupType": "all",
    "status": "success",
    "spaceFreed": 5368709120,
    "completedAt": "2026-01-26T10:35:00"
  }
}
```

## Project Structure

```
backend/
├── app.py                 # Application factory
├── config.py             # Configuration
├── models.py             # Database models
├── ssh_executor.py       # SSH client (Paramiko)
├── system_utils.py       # Parsing utilities
├── routes/
│   ├── __init__.py
│   ├── system.py         # System endpoints
│   └── cleanup.py        # Cleanup endpoints
├── requirements.txt      # Python dependencies
├── README.md            # Documentation
└── .env                 # Environment variables (not committed)
```

## Dependencies

- **Flask** - Web framework
- **Flask-CORS** - CORS support
- **Flask-SQLAlchemy** - ORM
- **Paramiko** - SSH client
- **python-dotenv** - Environment variables

## Key Components

### SSHExecutor
Handles SSH connections and command execution using Paramiko.
Supports both password and key-based authentication.

### CommandBuilder
Pre-built safe commands for common operations:
- System info (uname, CPU, memory)
- Disk space (df -h)
- Cleanup (cache, temp, logs)
- Process management

### SystemInfoParser
Parses command outputs from remote systems and converts to structured data.

## Usage Examples

### Add System
```bash
curl -X POST http://localhost:5000/api/systems \
  -H "Content-Type: application/json" \
  -d '{
    "pcName": "Lab-PC-01",
    "ipAddress": "192.168.1.100",
    "username": "admin",
    "password": "secret"
  }'
```

### Get System Status
```bash
curl http://localhost:5000/api/systems/1/status
```

### Start Cleanup
```bash
curl -X POST http://localhost:5000/api/cleanup \
  -H "Content-Type: application/json" \
  -d '{
    "pcIds": [1],
    "cleanupType": "all"
  }'
```

## Supported Cleanup Types

- `cache` - Clear system cache
- `temp` - Remove temporary files
- `logs` - Clean old log files
- `all` - All of the above

## Security Considerations

1. **SSH Credentials** - Stored in database; use encryption in production
2. **Secret Key** - Change SECRET_KEY in production
3. **CORS** - Configure to trusted origins only
4. **Environment Variables** - Keep .env secure and out of version control

## Performance

- Async cleanup operations prevent blocking
- Connection pooling through Paramiko
- Efficient database queries with SQLAlchemy
- Configurable timeouts for SSH operations

## Error Handling

- Graceful SSH connection failures
- Command execution error reporting
- Database rollback on failures
- Comprehensive logging

## Future Enhancements

- [ ] Database encryption for credentials
- [ ] API authentication/authorization
- [ ] Task scheduling (Celery)
- [ ] Metrics and analytics
- [ ] System alerts/notifications
- [ ] Batch operations optimization
