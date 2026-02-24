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


def execute_cleanup_async(operation_id, system_id, cleanup_type, executor_config, password):
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
            commands = []

            # Pass password to CommandBuilder for sudo commands
            if cleanup_type in ['cache', 'all']:
                commands.append(CommandBuilder.clean_cache(password))

            if cleanup_type in ['temp', 'all']:
                commands.append(CommandBuilder.clean_temp_files(password))

            if cleanup_type in ['logs', 'all']:
                commands.append(CommandBuilder.clean_logs(password))

            total_space_freed = 0
            errors = []

            for command in commands:
                return_code, stdout, stderr = executor.execute_command(command)
                if return_code != 0:
                    errors.append(f"Command failed: {stderr}")

            operation.status = 'success' if not errors else 'failed'
            operation.error_message = '\n'.join(errors) if errors else None
            operation.space_freed = total_space_freed
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
                args=(operation.id, pc_id, cleanup_type, executor_config, system.password)
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