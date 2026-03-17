"""
SSH Command Executor - Handles SSH connections and command execution
"""
import paramiko
import logging
from pathlib import Path
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
            # Request a pseudo-terminal to satisfy sudo environments that require a tty.
            stdin, stdout, stderr = self.client.exec_command(
                command,
                timeout=self.timeout,
                get_pty=True
            )
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
        return "sync && echo 3 | sudo -n tee /proc/sys/vm/drop_caches"
    
    @staticmethod
    def clean_temp_files() -> str:
        """Clean temporary files"""
        return "sudo -n rm -rf /tmp/* /var/tmp/*"
    
    @staticmethod
    def clean_logs() -> str:
        """Clean old log files"""
        return "sudo -n find /var/log -type f -name '*.log' -mtime +30 -delete"

    @staticmethod
    def clean_full_system() -> str:
        """Run the full system cleanup script (no size limits)."""
        script = r"""#!/bin/bash

# =============================================================================
# SYSTEM CLEANUP SCRIPT - FULL SYSTEM CLEANUP (NO SIZE LIMITS)
# =============================================================================
# A comprehensive system cleanup script that cleans everything for maximum performance
#
# USAGE:
#   sudo ./system_cleanup.sh         # Run with confirmation
#   sudo ./system_cleanup.sh --force # Skip confirmation (use with caution!)
#   sudo ./system_cleanup.sh --help  # Show this help message
#
# REQUIREMENTS:
#   - Must be run with sudo for full system access
#   - Works on Debian/Ubuntu, Arch, Fedora, and most Linux distros
# =============================================================================

# =============================================================================
# CONFIGURATION - Edit these variables as needed
# =============================================================================

# NO SIZE LIMITS - Commented out to allow cleaning of all files regardless of size
# MAX_FILE_SIZE=104857600  # REMOVED - No size limits!

# Log files older than this many days will be considered for cleanup
LOG_FILE_AGE=30

# Cache files older than this many days will be considered for cleanup
CACHE_FILE_AGE=7

# Temp files older than this many days will be considered for cleanup
TEMP_FILE_AGE=1

# Minimum file size to consider for duplicate detection (in bytes)
MIN_DUPLICATE_SIZE=1024  # Keep this to avoid hashing tiny files

# Colors for terminal output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
PURPLE='\033[0;35m'
CYAN='\033[0;36m'
NC='\033[0m' # No Color
BOLD='\033[1m'

# =============================================================================
# GLOBAL VARIABLES - Do not edit below this line
# =============================================================================

SCRIPT_NAME=$(basename "$0")
SCRIPT_DIR=$(dirname "$(readlink -f "$0")")
LOG_FILE="$SCRIPT_DIR/cleanup_log_$(date '+%Y%m%d_%H%M%S').txt"
REPORT_FILE="$SCRIPT_DIR/cleanup_report_$(date '+%Y%m%d_%H%M%S').txt"
TEMP_DIR="/tmp/system_cleanup_$$"

# Statistics
declare -A CATEGORY_COUNTS
declare -A CATEGORY_SIZES
TOTAL_FILES=0
TOTAL_BYTES=0
SKIPPED_FILES=0
ERRORS=0

# Skip patterns (don't delete these even if they match)
SKIP_PATTERNS=(
    "*.conf"
    "*.config"
    "*.cfg"
    "*.ini"
    "*.db"
    "*.sqlite"
    "*.sqlite3"
    "*.lock"
    "*.pid"
    "*.socket"
)

# Critical system directories - NEVER touch these
CRITICAL_DIRS=(
    "/bin"
    "/boot"
    "/dev"
    "/etc"
    "/lib"
    "/lib64"
    "/opt"
    "/proc"
    "/sbin"
    "/sys"
    "/usr/bin"
    "/usr/include"
    "/usr/lib"
    "/usr/lib64"
    "/usr/sbin"
    "/usr/share"
    "/var/lib/dpkg"
    "/var/lib/rpm"
    "/var/lib/pacman"
    "/var/lib/apt/lists/partial"
)

# File patterns considered as junk
JUNK_PATTERNS=(
    "*.tmp"
    "*.temp"
    "*.TMP"
    "*~"
    "*.bak"
    "*.backup"
    "*.old"
    "*.orig"
    "*.swp"
    "*.swo"
    "*.swn"
    "*.pyc"
    "*.pyo"
    "__pycache__"
    "*.class"
    "*.o"
    "*.obj"
    "*.exe~"
    "*.dll~"
    "*.so~"
    "*.dylib~"
    "Thumbs.db"
    ".DS_Store"
    "Desktop.ini"
    "*.part"
    "*.crdownload"
    "*.download"
    "*.aria2"
    "*.torrent"
    "*.nfo"
    "*.diz"
    "*.core"
    "*.dmp"
    "*.crash"
    "*.stackdump"
)

# Cache directories patterns
CACHE_PATTERNS=(
    ".cache"
    ".npm/_cacache"
    ".cargo/registry/cache"
    ".gradle/caches"
    ".m2/repository"
    ".ivy2/cache"
    ".sbt"
    ".stack/work"
    ".cabal/packages"
    "snap/*/*/.cache"
    ".mozilla/firefox/*/cache2"
    ".mozilla/firefox/*/thumbnails"
    ".config/google-chrome/*/Cache"
    ".config/google-chrome/*/Code Cache"
    ".config/chromium/*/Cache"
    ".config/chromium/*/Code Cache"
    ".config/BraveSoftware/*/Cache"
    ".config/BraveSoftware/*/Code Cache"
    ".config/microsoft-edge/*/Cache"
    ".config/microsoft-edge/*/Code Cache"
    ".config/Code/CachedData"
    ".config/Code/CachedExtensions"
    ".config/Code/User/workspaceStorage"
    ".config/Slack/Cache"
    ".config/discord/Cache"
    ".config/spotify/Data"
    ".config/spotify/Browser/Cache"
)

# Package manager cache directories
PKG_CACHE_DIRS=(
    "/var/cache/apt/archives"      # Debian/Ubuntu
    "/var/cache/dnf"                # Fedora
    "/var/cache/yum"                # RHEL/CentOS
    "/var/cache/pacman/pkg"         # Arch
    "/var/cache/zypp/packages"      # openSUSE
    "/var/cache/snapd"              # Snap
    "/var/lib/flatpak/repo/tmp"     # Flatpak
)

# =============================================================================
# FUNCTIONS
# =============================================================================

# -----------------------------------------------------------------------------
# Display help information
# -----------------------------------------------------------------------------
show_help() {
    cat << EOF
${BOLD}SYSTEM CLEANUP SCRIPT - FULL SYSTEM CLEANUP${NC}

A comprehensive system cleanup script that cleans EVERYTHING for maximum performance.
NO FILE SIZE LIMITS - Cleans files of any size!

${BOLD}USAGE:${NC}
  sudo $SCRIPT_NAME              # Run with confirmation
  sudo $SCRIPT_NAME --force      # Skip confirmation (use with caution!)
  sudo $SCRIPT_NAME --help       # Show this help message

${BOLD}OPTIONS:${NC}
  --force    Skip confirmation prompt (automated cleanup)
  --help     Show this help message

${BOLD}CONFIGURATION:${NC}
  Edit the variables at the top of the script to customize:
  - LOG_FILE_AGE: Age of log files to consider (default: 30 days)
  - CACHE_FILE_AGE: Age of cache files to consider (default: 7 days)
  - TEMP_FILE_AGE: Age of temp files to consider (default: 1 day)

${BOLD}SAFEGUARDS:${NC}
  - Critical system directories are NEVER touched
  - Critical file patterns (*.conf, *.db, etc.) are preserved
  - Confirmation required before deletion (unless --force is used)
  - All deletions are logged to: $LOG_FILE

${BOLD}REQUIREMENTS:${NC}
  - Must be run with sudo for full system access
  - Dependencies: find, du, sort, awk, sha256sum, bc

${BOLD}EXAMPLES:${NC}
  sudo ./$SCRIPT_NAME              # Interactive mode with confirmation
  sudo ./$SCRIPT_NAME --force      # Automated mode (no confirmation)
EOF
}

# -----------------------------------------------------------------------------
# Initialize the script environment
# -----------------------------------------------------------------------------
init_environment() {
    # Create temp directory
    mkdir -p "$TEMP_DIR"
   
    # Initialize log file
    {
        echo "================================================================================"
        echo "SYSTEM CLEANUP LOG - FULL SYSTEM CLEANUP (NO SIZE LIMITS)"
        echo "================================================================================"
        echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Hostname: $(hostname)"
        echo "User: $USER"
        echo "Mode: $MODE"
        echo "================================================================================"
        echo ""
    } > "$LOG_FILE"
   
    # Initialize report file
    {
        echo "================================================================================"
        echo "SYSTEM CLEANUP REPORT - FULL SYSTEM CLEANUP (NO SIZE LIMITS)"
        echo "================================================================================"
        echo "Date: $(date '+%Y-%m-%d %H:%M:%S')"
        echo "Hostname: $(hostname)"
        echo "Mode: $MODE"
        echo ""
    } > "$REPORT_FILE"
   
    # Print header
    echo -e "${CYAN}${BOLD}"
    echo "================================================================================"
    echo "           SYSTEM CLEANUP SCRIPT - FULL SYSTEM CLEANUP (NO SIZE LIMITS)"
    echo "================================================================================"
    echo -e "${NC}"
    echo -e "${YELLOW}Mode:${NC} $MODE"
    echo -e "${YELLOW}Date:${NC} $(date '+%Y-%m-%d %H:%M:%S')"
    echo -e "${YELLOW}System:${NC} $(hostname) ($(uname -o))"
    echo -e "${YELLOW}Note:${NC} ${RED}No file size limits - cleaning ALL files regardless of size!${NC}"
    echo ""
}

# (script continues...)"""

        # If the stored cleanup script file exists, prefer using it (easier to maintain).
        cleanup_script_path = Path(__file__).resolve().parent / "scripts" / "system_cleanup.sh"
        if cleanup_script_path.exists():
            try:
                script = cleanup_script_path.read_text()
            except Exception:
                script = script  # fallback to embedded version if read fails

        # Use a unique heredoc delimiter so the embedded script's own "EOF" blocks don't terminate it early.
        return (
            "cat > /tmp/system_cleanup.sh <<'SCRIPT_EOF'\n"
            + script
            + "\nSCRIPT_EOF\n"
            + "chmod +x /tmp/system_cleanup.sh && sudo -n /tmp/system_cleanup.sh --force"
        )

    @staticmethod
    def get_running_processes() -> str:
        """Get list of running processes"""
        return "ps aux"

    @staticmethod
    def check_connectivity(target_host: str) -> str:
        """Check connectivity to a host"""
        return f"ping -c 4 {target_host}"
    
    @staticmethod
    def check_connectivity(target_host: str) -> str:
        """Check connectivity to a host"""
        return f"ping -c 4 {target_host}"
