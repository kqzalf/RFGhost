"""RF signal logging module.

This module provides functionality for logging RF signal data and anomalies
with features like file rotation and compression.
"""

import logging
import json
import os
import gzip
from datetime import datetime
from typing import Dict, List, Optional, Any

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RFGhost')

class RFLogger:
    """Logger for RF signal data and anomalies."""
    
    def __init__(self, log_dir: str = "logs", max_size: int = 10 * 1024 * 1024):
        """Initialize the RF logger.
        
        Args:
            log_dir: Directory for log files
            max_size: Maximum log file size in bytes
        """
        self.log_dir = log_dir
        self.max_size = max_size
        self.current_log = os.path.join(log_dir, "current.log")
        self._ensure_log_dir()
        
    def _ensure_log_dir(self) -> None:
        """Ensure log directory exists."""
        try:
            os.makedirs(self.log_dir, exist_ok=True)
        except (IOError, OSError) as e:
            logger.error("Failed to create log directory: %s", str(e))
            raise
            
    def _compress_old_log(self, log_file: str) -> None:
        """Compress old log file.
        
        Args:
            log_file: Path to log file
        """
        try:
            if not os.path.exists(log_file):
                return
                
            # Create compressed filename
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            compressed_file = f"{log_file}.{timestamp}.gz"
            
            # Compress file
            with open(log_file, 'rb') as f_in:
                with gzip.open(compressed_file, 'wb') as f_out:
                    f_out.writelines(f_in)
                    
            # Remove original file
            os.remove(log_file)
            
        except (IOError, OSError) as e:
            logger.error("Failed to compress log file: %s", str(e))
            
    def _cleanup_old_files(self) -> None:
        """Clean up old log files."""
        try:
            # List all files in log directory
            files = os.listdir(self.log_dir)
            
            # Sort by modification time
            files.sort(key=lambda x: os.path.getmtime(os.path.join(self.log_dir, x)))
            
            # Keep only last 10 files
            for file in files[:-10]:
                try:
                    os.remove(os.path.join(self.log_dir, file))
                except (IOError, OSError) as e:
                    logger.error("Failed to remove old log file: %s", str(e))
                    
        except (IOError, OSError) as e:
            logger.error("Failed to cleanup old files: %s", str(e))
            
    def log_signal(self, signal_data: Dict[str, Any]) -> None:
        """Log RF signal data.
        
        Args:
            signal_data: Signal data to log
        """
        try:
            # Add timestamp
            signal_data["timestamp"] = datetime.now().isoformat()
            
            # Convert to JSON
            log_entry = json.dumps(signal_data) + "\n"
            
            # Check file size
            if os.path.exists(self.current_log):
                if os.path.getsize(self.current_log) > self.max_size:
                    self._compress_old_log(self.current_log)
                    
            # Write to log file
            with open(self.current_log, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
            # Cleanup old files
            self._cleanup_old_files()
            
        except (IOError, OSError, json.JSONDecodeError) as e:
            logger.error("Failed to log signal data: %s", str(e))
            
    def log_anomaly(self, anomaly_data: Dict[str, Any]) -> None:
        """Log RF anomaly data.
        
        Args:
            anomaly_data: Anomaly data to log
        """
        try:
            # Add timestamp
            anomaly_data["timestamp"] = datetime.now().isoformat()
            
            # Convert to JSON
            log_entry = json.dumps(anomaly_data) + "\n"
            
            # Check file size
            if os.path.exists(self.current_log):
                if os.path.getsize(self.current_log) > self.max_size:
                    self._compress_old_log(self.current_log)
                    
            # Write to log file
            with open(self.current_log, 'a', encoding='utf-8') as f:
                f.write(log_entry)
                
            # Cleanup old files
            self._cleanup_old_files()
            
        except (IOError, OSError, json.JSONDecodeError) as e:
            logger.error("Failed to log anomaly data: %s", str(e))
            
    def get_recent_logs(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries.
        
        Args:
            count: Number of entries to retrieve
            
        Returns:
            List of recent log entries
        """
        try:
            if not os.path.exists(self.current_log):
                return []
                
            # Read last n lines
            with open(self.current_log, 'r', encoding='utf-8') as f:
                lines = f.readlines()[-count:]
                
            # Parse JSON entries
            entries = []
            for line in lines:
                try:
                    entry = json.loads(line.strip())
                    entries.append(entry)
                except json.JSONDecodeError:
                    continue
                    
            return entries
            
        except (IOError, OSError) as e:
            logger.error("Failed to read recent logs: %s", str(e))
            return []

def get_rf_logger(log_dir: str = "logs") -> RFLogger:
    """Get or create the global RF logger instance.
    
    Args:
        log_dir: Directory to store log files
        
    Returns:
        RFLogger instance
    """
    global _rf_logger
    if _rf_logger is None:
        _rf_logger = RFLogger(log_dir)
    return _rf_logger

# Global instance
_rf_logger: Optional[RFLogger] = None
