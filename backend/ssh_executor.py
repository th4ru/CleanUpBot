"""
SSH Command Executor - Handles SSH connections and command execution
"""
import paramiko
import logging
from typing import Tuple, Dict, Any
from paramiko.ssh_exception import (
    AuthenticationException,
    SSHException,
    NoValidConnectionsError
)

logger = logging.getLogger(__name__)


class SSHExecutor:
    """Execute commands on remote systems via SSH"""
    
    def __init__(self, hostname: str, username: str, password: str = None, 
                 private_key_path: str = None, port: int = 22, timeout: int = 30):
        """
        Initialize SSH connection parameters
        
        Args:
            hostname: IP address or hostname of the remote system
            username: SSH username
            password: SSH password (if using password auth)
            private_key_path: Path to private key (if using key auth)
            port: SSH port (default: 22)
            timeout: Connection timeout in seconds
        """
        self.hostname = hostname
        self.username = username
        self.password = password
        self.private_key_path = private_key_path
        self.port = port
        self.timeout = timeout
        self.client = None
    
    def connect(self) -> bool:
        """
        Establish SSH connection
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            self.client = paramiko.SSHClient()
            self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if self.private_key_path:
                self.client.connect(
                    self.hostname,
                    port=self.port,
                    username=self.username,
                    key_filename=self.private_key_path,
                    timeout=self.timeout
                )
            else:
                self.client.connect(
                    self.hostname,
                    port=self.port,
                    username=self.username,
                    password=self.password,
                    timeout=self.timeout
                )
            
            logger.info(f"SSH connection established to {self.hostname}")
            return True
            
        except AuthenticationException:
            logger.error(f"Authentication failed for {self.hostname}")
            return False
        except (SSHException, NoValidConnectionsError) as e:
            logger.error(f"SSH connection failed to {self.hostname}: {str(e)}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error connecting to {self.hostname}: {str(e)}")
            return False
    
    def execute_command(self, command: str) -> Tuple[int, str, str]:
        """
        Execute a command on the remote system
        
        Args:
            command: Command to execute
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        if not self.client:
            logger.error("SSH client not connected")
            return 1, "", "SSH client not connected"
        
        try:
            stdin, stdout, stderr = self.client.exec_command(command, timeout=self.timeout)
            return_code = stdout.channel.recv_exit_status()
            stdout_data = stdout.read().decode('utf-8', errors='ignore')
            stderr_data = stderr.read().decode('utf-8', errors='ignore')
            
            logger.info(f"Command executed on {self.hostname}: {command}")
            return return_code, stdout_data, stderr_data
            
        except Exception as e:
            logger.error(f"Error executing command on {self.hostname}: {str(e)}")
            return 1, "", str(e)
    
    def disconnect(self):
        """Close SSH connection"""
        if self.client:
            self.client.close()
            logger.info(f"SSH connection closed to {self.hostname}")

    def execute_script(self, script_path: str, args: str = "") -> Tuple[int, str, str]:
        """
        Upload and execute a local script on the remote system with sudo.
        
        Args:
            script_path: Path to the local script file
            args: Arguments to pass to the script
            
        Returns:
            Tuple of (return_code, stdout, stderr)
        """
        if not self.client:
            logger.error("SSH client not connected")
            return 1, "", "SSH client not connected"
            
        try:
            # Upload script
            sftp = self.client.open_sftp()
            remote_path = f"/tmp/uploaded_script_{id(self)}.sh"
            sftp.put(script_path, remote_path)
            sftp.close()
            
            # Make executable and run with sudo
            command = f"chmod +x {remote_path} && sudo {remote_path} {args}; EXIT_CODE=$?; rm -f {remote_path}; exit $EXIT_CODE"
            return self.execute_command(command)
        except Exception as e:
            logger.error(f"Error executing script on {self.hostname}: {str(e)}")
            return 1, "", str(e)
    
    def __enter__(self):
        """Context manager entry"""
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        """Context manager exit"""
        self.disconnect()


class CommandBuilder:
    """Build safe system commands for common operations"""
    
    @staticmethod
    def get_system_info() -> str:
        """Get system information command"""
        return "uname -a && echo '---' && cat /proc/cpuinfo | head -5 && echo '---' && free -h"
    
    @staticmethod
    def get_disk_space() -> str:
        """Get disk space information"""
        return "df -h"
    
    @staticmethod
    def get_memory_usage() -> str:
        """Get memory usage"""
        return "free -h"
    
    @staticmethod
    def get_cpu_usage() -> str:
        """Get CPU usage"""
        return "top -bn1 | head -3"
    
    @staticmethod
    def get_uptime() -> str:
        """Get system uptime"""
        return "uptime"
    
    @staticmethod
    def clean_cache() -> str:
        """Clean system cache (Linux)"""
        return "sync && echo 3 | sudo tee /proc/sys/vm/drop_caches"
    
    @staticmethod
    def clean_temp_files() -> str:
        """Clean temporary files"""
        return "sudo rm -rf /tmp/* /var/tmp/*"
    
    @staticmethod
    def clean_logs() -> str:
        """Clean old log files"""
        return "sudo find /var/log -type f -name '*.log' -mtime +30 -delete"
    
    @staticmethod
    def get_running_processes() -> str:
        """Get list of running processes"""
        return "ps aux"
    
    @staticmethod
    def check_connectivity(target_host: str) -> str:
        """Check connectivity to a host"""
        return f"ping -c 4 {target_host}"
