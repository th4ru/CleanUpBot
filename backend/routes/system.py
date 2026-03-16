"""
System endpoints - handle system monitoring and information
"""
from flask import Blueprint, request, jsonify
from datetime import datetime, timedelta
import logging

from models import db, SystemPC, SystemStatus, DiskSpace
from ssh_executor import SSHExecutor, CommandBuilder
from system_utils import SystemInfoParser

logger = logging.getLogger(__name__)
system_bp = Blueprint('system', __name__)


@system_bp.route('/systems', methods=['GET'])
def get_systems():
    """Get list of all managed systems"""
    try:
        systems = SystemPC.query.all()
        return jsonify({
            'success': True,
            'data': [sys.to_dict() for sys in systems]
        }), 200
    except Exception as e:
        logger.error(f"Error fetching systems: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@system_bp.route('/systems', methods=['POST'])
def add_system():
    """Add a new system to management"""
    try:
        data = request.get_json()
        
        # Validate required fields
        required_fields = ['pcName', 'ipAddress', 'username']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        # Check if system already exists
        existing = SystemPC.query.filter_by(pc_name=data['pcName']).first()
        if existing:
            return jsonify({
                'success': False,
                'error': 'System already exists'
            }), 409
        
        # Create new system
        new_system = SystemPC(
            pc_name=data['pcName'],
            ip_address=data['ipAddress'],
            username=data['username'],
            password=data.get('password'),
            private_key_path=data.get('privateKeyPath'),
            ssh_port=data.get('sshPort', 22)
        )
        
        db.session.add(new_system)
        db.session.commit()
        
        logger.info(f"System added: {data['pcName']}")
        return jsonify({
            'success': True,
            'data': new_system.to_dict()
        }), 201
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error adding system: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@system_bp.route('/systems/<int:system_id>', methods=['GET'])
def get_system(system_id):
    """Get specific system details"""
    try:
        system = SystemPC.query.get(system_id)
        if not system:
            return jsonify({
                'success': False,
                'error': 'System not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': system.to_dict()
        }), 200
    except Exception as e:
        logger.error(f"Error fetching system {system_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@system_bp.route('/systems/<int:system_id>', methods=['DELETE'])
def delete_system(system_id):
    """Delete a system from management"""
    try:
        system = SystemPC.query.get(system_id)
        if not system:
            return jsonify({
                'success': False,
                'error': 'System not found'
            }), 404
        
        db.session.delete(system)
        db.session.commit()
        
        logger.info(f"System deleted: {system.pc_name}")
        return jsonify({
            'success': True,
            'message': 'System deleted'
        }), 200
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error deleting system {system_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@system_bp.route('/systems/<int:system_id>/status', methods=['GET'])
def get_system_status(system_id):
    """Get current system status"""
    try:
        system = SystemPC.query.get(system_id)
        if not system:
            return jsonify({
                'success': False,
                'error': 'System not found'
            }), 404
        
        # Try to connect and get status
        executor = SSHExecutor(
            system.ip_address,
            system.username,
            system.password,
            system.private_key_path,
            system.ssh_port
        )
        
        if not executor.connect():
            system.status = 'offline'
            db.session.commit()
            return jsonify({
                'success': True,
                'data': {
                    'systemId': system.id,
                    'status': 'offline',
                    'message': 'Connection failed'
                }
            }), 200
        
        # Get system info
        try:
            # Uptime
            _, uptime_str, _ = executor.execute_command(CommandBuilder.get_uptime())
            
            # CPU usage
            _, cpu_str, _ = executor.execute_command(CommandBuilder.get_cpu_usage())
            cpu_info = SystemInfoParser.parse_cpu_usage(cpu_str)
            
            # Memory usage
            _, mem_str, _ = executor.execute_command(CommandBuilder.get_memory_usage())
            mem_info = SystemInfoParser.parse_memory_usage(mem_str)
            
            # Disk usage
            _, disk_str, _ = executor.execute_command(CommandBuilder.get_disk_space())
            disk_info = SystemInfoParser.parse_disk_space(disk_str)
            
            system.status = 'online'
            system.last_seen = datetime.utcnow()
            
            # Save status to database
            system_status = SystemStatus(
                system_id=system.id,
                uptime=uptime_str.strip(),
                cpu_usage=cpu_info.get('user', 0),
                memory_usage=mem_info.get('used', '0')
            )
            db.session.add(system_status)
            db.session.commit()
            
            return jsonify({
                'success': True,
                'data': {
                    'systemId': system.id,
                    'status': 'online',
                    'uptime': uptime_str.strip(),
                    'cpuUsage': cpu_info.get('user', 0),
                    'memoryInfo': mem_info,
                    'diskInfo': disk_info[:1]  # Return main disk
                }
            }), 200
        
        finally:
            executor.disconnect()
    
    except Exception as e:
        logger.error(f"Error getting status for system {system_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@system_bp.route('/systems/<int:system_id>/disk-space', methods=['GET'])
def get_disk_space(system_id):
    """Get disk space information for a system"""
    try:
        system = SystemPC.query.get(system_id)
        if not system:
            return jsonify({
                'success': False,
                'error': 'System not found'
            }), 404
        
        executor = SSHExecutor(
            system.ip_address,
            system.username,
            system.password,
            system.private_key_path,
            system.ssh_port
        )
        
        if not executor.connect():
            return jsonify({
                'success': False,
                'error': 'Failed to connect to system'
            }), 503
        
        try:
            _, disk_str, _ = executor.execute_command(CommandBuilder.get_disk_space())
            disk_info = SystemInfoParser.parse_disk_space(disk_str)
            
            return jsonify({
                'success': True,
                'data': disk_info
            }), 200
        
        finally:
            executor.disconnect()
    
    except Exception as e:
        logger.error(f"Error getting disk space for system {system_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@system_bp.route('/systems/test-connection', methods=['POST'])
def test_connection():
    """Test SSH connection to a system"""
    try:
        data = request.get_json()
        
        required_fields = ['ipAddress', 'username']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        executor = SSHExecutor(
            data['ipAddress'],
            data['username'],
            data.get('password'),
            data.get('privateKeyPath'),
            data.get('sshPort', 22)
        )
        
        if executor.connect():
            _, uptime, _ = executor.execute_command(CommandBuilder.get_uptime())
            executor.disconnect()
            
            return jsonify({
                'success': True,
                'message': 'Connection successful',
                'data': {'uptime': uptime.strip()}
            }), 200
        else:
            return jsonify({
                'success': False,
                'error': 'Connection failed'
            }), 503
    
    except Exception as e:
        logger.error(f"Error testing connection: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@system_bp.route('/systems/<int:system_id>/history', methods=['GET'])
def get_system_history(system_id):
    """Get system status history"""
    try:
        hours = request.args.get('hours', 24, type=int)
        
        system = SystemPC.query.get(system_id)
        if not system:
            return jsonify({
                'success': False,
                'error': 'System not found'
            }), 404
        
        since = datetime.utcnow() - timedelta(hours=hours)
        history = SystemStatus.query.filter_by(system_id=system_id).filter(
            SystemStatus.recorded_at >= since
        ).order_by(SystemStatus.recorded_at.desc()).limit(100).all()
        
        return jsonify({
            'success': True,
            'data': [h.to_dict() for h in history]
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching history for system {system_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
