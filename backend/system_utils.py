"""
System utilities - parsing and formatting helpers
"""
import re
from typing import Dict, List, Any, Tuple


class SystemInfoParser:
    """Parse system information from command outputs"""
    
    @staticmethod
    def parse_disk_space(df_output: str) -> List[Dict[str, Any]]:
        """
        Parse 'df -h' output
        
        Example output:
        Filesystem     1K-blocks     Used Available Use% Mounted on
        /dev/sda1      103081248 45235468  57296692  46% /
        
        Returns:
            List of disk info dictionaries
        """
        disks = []
        lines = df_output.strip().split('\n')[1:]  # Skip header
        
        for line in lines:
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) >= 6:
                try:
                    # Try to convert percentages and values
                    usage_percent = float(parts[4].rstrip('%'))
                    disks.append({
                        'filesystem': parts[0],
                        'total': parts[1],
                        'used': parts[2],
                        'available': parts[3],
                        'usage_percent': usage_percent,
                        'mount_point': parts[5]
                    })
                except (ValueError, IndexError):
                    continue
        
        return disks
    
    @staticmethod
    def parse_memory_usage(free_output: str) -> Dict[str, str]:
        """
        Parse 'free -h' output
        
        Example output:
                      total        used        free      shared  buff/cache   available
        Mem:          15.5Gi       8.2Gi       2.1Gi       512Mi       5.2Gi       6.5Gi
        
        Returns:
            Dictionary with memory information
        """
        result = {}
        lines = free_output.strip().split('\n')
        
        for line in lines:
            if 'Mem:' in line:
                parts = line.split()
                if len(parts) >= 6:
                    result = {
                        'total': parts[1],
                        'used': parts[2],
                        'free': parts[3],
                        'shared': parts[4],
                        'buff_cache': parts[5],
                        'available': parts[6] if len(parts) > 6 else parts[5]
                    }
        
        return result
    
    @staticmethod
    def parse_uptime(uptime_output: str) -> Dict[str, Any]:
        """
        Parse 'uptime' output
        
        Example: 10:30:45 up 5 days,  3:45,  2 users,  load average: 0.50, 0.45, 0.40
        
        Returns:
            Dictionary with uptime information
        """
        result = {}
        
        # Extract load average
        load_match = re.search(r'load average: ([\d.]+), ([\d.]+), ([\d.]+)', uptime_output)
        if load_match:
            result['load_1min'] = float(load_match.group(1))
            result['load_5min'] = float(load_match.group(2))
            result['load_15min'] = float(load_match.group(3))
        
        # Extract uptime
        if 'up' in uptime_output:
            # Simple extraction
            up_part = uptime_output.split('up')[1].split('load')[0].strip().rstrip(',')
            result['uptime_string'] = up_part
        
        return result
    
    @staticmethod
    def parse_cpu_usage(top_output: str) -> Dict[str, float]:
        """
        Parse 'top' output for CPU usage
        
        Returns:
            Dictionary with CPU usage percentages
        """
        result = {}
        lines = top_output.strip().split('\n')
        
        for line in lines:
            if 'Cpu(s):' in line:
                # Extract CPU stats
                match = re.search(r'(\d+\.?\d*)\s*us', line)
                if match:
                    result['user'] = float(match.group(1))
                
                match = re.search(r'(\d+\.?\d*)\s*sy', line)
                if match:
                    result['system'] = float(match.group(1))
                
                match = re.search(r'(\d+\.?\d*)\s*id', line)
                if match:
                    result['idle'] = float(match.group(1))
                
                break
        
        return result
    
    @staticmethod
    def convert_bytes_to_human(bytes_value: int, decimal_places: int = 2) -> str:
        """
        Convert bytes to human readable format
        
        Args:
            bytes_value: Size in bytes
            decimal_places: Number of decimal places
            
        Returns:
            Formatted string (e.g., "1.5 GB")
        """
        for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
            if bytes_value < 1024:
                return f"{bytes_value:.{decimal_places}f} {unit}"
            bytes_value /= 1024
        
        return f"{bytes_value:.{decimal_places}f} PB"
    
    @staticmethod
    def convert_human_to_bytes(size_string: str) -> int:
        """
        Convert human readable size to bytes
        
        Args:
            size_string: Size string (e.g., "1.5 GB")
            
        Returns:
            Size in bytes
        """
        units = {'B': 1, 'KB': 1024, 'MB': 1024**2, 'GB': 1024**3, 'TB': 1024**4}
        
        size_string = size_string.strip().upper()
        for unit, multiplier in units.items():
            if unit in size_string:
                return int(float(size_string.replace(unit, '').strip()) * multiplier)
        
        return int(float(size_string))
