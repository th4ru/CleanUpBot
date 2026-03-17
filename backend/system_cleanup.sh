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
# Check for required dependencies
# -----------------------------------------------------------------------------
check_dependencies() {
    local deps=("find" "du" "sort" "awk" "sha256sum" "bc")
    local missing=()
   
    for dep in "${deps[@]}"; do
        if ! command -v "$dep" &> /dev/null; then
            missing+=("$dep")
        fi
    done
   
    if [[ ${#missing[@]} -gt 0 ]]; then
        echo -e "${RED}Error: Missing dependencies: ${missing[*]}${NC}"
        echo "Please install missing dependencies and try again."
        exit 1
    fi
}

# -----------------------------------------------------------------------------
# Check if a path is in critical directories
# -----------------------------------------------------------------------------
is_critical_path() {
    local path="$1"
    for critical in "${CRITICAL_DIRS[@]}"; do
        if [[ "$path" == "$critical"* ]] || [[ "$path" == "$critical" ]]; then
            return 0
        fi
    done
    return 1
}

# -----------------------------------------------------------------------------
# Check if file matches skip patterns
# -----------------------------------------------------------------------------
should_skip() {
    local file="$1"
    for pattern in "${SKIP_PATTERNS[@]}"; do
        if [[ "$file" == $pattern ]]; then
            return 0
        fi
    done
    return 1
}

# -----------------------------------------------------------------------------
# Format file size in human-readable format
# -----------------------------------------------------------------------------
format_size() {
    local bytes=$1
    if [[ $bytes -lt 1024 ]]; then
        echo "${bytes}B"
    elif [[ $bytes -lt 1048576 ]]; then
        echo "$(echo "scale=2; $bytes/1024" | bc)KB"
    elif [[ $bytes -lt 1073741824 ]]; then
        echo "$(echo "scale=2; $bytes/1048576" | bc)MB"
    elif [[ $bytes -lt 1099511627776 ]]; then
        echo "$(echo "scale=2; $bytes/1073741824" | bc)GB"
    else
        echo "$(echo "scale=2; $bytes/1099511627776" | bc)TB"
    fi
}

# -----------------------------------------------------------------------------
# Log and delete a file
# -----------------------------------------------------------------------------
delete_file() {
    local file="$1"
    local category="$2"
   
    # Skip if file doesn't exist
    [[ ! -e "$file" ]] && return
   
    # Get file size
    local size=0
    if [[ -f "$file" ]]; then
        size=$(stat -c%s "$file" 2>/dev/null)
    fi
   
    # NO SIZE LIMIT CHECK - We clean files of ANY size!
    # The old size limit check has been removed completely
   
    # Skip if matches skip patterns
    if should_skip "$file"; then
        echo -e "  ${PURPLE}[SKIPPED]${NC} Protected pattern: $file"
        SKIPPED_FILES=$((SKIPPED_FILES + 1))
        echo "$(date '+%Y-%m-%d %H:%M:%S') [SKIPPED-PATTERN] $file" >> "$LOG_FILE"
        return
    fi
   
    echo -e "  ${RED}[DELETING]${NC} $file (${CYAN}$(format_size $size)${NC})"
   
    # Attempt deletion
    if rm -rf "$file" 2>/dev/null; then
        echo "$(date '+%Y-%m-%d %H:%M:%S') DELETED: $file (Size: $(format_size $size), Category: $category)" >> "$LOG_FILE"
        echo "$(date '+%Y-%m-%d %H:%M:%S') [$category] $file ($(format_size $size))" >> "$REPORT_FILE"
       
        # Update counters
        CATEGORY_COUNTS[$category]=$((CATEGORY_COUNTS[$category] + 1))
        CATEGORY_SIZES[$category]=$((CATEGORY_SIZES[$category] + size))
        TOTAL_FILES=$((TOTAL_FILES + 1))
        TOTAL_BYTES=$((TOTAL_BYTES + size))
    else
        echo -e "  ${RED}[ERROR]${NC} Failed to delete: $file"
        ERRORS=$((ERRORS + 1))
        echo "$(date '+%Y-%m-%d %H:%M:%S') [ERROR] Failed to delete: $file" >> "$LOG_FILE"
    fi
}

# -----------------------------------------------------------------------------
# Remove directory if empty
# -----------------------------------------------------------------------------
remove_empty_dir() {
    local dir="$1"
   
    if [[ -d "$dir" ]] && [[ -z "$(ls -A "$dir" 2>/dev/null)" ]]; then
        echo -e "  ${YELLOW}[REMOVING]${NC} Empty directory: $dir"
        if rmdir "$dir" 2>/dev/null; then
            echo "$(date '+%Y-%m-%d %H:%M:%S') REMOVED empty directory: $dir" >> "$LOG_FILE"
        fi
    fi
}

# -----------------------------------------------------------------------------
# Scan for temporary files
# -----------------------------------------------------------------------------
scan_temp_files() {
    echo -e "\n${BOLD}${BLUE}[1/8] Cleaning temporary files (ANY SIZE)...${NC}"
    local count=0
   
    local temp_dirs=("/tmp" "/var/tmp" "/dev/shm" "/var/lock" "/var/run/lock")
   
    for dir in "${temp_dirs[@]}"; do
        if [[ -d "$dir" ]] && ! is_critical_path "$dir"; then
            while IFS= read -r file; do
                delete_file "$file" "temp_files"
                count=$((count + 1))
            done < <(find "$dir" -type f -atime +$TEMP_FILE_AGE -o -type f -mtime +$TEMP_FILE_AGE 2>/dev/null)
        fi
    done
   
    if [[ $count -gt 0 ]]; then
        echo -e "  ${GREEN}Cleaned $count temporary files${NC}"
    fi
}

# -----------------------------------------------------------------------------
# Scan for cache files
# -----------------------------------------------------------------------------
scan_cache_files() {
    echo -e "\n${BOLD}${BLUE}[2/8] Cleaning cache files (ANY SIZE)...${NC}"
    local count=0
   
    # System cache directories
    for dir in "${PKG_CACHE_DIRS[@]}"; do
        if [[ -d "$dir" ]] && ! is_critical_path "$dir"; then
            while IFS= read -r file; do
                delete_file "$file" "package_cache"
                count=$((count + 1))
            done < <(find "$dir" -type f -mtime +$CACHE_FILE_AGE 2>/dev/null)
        fi
    done
   
    # User cache directories
    for user_home in /home/* /root; do
        if [[ -d "$user_home" ]]; then
            for pattern in "${CACHE_PATTERNS[@]}"; do
                while IFS= read -r file; do
                    delete_file "$file" "user_cache"
                    count=$((count + 1))
                done < <(find "$user_home" -path "*/$pattern" -type f -mtime +$CACHE_FILE_AGE 2>/dev/null)
            done
        fi
    done
   
    # System cache directories
    while IFS= read -r file; do
        if ! is_critical_path "$file"; then
            delete_file "$file" "system_cache"
            count=$((count + 1))
        fi
    done < <(find /var/cache -type f -mtime +$CACHE_FILE_AGE 2>/dev/null)
   
    if [[ $count -gt 0 ]]; then
        echo -e "  ${GREEN}Cleaned $count cache files${NC}"
    fi
}

# -----------------------------------------------------------------------------
# Scan for log files
# -----------------------------------------------------------------------------
scan_log_files() {
    echo -e "\n${BOLD}${BLUE}[3/8] Cleaning log files (ANY SIZE)...${NC}"
    local count=0
   
    while IFS= read -r file; do
        if ! is_critical_path "$file"; then
            delete_file "$file" "log_files"
            count=$((count + 1))
        fi
    done < <(find /var/log -type f -name "*.log" -mtime +$LOG_FILE_AGE 2>/dev/null)
   
    # Compressed logs
    while IFS= read -r file; do
        if ! is_critical_path "$file"; then
            delete_file "$file" "compressed_logs"
            count=$((count + 1))
        fi
    done < <(find /var/log -type f \( -name "*.gz" -o -name "*.bz2" -o -name "*.xz" -o -name "*.old" \) -mtime +$LOG_FILE_AGE 2>/dev/null)
   
    # User logs
    for user_home in /home/*; do
        if [[ -d "$user_home" ]]; then
            while IFS= read -r file; do
                delete_file "$file" "user_history"
                count=$((count + 1))
            done < <(find "$user_home" -name ".bash_history" -o -name ".zsh_history" -o -name ".python_history" -mtime +$LOG_FILE_AGE 2>/dev/null)
        fi
    done
   
    if [[ $count -gt 0 ]]; then
        echo -e "  ${GREEN}Cleaned $count log files${NC}"
    fi
}

# -----------------------------------------------------------------------------
# Scan for junk files
# -----------------------------------------------------------------------------
scan_junk_files() {
    echo -e "\n${BOLD}${BLUE}[4/8] Cleaning junk files (ANY SIZE)...${NC}"
    local count=0
   
    for user_home in /home/* /root; do
        if [[ -d "$user_home" ]]; then
            for pattern in "${JUNK_PATTERNS[@]}"; do
                while IFS= read -r file; do
                    if ! is_critical_path "$file"; then
                        delete_file "$file" "junk_files"
                        count=$((count + 1))
                    fi
                done < <(find "$user_home" -name "$pattern" -type f -mtime +1 2>/dev/null)
            done
        fi
    done
   
    if [[ $count -gt 0 ]]; then
        echo -e "  ${GREEN}Cleaned $count junk files${NC}"
    fi
}

# -----------------------------------------------------------------------------
# Scan trash directories
# -----------------------------------------------------------------------------
scan_trash() {
    echo -e "\n${BOLD}${BLUE}[5/8] Cleaning trash directories (ANY SIZE)...${NC}"
    local count=0
   
    for user_home in /home/* /root; do
        if [[ -d "$user_home" ]]; then
            while IFS= read -r trashdir; do
                if [[ -d "$trashdir" ]]; then
                    while IFS= read -r file; do
                        delete_file "$file" "trash"
                        count=$((count + 1))
                    done < <(find "$trashdir" -type f 2>/dev/null)
                   
                    # Try to remove empty trash directories
                    remove_empty_dir "$trashdir"
                    remove_empty_dir "$(dirname "$trashdir" 2>/dev/null)"
                fi
            done < <(find "$user_home" -path "*/.Trash*" -o -path "*/Trash" -o -path "*/.local/share/Trash" 2>/dev/null)
        fi
    done
   
    if [[ $count -gt 0 ]]; then
        echo -e "  ${GREEN}Cleaned $count files from trash${NC}"
    fi
}

# -----------------------------------------------------------------------------
# Scan for broken symlinks
# -----------------------------------------------------------------------------
scan_broken_symlinks() {
    echo -e "\n${BOLD}${BLUE}[6/8] Cleaning broken symlinks...${NC}"
    local count=0
   
    for dir in / /home; do
        if [[ -d "$dir" ]]; then
            while IFS= read -r link; do
                if ! is_critical_path "$link"; then
                    echo -e "  ${RED}[DELETING]${NC} Broken symlink: $link"
                   
                    if rm -f "$link" 2>/dev/null; then
                        echo "$(date '+%Y-%m-%d %H:%M:%S') DELETED broken symlink: $link" >> "$LOG_FILE"
                        echo "$(date '+%Y-%m-%d %H:%M:%S') [broken_symlink] $link" >> "$REPORT_FILE"
                       
                        CATEGORY_COUNTS["broken_symlinks"]=$((CATEGORY_COUNTS["broken_symlinks"] + 1))
                        TOTAL_FILES=$((TOTAL_FILES + 1))
                        count=$((count + 1))
                    else
                        echo -e "  ${RED}[ERROR]${NC} Failed to delete broken symlink: $link"
                        ERRORS=$((ERRORS + 1))
                    fi
                fi
            done < <(find "$dir" -xtype l 2>/dev/null)
        fi
    done
   
    if [[ $count -gt 0 ]]; then
        echo -e "  ${GREEN}Cleaned $count broken symlinks${NC}"
    fi
}

# -----------------------------------------------------------------------------
# Scan for duplicate files
# -----------------------------------------------------------------------------
scan_duplicates() {
    echo -e "\n${BOLD}${BLUE}[7/8] Cleaning duplicate files (ANY SIZE)...${NC}"
    echo -e "${YELLOW}Note: This may take a while on large systems${NC}"
   
    local temp_files="$TEMP_DIR/all_files.txt"
    local count=0
   
    # Find all regular files larger than MIN_DUPLICATE_SIZE
    # NO UPPER SIZE LIMIT - cleaning duplicates of ANY size!
    find /home /usr/local -type f -size +${MIN_DUPLICATE_SIZE}c 2>/dev/null | while read -r file; do
        if ! is_critical_path "$file" && ! should_skip "$file"; then
            local hash=$(sha256sum "$file" 2>/dev/null | awk '{print $1}')
            if [[ -n "$hash" ]]; then
                echo "$hash:$file" >> "$temp_files"
            fi
        fi
    done
   
    # Find duplicates
    if [[ -f "$temp_files" ]]; then
        sort "$temp_files" | cut -d: -f1 | uniq -d | while read -r duplicate_hash; do
            # Get all files with this hash, skip the first one (keep it)
            local first=true
            grep "^$duplicate_hash:" "$temp_files" | while IFS=: read -r hash file; do
                if $first; then
                    first=false
                else
                    delete_file "$file" "duplicates"
                    count=$((count + 1))
                fi
            done
        done
        rm -f "$temp_files"
    fi
   
    if [[ $count -gt 0 ]]; then
        echo -e "  ${GREEN}Cleaned $count duplicate files${NC}"
    fi
}

# -----------------------------------------------------------------------------
# Clean package manager caches
# -----------------------------------------------------------------------------
clean_package_caches() {
    echo -e "\n${BOLD}${BLUE}[8/8] Cleaning package manager caches...${NC}"
   
    # APT (Debian/Ubuntu)
    if command -v apt-get &>/dev/null; then
        echo -e "  ${CYAN}APT:${NC} Cleaning package cache..."
        apt-get clean
        apt-get autoremove -y
        echo "$(date '+%Y-%m-%d %H:%M:%S') Ran: apt-get clean && apt-get autoremove" >> "$LOG_FILE"
    fi
   
    # DNF (Fedora)
    if command -v dnf &>/dev/null; then
        echo -e "  ${CYAN}DNF:${NC} Cleaning package cache..."
        dnf clean all
        dnf autoremove -y
        echo "$(date '+%Y-%m-%d %H:%M:%S') Ran: dnf clean all && dnf autoremove" >> "$LOG_FILE"
    fi
   
    # YUM (RHEL/CentOS)
    if command -v yum &>/dev/null; then
        echo -e "  ${CYAN}YUM:${NC} Cleaning package cache..."
        yum clean all
        yum autoremove -y
        echo "$(date '+%Y-%m-%d %H:%M:%S') Ran: yum clean all && yum autoremove" >> "$LOG_FILE"
    fi
   
    # Pacman (Arch)
    if command -v pacman &>/dev/null; then
        echo -e "  ${CYAN}Pacman:${NC} Cleaning package cache..."
        pacman -Sc --noconfirm
        pacman -Rns $(pacman -Qdtq) --noconfirm 2>/dev/null
        echo "$(date '+%Y-%m-%d %H:%M:%S') Ran: pacman -Sc && removed orphans" >> "$LOG_FILE"
    fi
   
    # Snap
    if command -v snap &>/dev/null; then
        echo -e "  ${CYAN}Snap:${NC} Removing disabled revisions..."
        snap list --all 2>/dev/null | awk '/disabled/{print $1, $3}' | while read -r name rev; do
            echo -e "    Removing disabled snap: $name (revision $rev)"
            snap remove "$name" --revision="$rev" 2>/dev/null
            echo "$(date '+%Y-%m-%d %H:%M:%S') Removed disabled snap: $name (revision $rev)" >> "$LOG_FILE"
        done
    fi
   
    # Flatpak
    if command -v flatpak &>/dev/null; then
        echo -e "  ${CYAN}Flatpak:${NC} Removing unused runtimes..."
        flatpak uninstall --unused --noninteractive
        echo "$(date '+%Y-%m-%d %H:%M:%S') Ran: flatpak uninstall --unused" >> "$LOG_FILE"
    fi
   
    # Docker
    if command -v docker &>/dev/null; then
        echo -e "  ${CYAN}Docker:${NC} Cleaning up..."
       
        # Remove stopped containers
        echo -e "    Removing stopped containers..."
        docker container prune -f
        echo "$(date '+%Y-%m-%d %H:%M:%S') Ran: docker container prune" >> "$LOG_FILE"
       
        # Remove dangling images
        echo -e "    Removing dangling images..."
        docker image prune -a -f
        echo "$(date '+%Y-%m-%d %H:%M:%S') Ran: docker image prune -a" >> "$LOG_FILE"
       
        # Remove unused volumes
        echo -e "    Removing unused volumes..."
        docker volume prune -f
        echo "$(date '+%Y-%m-%d %H:%M:%S') Ran: docker volume prune" >> "$LOG_FILE"
       
        # Remove build cache
        echo -e "    Removing build cache..."
        docker builder prune -a -f
        echo "$(date '+%Y-%m-%d %H:%M:%S') Ran: docker builder prune -a" >> "$LOG_FILE"
       
        # Remove all unused objects
        echo -e "    Removing all unused Docker objects..."
        docker system prune -a -f --volumes
        echo "$(date '+%Y-%m-%d %H:%M:%S') Ran: docker system prune -a" >> "$LOG_FILE"
    fi
   
    # Journal logs
    if command -v journalctl &>/dev/null; then
        echo -e "  ${CYAN}Journal:${NC} Cleaning systemd journals..."
        journalctl --vacuum-time=3d
        echo "$(date '+%Y-%m-%d %H:%M:%S') Ran: journalctl --vacuum-time=3d" >> "$LOG_FILE"
    fi
   
    # Thumbnail cache
    echo -e "  ${CYAN}Thumbnails:${NC} Cleaning thumbnail cache..."
    rm -rf ~/.cache/thumbnails/* 2>/dev/null
    for user_home in /home/*; do
        if [[ -d "$user_home/.cache/thumbnails" ]]; then
            rm -rf "$user_home/.cache/thumbnails/"* 2>/dev/null
        fi
    done
}

# -----------------------------------------------------------------------------
# Display summary of cleanup
# -----------------------------------------------------------------------------
display_summary() {
    echo -e "\n${GREEN}${BOLD}"
    echo "================================================================================"
    echo "                          CLEANUP COMPLETE"
    echo "================================================================================"
    echo -e "${NC}"
   
    if [[ $TOTAL_FILES -eq 0 && $SKIPPED_FILES -eq 0 && $ERRORS -eq 0 ]]; then
        echo -e "${YELLOW}No files were cleaned.${NC}"
    else
        echo -e "${BOLD}Results:${NC}"
        echo -e "  ${GREEN}Files deleted:${NC}     $TOTAL_FILES"
        echo -e "  ${GREEN}Space freed:${NC}      $(format_size $TOTAL_BYTES)"
        echo -e "  ${YELLOW}Files skipped:${NC}    $SKIPPED_FILES"
       
        if [[ $ERRORS -gt 0 ]]; then
            echo -e "  ${RED}Errors:${NC}          $ERRORS"
        fi
       
        echo ""
        echo -e "${BOLD}Breakdown by category:${NC}"
       
        # Create temporary file for sorting
        local temp_sort="$TEMP_DIR/sort.txt"
       
        # Write categories to temp file for sorting
        for cat in "${!CATEGORY_COUNTS[@]}"; do
            if [[ ${CATEGORY_COUNTS[$cat]} -gt 0 ]]; then
                echo "${CATEGORY_SIZES[$cat]}:$cat:${CATEGORY_COUNTS[$cat]}" >> "$temp_sort"
            fi
        done
       
        # Sort and display
        if [[ -f "$temp_sort" ]]; then
            sort -rn "$temp_sort" | while IFS=: read -r size cat count; do
                # Format the category name nicely
                case "$cat" in
                    "broken_symlinks") display_cat="Broken Symlinks" ;;
                    "duplicates") display_cat="Duplicate Files" ;;
                    "temp_files") display_cat="Temp Files" ;;
                    "user_cache") display_cat="User Cache" ;;
                    "system_cache") display_cat="System Cache" ;;
                    "package_cache") display_cat="Package Cache" ;;
                    "log_files") display_cat="Log Files" ;;
                    "compressed_logs") display_cat="Compressed Logs" ;;
                    "user_history") display_cat="User History" ;;
                    "junk_files") display_cat="Junk Files" ;;
                    "trash") display_cat="Trash" ;;
                    *) display_cat="$cat" ;;
                esac
                printf "  ${CYAN}%-20s${NC} %8d items  ${YELLOW}%10s${NC}\n" "$display_cat:" "$count" "$(format_size $size)"
            done
            rm -f "$temp_sort"
        fi
    fi
   
    # Write summary to report
    {
        echo ""
        echo "================================================================================"
        echo "SUMMARY"
        echo "================================================================================"
        echo "Files deleted: $TOTAL_FILES"
        echo "Space freed: $(format_size $TOTAL_BYTES) ($TOTAL_BYTES bytes)"
        echo "Files skipped: $SKIPPED_FILES"
        echo "Errors: $ERRORS"
        echo ""
        echo "Breakdown by category:"
        for cat in "${!CATEGORY_COUNTS[@]}"; do
            if [[ ${CATEGORY_COUNTS[$cat]} -gt 0 ]]; then
                echo "  $cat: ${CATEGORY_COUNTS[$cat]} items ($(format_size ${CATEGORY_SIZES[$cat]}))"
            fi
        done
    } >> "$REPORT_FILE"
}

# -----------------------------------------------------------------------------
# Ask for confirmation before cleaning
# -----------------------------------------------------------------------------
confirm_clean() {
    if [[ $MODE == "interactive" ]]; then
        echo -e "\n${RED}${BOLD}⚠️  WARNING: This will permanently delete files from your system${NC}"
        echo -e "${RED}${BOLD}⚠️  NO SIZE LIMITS - Files of ANY size will be deleted!${NC}"
        echo -e "${YELLOW}All deletions will be logged to: $LOG_FILE${NC}"
        echo ""
        read -p "Are you sure you want to proceed? (Type 'yes' to confirm): " confirmation
       
        if [[ "$confirmation" != "yes" ]]; then
            echo -e "${GREEN}Cleanup cancelled.${NC}"
            exit 0
        fi
       
        echo -e "${YELLOW}Starting cleanup...${NC}\n"
    fi
}

# -----------------------------------------------------------------------------
# Cleanup temporary files
# -----------------------------------------------------------------------------
cleanup() {
    rm -rf "$TEMP_DIR" 2>/dev/null
   
    echo -e "\n${GREEN}Cleanup completed!${NC}"
    echo -e "${GREEN}Report saved to: $REPORT_FILE${NC}"
    echo -e "${GREEN}Log saved to: $LOG_FILE${NC}"
   
    if [[ $ERRORS -gt 0 ]]; then
        echo "There were some errors during cleanup. Check the log file for details."
    fi
}

# =============================================================================
# MAIN SCRIPT EXECUTION
# =============================================================================

# Parse arguments
MODE="interactive"
if [[ "$1" == "--force" ]]; then
    MODE="automated"
elif [[ "$1" == "--help" || "$1" == "-h" ]]; then
    show_help
    exit 0
fi

# Set up trap for cleanup on exit
trap cleanup EXIT

# Run pre-checks
check_privileges
check_dependencies
init_environment
confirm_clean

# Run cleanup tasks
scan_temp_files
scan_cache_files
scan_log_files
scan_junk_files
scan_trash
scan_broken_symlinks
scan_duplicates
clean_package_caches

# Display results
display_summary
