# Backend Configuration

## Required Environment Variables

Create a `.env` file in the backend directory:

```env
# Flask Configuration
FLASK_ENV=development
SECRET_KEY=your-secret-key-here

# Database
DATABASE_URL=sqlite:///system_manager.db
# For PostgreSQL: postgresql://user:password@localhost:5432/system_manager

# SSH Configuration
SSH_PORT=22
SSH_TIMEOUT=30

# CORS Configuration
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

## Installation

1. Navigate to backend folder:
```bash
cd backend
```

2. Create virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

4. Create `.env` file with required variables

5. Run the application:
```bash
python app.py
```

The server will start on `http://localhost:5000`

## API Endpoints

### System Management

- `GET /api/systems` - Get all managed systems
- `POST /api/systems` - Add new system
- `GET /api/systems/<id>` - Get system details
- `DELETE /api/systems/<id>` - Remove system
- `GET /api/systems/<id>/status` - Get real-time system status
- `GET /api/systems/<id>/disk-space` - Get disk space info
- `GET /api/systems/<id>/history` - Get status history
- `POST /api/systems/test-connection` - Test SSH connection

### Cleanup Operations

- `POST /api/cleanup` - Start cleanup operation
- `GET /api/cleanup` - Get all cleanup operations
- `GET /api/cleanup/<id>` - Get cleanup operation status
- `GET /api/cleanup/system/<id>` - Get cleanup history for system

### Health Check

- `GET /health` - Check server health

## Architecture

- `app.py` - Application factory and entry point
- `config.py` - Configuration management
- `models.py` - Database models
- `ssh_executor.py` - SSH command execution (uses Paramiko)
- `system_utils.py` - Parsing and utility functions
- `routes/` - API endpoints
  - `system.py` - System monitoring endpoints
  - `cleanup.py` - Cleanup operation endpoints

## Database

SQLite is used by default for development. For production, configure PostgreSQL:

```env
DATABASE_URL=postgresql://user:password@localhost:5432/system_manager
```

## SSH Authentication

The backend supports both:
1. **Password authentication** - Pass `password` in request
2. **Key-based authentication** - Pass `privateKeyPath` in request

## Security Notes

- SSH credentials are stored encrypted in production
- Use strong SECRET_KEY in production
- Restrict CORS_ORIGINS to trusted domains
- Use environment variables for sensitive data
- Never commit `.env` file to version control
