"""
Cleanup endpoints - handle system cleanup operations
"""
from flask import Blueprint, request, jsonify, current_app
from datetime import datetime
import logging
from threading import Thread
from concurrent.futures import ThreadPoolExecutor, TimeoutError

from models import db, SystemPC, CleanupOperation
from ssh_executor import SSHExecutor, CommandBuilder

logger = logging.getLogger(__name__)
cleanup_bp = Blueprint('cleanup', __name__)


def execute_cleanup_async(app, operation_id, system_id, cleanup_type, executor_config):
    """Execute cleanup operation asynchronously"""
    with app.app_context():
        try:
            operation = CleanupOperation.query.get(operation_id)
            if not operation:
                return

            logger.info(f"Starting cleanup async for operation {operation_id} (system {system_id})")
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
                # Quick check: ensure we can run sudo without password prompts.
                # If the remote host requires a password, the cleanup cannot proceed.
                sudo_check_exit, _, sudo_check_err = executor.execute_command("sudo -n true")
                if sudo_check_exit != 0:
                    operation.status = 'failed'
                    operation.error_message = (
                        "Remote host requires sudo password; configure passwordless sudo "
                        "for the cleanup user, or run the agent as a user with sudo rights. "
                        f"(sudo error: {sudo_check_err.strip()})"
                    )
                    operation.completed_at = datetime.utcnow()
                    db.session.commit()
                    return

                commands = []

                # For the "all" cleanup type, run the full cleanup script (no size limits).
                if cleanup_type == 'all':
                    commands.append(CommandBuilder.clean_full_system())
                else:
                    if cleanup_type == 'cache':
                        commands.append(CommandBuilder.clean_cache())
                    if cleanup_type == 'temp':
                        commands.append(CommandBuilder.clean_temp_files())
                    if cleanup_type == 'logs':
                        commands.append(CommandBuilder.clean_logs())

                total_space_freed = 0
                errors = []

                # Run each command with a hard timeout so a hung remote process doesn't block indefinitely
                COMMAND_TIMEOUT_SECONDS = 600  # 10 minutes

                def run_command_with_timeout(cmd: str):
                    with ThreadPoolExecutor(max_workers=1) as executor_pool:
                        future = executor_pool.submit(executor.execute_command, cmd)
                        try:
                            return future.result(timeout=COMMAND_TIMEOUT_SECONDS)
                        except TimeoutError:
                            future.cancel()
                            return 1, "", f"Command timed out after {COMMAND_TIMEOUT_SECONDS} seconds"
                        except Exception as exc:
                            return 1, "", str(exc)

                for command in commands:
                    logger.info(f"Running cleanup command for operation {operation_id}: {command}")
                    return_code, stdout, stderr = run_command_with_timeout(command)
                    logger.info(
                        f"Cleanup command completed for operation {operation_id}: exit={return_code}, "
                        f"stdout={stdout[:500]!r}, stderr={stderr[:500]!r}"
                    )

                    if return_code != 0:
                        errors.append(f"Command failed (exit {return_code}): {stderr or stdout}")

                operation.status = 'failed' if errors else 'success'
                operation.error_message = "\n".join(errors) if errors else None
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
            db.session.rollback()
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
            
            # Create cleanup operation record (start as running immediately)
            operation = CleanupOperation(
                system_id=pc_id,
                cleanup_type=cleanup_type,
                status='running',
                started_at=datetime.utcnow()
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
                args=(current_app._get_current_object(), operation.id, pc_id, cleanup_type, executor_config)
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
