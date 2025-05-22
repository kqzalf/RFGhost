"""Logging module for RF signal data and anomalies.

This module provides functionality for logging RF signal data and anomalies
to JSONL files with automatic rotation and compression.
"""

import json
import logging
from datetime import datetime
from typing import Dict, Optional, Any, List
from pathlib import Path
import gzip
import shutil
import threading

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RFGhost')

class RFLogger:
    """Logger for RF signal data and anomalies with file rotation and compression."""
    
    def __init__(self, 
                 log_dir: str = "logs",
                 max_file_size_mb: int = 10,
                 max_files: int = 5,
                 compress_old: bool = True):
        """Initialize the RF signal logger.
        
        Args:
            log_dir: Directory to store log files
            max_file_size_mb: Maximum size of each log file in MB
            max_files: Maximum number of log files to keep
            compress_old: Whether to compress old log files
        """
        self.log_dir = Path(log_dir)
        self.max_file_size = max_file_size_mb * 1024 * 1024  # Convert to bytes
        self.max_files = max_files
        self.compress_old = compress_old
        self.current_file = None
        self.current_size = 0
        self._lock = threading.Lock()  # Thread safety
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize current log file
        self._rotate_if_needed()
        
    def _get_current_log_file(self) -> Path:
        """Get the path for the current log file.
        
        Returns:
            Path object for the log file
        """
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.log_dir / f"rfghost_{timestamp}.jsonl"
        
    def _rotate_if_needed(self) -> None:
        """Rotate log files if current file is too large or doesn't exist."""
        with self._lock:
            if (self.current_file is None or 
                not self.current_file.exists() or 
                self.current_size >= self.max_file_size):
                
                # Close current file if it exists
                if self.current_file and self.current_file.exists():
                    self._compress_old_log()
                    
                # Create new log file
                self.current_file = self._get_current_log_file()
                self.current_size = 0
                
                # Clean up old files
                self._cleanup_old_files()
                
    def _compress_old_log(self) -> None:
        """Compress the previous log file if compression is enabled."""
        if not self.compress_old:
            return
            
        try:
            gz_file = self.current_file.with_suffix('.jsonl.gz')
            with open(self.current_file, 'rb') as f_in:
                with gzip.open(gz_file, 'wb') as f_out:
                    shutil.copyfileobj(f_in, f_out)
            self.current_file.unlink()  # Remove original file
        except Exception as e:
            logger.error("Failed to compress log file: %s", str(e))
            
    def _cleanup_old_files(self) -> None:
        """Remove old log files if we have too many."""
        try:
            # Get all log files (including compressed ones)
            log_files = list(self.log_dir.glob("rfghost_*.jsonl*"))
            
            # Sort by modification time (oldest first)
            log_files.sort(key=lambda x: x.stat().st_mtime)
            
            # Remove oldest files if we have too many
            while len(log_files) >= self.max_files:
                oldest = log_files.pop(0)
                oldest.unlink()
        except Exception as e:
            logger.error("Failed to cleanup old log files: %s", str(e))
            
    def log_signal(self, signal_data: Dict[str, Any]) -> bool:
        """Log RF signal data to the current log file.
        
        Args:
            signal_data: Dictionary containing signal data
            
        Returns:
            True if logging successful, False otherwise
        """
        try:
            with self._lock:
                self._rotate_if_needed()
                
                # Add timestamp if not present
                if "timestamp" not in signal_data:
                    signal_data["timestamp"] = datetime.now().isoformat()
                    
                # Convert to JSON and write to file
                json_data = json.dumps(signal_data) + "\n"
                with open(self.current_file, "a", encoding="utf-8") as f:
                    f.write(json_data)
                    
                self.current_size += len(json_data.encode("utf-8"))
                return True
                
        except Exception as e:
            logger.error("Failed to log signal data: %s", str(e))
            return False
            
    def log_anomaly(self, anomaly_data: Dict[str, Any]) -> bool:
        """Log anomaly data to the current log file.
        
        Args:
            anomaly_data: Dictionary containing anomaly data
            
        Returns:
            True if logging successful, False otherwise
        """
        try:
            with self._lock:
                self._rotate_if_needed()
                
                # Add timestamp if not present
                if "timestamp" not in anomaly_data:
                    anomaly_data["timestamp"] = datetime.now().isoformat()
                    
                # Convert to JSON and write to file
                json_data = json.dumps(anomaly_data) + "\n"
                with open(self.current_file, "a", encoding="utf-8") as f:
                    f.write(json_data)
                    
                self.current_size += len(json_data.encode("utf-8"))
                return True
                
        except Exception as e:
            logger.error("Failed to log anomaly data: %s", str(e))
            return False
            
    def get_recent_logs(self, count: int = 100) -> List[Dict[str, Any]]:
        """Get recent log entries from the current log file.
        
        Args:
            count: Number of entries to retrieve
            
        Returns:
            List of log entries as dictionaries
        """
        try:
            if not self.current_file or not self.current_file.exists():
                return []
                
            logs = []
            with open(self.current_file, "r", encoding="utf-8") as f:
                for line in f:
                    try:
                        log_entry = json.loads(line.strip())
                        logs.append(log_entry)
                        if len(logs) >= count:
                            break
                    except json.JSONDecodeError:
                        continue
                        
            return logs
            
        except Exception as e:
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
