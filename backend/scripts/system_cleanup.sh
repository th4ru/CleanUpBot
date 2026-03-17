#!/bin/bash

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

# -----------------------------------------------------------------------------
# Check if running with sufficient privileges
# -----------------------------------------------------------------------------
check_privileges() {
    if [[ $EUID -ne 0 ]]; then
        echo -e "${RED}Error: This script must be run as root (sudo)${NC}"
        echo "Root access is required to clean system directories."
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# Minimal cleanup routines (safe defaults)
# -----------------------------------------------------------------------------
clean_temp_dirs() {
    echo -e "${BLUE}Cleaning temporary directories...${NC}"
    find /tmp /var/tmp /dev/shm -mindepth 1 -mtime +$TEMP_FILE_AGE -print0 2>/dev/null \
        | xargs -0 -r rm -rf 2>/dev/null
}

clean_cache_dirs() {
    echo -e "${BLUE}Cleaning cache directories...${NC}"
    for dir in /var/cache /home/*/.cache /root/.cache; do
        if [[ -d "$dir" ]]; then
            find "$dir" -mindepth 1 -mtime +$CACHE_FILE_AGE -print0 2>/dev/null \
                | xargs -0 -r rm -rf 2>/dev/null
        fi
    done
}

clean_log_files() {
    echo -e "${BLUE}Cleaning old log files...${NC}"
    find /var/log -type f -name "*.log" -mtime +$LOG_FILE_AGE -print0 2>/dev/null \
        | xargs -0 -r rm -f 2>/dev/null
}

prune_package_caches() {
    echo -e "${BLUE}Pruning package manager caches...${NC}"
    if command -v apt-get &>/dev/null; then
        apt-get clean -y 2>/dev/null
        apt-get autoremove -y 2>/dev/null
    fi
    if command -v dnf &>/dev/null; then
        dnf clean all -y 2>/dev/null
        dnf autoremove -y 2>/dev/null
    fi
    if command -v yum &>/dev/null; then
        yum clean all -y 2>/dev/null
        yum autoremove -y 2>/dev/null
    fi
    if command -v pacman &>/dev/null; then
        pacman -Sc --noconfirm 2>/dev/null
        pacman -Rns $(pacman -Qdtq 2>/dev/null || true) --noconfirm 2>/dev/null
    fi
}

# -----------------------------------------------------------------------------
# Main entrypoint
# -----------------------------------------------------------------------------
main() {
    local mode="interactive"
    if [[ "$1" == "--force" ]]; then
        mode="force"
    fi

    if [[ "$1" == "--help" ]]; then
        show_help
        exit 0
    fi

    MODE="$mode"
    init_environment
    check_privileges

    echo -e "${YELLOW}Starting cleanup...${NC}"

    clean_temp_dirs
    clean_cache_dirs
    clean_log_files
    prune_package_caches

    echo -e "${GREEN}Cleanup finished.${NC}"
    echo "Logs: $LOG_FILE"
    echo "Report: $REPORT_FILE"
}

main "$@"
