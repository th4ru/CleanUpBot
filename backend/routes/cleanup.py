"""
Cleanup endpoints - handle system cleanup operations
"""
from flask import Blueprint, request, jsonify
from datetime import datetime
import logging
from threading import Thread

from models import db, SystemPC, CleanupOperation
from ssh_executor import SSHExecutor, CommandBuilder

logger = logging.getLogger(__name__)
cleanup_bp = Blueprint('cleanup', __name__)


def execute_cleanup_async(operation_id, system_id, cleanup_type, executor_config):
    """Execute cleanup operation asynchronously"""
    try:
        operation = CleanupOperation.query.get(operation_id)
        if not operation:
            return
        
        operation.status = 'running'
        db.session.commit()
        
        executor = SSHExecutor(**executor_config)
        
        if not executor.connect():
            operation.status = 'failed'
            operation.error_message = 'Failed to connect to system'
            operation.completed_at = datetime.utcnow()
            db.session.commit()
            executor.disconnect()
            return
        
        try:
            import os
            # Get path to system_cleanup.sh
            script_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
            script_path = os.path.join(script_dir, 'system_cleanup.sh')
            
            total_space_freed = 0
            errors = []
            
            return_code, stdout, stderr = executor.execute_script(script_path, args="--force")
            if return_code != 0:
                errors.append(f"Script failed: {stderr}")
            
            # Extract space freed from stdout if possible
            import re
            space_freed_match = re.search(r"Space freed:\s+(.*?)\s+\(", stdout)
            
            operation.status = 'failed' if errors else 'success'
            operation.space_freed = str(total_space_freed)
            if space_freed_match:
                operation.space_freed = space_freed_match.group(1).strip()
                
            if errors:
                operation.error_message = "; ".join(errors)
                
            operation.completed_at = datetime.utcnow()
            
        except Exception as e:
            operation.status = 'failed'
            operation.error_message = str(e)
            operation.completed_at = datetime.utcnow()
            logger.error(f"Error during cleanup operation {operation_id}: {str(e)}")
        
        finally:
            executor.disconnect()
            db.session.commit()
    
    except Exception as e:
        logger.error(f"Error in cleanup async: {str(e)}")


@cleanup_bp.route('/cleanup', methods=['POST'])
def start_cleanup():
    """Start a cleanup operation"""
    try:
        data = request.get_json()
        
        required_fields = ['pcIds', 'cleanupType']
        if not all(field in data for field in required_fields):
            return jsonify({
                'success': False,
                'error': 'Missing required fields'
            }), 400
        
        pc_ids = data['pcIds']
        cleanup_type = data['cleanupType']
        
        if cleanup_type not in ['cache', 'temp', 'logs', 'all']:
            return jsonify({
                'success': False,
                'error': 'Invalid cleanup type'
            }), 400
        
        operations = []
        
        for pc_id in pc_ids:
            system = SystemPC.query.get(pc_id)
            if not system:
                continue
            
            # Create cleanup operation record
            operation = CleanupOperation(
                system_id=pc_id,
                cleanup_type=cleanup_type,
                status='pending'
            )
            db.session.add(operation)
            db.session.commit()
            
            # Execute cleanup asynchronously
            executor_config = {
                'hostname': system.ip_address,
                'username': system.username,
                'password': system.password,
                'private_key_path': system.private_key_path,
                'port': system.ssh_port
            }
            
            thread = Thread(
                target=execute_cleanup_async,
                args=(operation.id, pc_id, cleanup_type, executor_config)
            )
            thread.daemon = True
            thread.start()
            
            operations.append(operation.to_dict())
        
        logger.info(f"Cleanup operations started for {len(pc_ids)} systems")
        return jsonify({
            'success': True,
            'data': operations
        }), 202
    
    except Exception as e:
        db.session.rollback()
        logger.error(f"Error starting cleanup: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cleanup_bp.route('/cleanup/<int:operation_id>', methods=['GET'])
def get_cleanup_status(operation_id):
    """Get cleanup operation status"""
    try:
        operation = CleanupOperation.query.get(operation_id)
        if not operation:
            return jsonify({
                'success': False,
                'error': 'Operation not found'
            }), 404
        
        return jsonify({
            'success': True,
            'data': operation.to_dict()
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching cleanup status {operation_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cleanup_bp.route('/cleanup/system/<int:system_id>', methods=['GET'])
def get_cleanup_history(system_id):
    """Get cleanup operation history for a system"""
    try:
        limit = request.args.get('limit', 50, type=int)
        
        system = SystemPC.query.get(system_id)
        if not system:
            return jsonify({
                'success': False,
                'error': 'System not found'
            }), 404
        
        operations = CleanupOperation.query.filter_by(system_id=system_id).order_by(
            CleanupOperation.started_at.desc()
        ).limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [op.to_dict() for op in operations]
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching cleanup history for system {system_id}: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@cleanup_bp.route('/cleanup', methods=['GET'])
def get_all_cleanup_operations():
    """Get all cleanup operations"""
    try:
        status = request.args.get('status')
        limit = request.args.get('limit', 100, type=int)
        
        query = CleanupOperation.query.order_by(CleanupOperation.started_at.desc())
        
        if status:
            query = query.filter_by(status=status)
        
        operations = query.limit(limit).all()
        
        return jsonify({
            'success': True,
            'data': [op.to_dict() for op in operations]
        }), 200
    
    except Exception as e:
        logger.error(f"Error fetching cleanup operations: {str(e)}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500
