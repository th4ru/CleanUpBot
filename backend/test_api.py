"""
Test script for backend API
"""
import requests
import json

BASE_URL = 'http://localhost:5000/api'

def test_health():
    """Test health endpoint"""
    print("\n=== Testing Health Check ===")
    response = requests.get('http://localhost:5000/health')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_add_system():
    """Add a test system"""
    print("\n=== Adding Test System ===")
    data = {
        "pcName": "Test-Server-01",
        "ipAddress": "192.168.1.100",
        "username": "admin",
        "password": "password123",
        "sshPort": 22
    }
    response = requests.post(f'{BASE_URL}/systems', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 201:
        return response.json().get('data', {}).get('id')
    return None

def test_get_systems():
    """Get all systems"""
    print("\n=== Getting All Systems ===")
    response = requests.get(f'{BASE_URL}/systems')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_get_system(system_id):
    """Get specific system"""
    print(f"\n=== Getting System {system_id} ===")
    response = requests.get(f'{BASE_URL}/systems/{system_id}')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_system_status(system_id):
    """Get system status"""
    print(f"\n=== Getting System {system_id} Status ===")
    response = requests.get(f'{BASE_URL}/systems/{system_id}/status')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_start_cleanup(system_id):
    """Start cleanup operation"""
    print(f"\n=== Starting Cleanup for System {system_id} ===")
    data = {
        "pcIds": [system_id],
        "cleanupType": "all"
    }
    response = requests.post(f'{BASE_URL}/cleanup', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    
    if response.status_code == 202:
        operations = response.json().get('data', [])
        if operations:
            return operations[0].get('id')
    return None

def test_cleanup_status(operation_id):
    """Get cleanup operation status"""
    print(f"\n=== Getting Cleanup Status {operation_id} ===")
    response = requests.get(f'{BASE_URL}/cleanup/{operation_id}')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_delete_system(system_id):
    """Delete a system"""
    print(f"\n=== Deleting System {system_id} ===")
    response = requests.delete(f'{BASE_URL}/systems/{system_id}')
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

def test_connection():
    """Test SSH connection"""
    print("\n=== Testing SSH Connection ===")
    data = {
        "ipAddress": "192.168.1.100",
        "username": "admin",
        "password": "password123",
        "sshPort": 22
    }
    response = requests.post(f'{BASE_URL}/systems/test-connection', json=data)
    print(f"Status: {response.status_code}")
    print(f"Response: {json.dumps(response.json(), indent=2)}")
    return response.status_code == 200

if __name__ == '__main__':
    print("=" * 50)
    print("Backend API Test Suite")
    print("=" * 50)
    
    try:
        # Test health
        test_health()
        
        # Test adding system
        system_id = test_add_system()
        
        if system_id:
            # Test get systems
            test_get_systems()
            
            # Test get specific system
            test_get_system(system_id)
            
            # Test connection (will fail if host unreachable)
            test_connection()
            
            # Test cleanup
            operation_id = test_start_cleanup(system_id)
            if operation_id:
                test_cleanup_status(operation_id)
            
            # Test delete
            test_delete_system(system_id)
        
        print("\n" + "=" * 50)
        print("Tests Complete!")
        print("=" * 50)
    
    except requests.exceptions.ConnectionError:
        print("ERROR: Could not connect to backend at http://localhost:5000")
        print("Make sure the backend is running: python app.py")
    except Exception as e:
        print(f"ERROR: {str(e)}")
