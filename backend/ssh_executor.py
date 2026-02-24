"""
SSH Command Executor - Handles SSH connections and command execution
"""
import paramiko
import logging
from typing import Tuple

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
        self.hostname = hostname
        self.username = username
        self.password = password
        self.private_key_path = private_key_path
        self.port = port
        self.timeout = timeout
        self.client = None
    
    def connect(self) -> bool:
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
    
    def execute_command(self, command: str, sudo_password: str = None) -> Tuple[int, str, str]:
        """
        Execute a command on the remote system
        If sudo_password is provided, it prepends sudo -S and writes password to stdin.
        """
        if not self.client:
            logger.error("SSH client not connected")
            return 1, "", "SSH client not connected"
        
        try:
            if sudo_password:
                # Prepare sudo command
                command = f"sudo -S bash -c \"{command}\""
                stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
                stdin.write(sudo_password + "\n")
                stdin.flush()
            else:
                stdin, stdout, stderr = self.client.exec_command(command, get_pty=True)
            
            return_code = stdout.channel.recv_exit_status()
            stdout_data = stdout.read().decode('utf-8', errors='ignore')
            stderr_data = stderr.read().decode('utf-8', errors='ignore')
            
            logger.info(f"Command executed on {self.hostname}: {command}")
            return return_code, stdout_data, stderr_data
            
        except Exception as e:
            logger.error(f"Error executing command on {self.hostname}: {str(e)}")
            return 1, "", str(e)
    
    def disconnect(self):
        if self.client:
            self.client.close()
            logger.info(f"SSH connection closed to {self.hostname}")
    
    def __enter__(self):
        self.connect()
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        self.disconnect()


class CommandBuilder:
    """Build safe system commands for common operations"""
    
    @staticmethod
    def get_system_info() -> str:
        return "uname -a && echo '---' && cat /proc/cpuinfo | head -5 && echo '---' && free -h"
    
    @staticmethod
    def clean_cache(password: str = None) -> str:
        cmd = "sync && echo 3 > /proc/sys/vm/drop_caches"
        return cmd
    
    @staticmethod
    def clean_temp_files(password: str = None) -> str:
        return "rm -rf /tmp/* /var/tmp/*"
    
    @staticmethod
    def clean_logs(password: str = None) -> str:
        return "find /var/log -type f -name '*.log' -mtime +30 -delete"