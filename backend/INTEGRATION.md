# Frontend-Backend Integration Guide

## Overview

This guide shows how to integrate the Flask backend with your React frontend.

## Step 1: Start Backend

### Option A: Direct Python
```powershell
cd backend
python -m venv venv
venv\Scripts\activate
pip install -r requirements.txt
copy .env.example .env  # Edit if needed
python app.py
```

### Option B: Using run script
```powershell
cd backend
./run.bat  # Windows
# or
./run.sh   # macOS/Linux
```

### Option C: Docker
```bash
cd backend
docker-compose up
```

Backend will run on: `http://localhost:5000`

## Step 2: Update Frontend API Configuration

Edit `frontend/src/utils/api.ts`:

```typescript
const getBackendUrl = () => {
  return process.env.VITE_API_URL || 'http://localhost:5000/api';
};

export async function callSystemStatusFunction() {
  const apiUrl = `${getBackendUrl()}/systems`;
  
  try {
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('System status function error:', error);
    throw error;
  }
}

export async function callCleanupFunction(
  pcIds: string[],
  cleanupType: 'cache' | 'temp' | 'logs' | 'all'
) {
  const apiUrl = `${getBackendUrl()}/cleanup`;

  try {
    const response = await fetch(apiUrl, {
      method: 'POST',
      headers: {
        'Content-Type': 'application/json',
      },
      body: JSON.stringify({ pcIds, cleanupType }),
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Cleanup function error:', error);
    throw error;
  }
}

// New function to get disk space
export async function callDiskSpaceFunction(systemId: number) {
  const apiUrl = `${getBackendUrl()}/systems/${systemId}/disk-space`;

  try {
    const response = await fetch(apiUrl, {
      method: 'GET',
      headers: {
        'Content-Type': 'application/json',
      },
    });

    if (!response.ok) {
      throw new Error(`Error: ${response.statusText}`);
    }

    return await response.json();
  } catch (error) {
    console.error('Disk space function error:', error);
    throw error;
  }
}
```

## Step 3: Add Environment Variable

Create `frontend/.env.local`:

```env
VITE_API_URL=http://localhost:5000/api
```

## Step 4: Update Component Examples

### System Status View
```typescript
import { useEffect, useState } from 'react';

function SystemStatusView() {
  const [systems, setSystems] = useState([]);
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    fetchSystems();
  }, []);

  const fetchSystems = async () => {
    try {
      setLoading(true);
      const response = await callSystemStatusFunction();
      if (response.success) {
        setSystems(response.data);
      }
    } catch (error) {
      console.error('Failed to fetch systems:', error);
    } finally {
      setLoading(false);
    }
  };

  // ... rest of component
}
```

### Cleanup View
```typescript
const handleStartCleanup = async () => {
  try {
    setIsRunning(true);
    
    const systemIds = systems.map(s => s.id);
    const response = await callCleanupFunction(systemIds, 'all');
    
    if (response.success) {
      // Handle successful cleanup start
      setLogs([...response.data, ...logs]);
    }
  } catch (error) {
    console.error('Cleanup failed:', error);
  } finally {
    setIsRunning(false);
  }
};
```

## Step 5: Test Connection

Run the test script:

```bash
cd backend
pip install requests
python test_api.py
```

Or test manually:

```bash
# Test backend health
curl http://localhost:5000/health

# Get all systems
curl http://localhost:5000/api/systems

# Add new system
curl -X POST http://localhost:5000/api/systems \
  -H "Content-Type: application/json" \
  -d '{
    "pcName": "Lab-PC-01",
    "ipAddress": "192.168.1.100",
    "username": "admin",
    "password": "password"
  }'
```

## Step 6: Run Full Stack

### Terminal 1 - Backend
```bash
cd backend
python app.py
```

### Terminal 2 - Frontend
```bash
cd frontend
npm run dev
```

Access application: `http://localhost:5173`

## API Response Format

All endpoints return responses in this format:

```json
{
  "success": true,
  "data": {...} or [...],
  "error": "error message if failed"
}
```

## Available Backend Endpoints

### System Management
- `GET /api/systems` - Get all systems
- `POST /api/systems` - Add new system
- `GET /api/systems/{id}` - Get system details
- `GET /api/systems/{id}/status` - Get real-time status
- `GET /api/systems/{id}/disk-space` - Get disk space info
- `GET /api/systems/{id}/history` - Get status history
- `DELETE /api/systems/{id}` - Remove system
- `POST /api/systems/test-connection` - Test SSH connection

### Cleanup Operations
- `POST /api/cleanup` - Start cleanup
- `GET /api/cleanup` - Get all cleanup operations
- `GET /api/cleanup/{id}` - Get cleanup operation status
- `GET /api/cleanup/system/{id}` - Get cleanup history

## Debugging

### Backend not responding?
```bash
# Check if running
curl http://localhost:5000/health

# Check logs in terminal
# Should show: "Running on http://0.0.0.0:5000"
```

### CORS errors?
Backend has CORS enabled. Make sure frontend URL is in `CORS_ORIGINS` env var:
```env
CORS_ORIGINS=http://localhost:5173,http://localhost:3000
```

### SSH connection fails?
- Verify IP address is correct
- Verify SSH port (default 22)
- Verify credentials
- Check firewall allows SSH

## Database

SQLite database created automatically at `backend/system_manager.db`

To reset:
```bash
rm backend/system_manager.db
python backend/app.py  # Will recreate tables
```

## Production Deployment

### Deployment Steps

1. **Build frontend**
   ```bash
   cd frontend
   npm run build
   ```

2. **Configure backend**
   - Update `SECRET_KEY` in .env
   - Switch to PostgreSQL: `DATABASE_URL=postgresql://...`
   - Update `CORS_ORIGINS`

3. **Deploy**
   ```bash
   # Using Docker
   docker-compose -f docker-compose.yml up -d

   # Or using Gunicorn
   gunicorn -w 4 --bind 0.0.0.0:5000 app:create_app('production')
   ```

## Performance Tips

1. **Enable caching** - Cache system status for non-critical monitoring
2. **Batch operations** - Group SSH commands when possible
3. **Use connection pooling** - Configure in production database
4. **Monitor logs** - Check for slow queries or failed connections

## Security Checklist

- [ ] Change `SECRET_KEY` in production
- [ ] Use HTTPS in production
- [ ] Restrict `CORS_ORIGINS` to known domains
- [ ] Use SSH keys instead of passwords when possible
- [ ] Encrypt SSH credentials in database
- [ ] Use environment variables for sensitive data
- [ ] Regular security updates for dependencies
- [ ] Enable API rate limiting
- [ ] Use strong authentication/authorization

## Support

For issues:
1. Check logs in backend terminal
2. Verify connectivity with `curl`
3. Test with `test_api.py` script
4. Check database connection
5. Verify SSH credentials
