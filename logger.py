import json
import logging
import os
import time
from datetime import datetime
from typing import Dict, Optional
from pathlib import Path
import gzip
import shutil

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RFGhost')

class RFLogger:
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
        
        # Create log directory if it doesn't exist
        self.log_dir.mkdir(parents=True, exist_ok=True)
        
        # Initialize current log file
        self._rotate_if_needed()
        
    def _get_current_log_file(self) -> Path:
        """Get the path for the current log file."""
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        return self.log_dir / f"rfghost_{timestamp}.jsonl"
        
    def _rotate_if_needed(self) -> None:
        """Rotate log files if current file is too large or doesn't exist."""
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
            logger.error(f"Failed to compress log file: {e}")
            
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
            logger.error(f"Failed to cleanup old log files: {e}")
            
    def _format_log_entry(self, anomaly: Dict) -> Dict:
        """Format a log entry with additional metadata."""
        return {
            "timestamp": datetime.now().isoformat(),
            "anomaly": anomaly,
            "hostname": os.uname().nodename if hasattr(os, 'uname') else "unknown"
        }
        
    def log_anomaly(self, anomaly: Dict) -> bool:
        """Log an anomaly to the current log file.
        
        Args:
            anomaly: The anomaly data to log
            
        Returns:
            bool: True if logging was successful, False otherwise
        """
        try:
            self._rotate_if_needed()
            
            # Format the log entry
            log_entry = self._format_log_entry(anomaly)
            log_line = json.dumps(log_entry) + "\n"
            
            # Write to file
            with open(self.current_file, "a") as f:
                f.write(log_line)
                
            # Update size
            self.current_size += len(log_line.encode('utf-8'))
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to log anomaly: {e}")
            return False
            
    def get_recent_anomalies(self, count: int = 100) -> list:
        """Get the most recent anomalies from the log files.
        
        Args:
            count: Maximum number of anomalies to return
            
        Returns:
            list: List of recent anomalies
        """
        anomalies = []
        try:
            # Get all log files (including compressed ones)
            log_files = list(self.log_dir.glob("rfghost_*.jsonl*"))
            
            # Sort by modification time (newest first)
            log_files.sort(key=lambda x: x.stat().st_mtime, reverse=True)
            
            # Read from files until we have enough anomalies
            for log_file in log_files:
                if len(anomalies) >= count:
                    break
                    
                try:
                    if log_file.suffix == '.gz':
                        with gzip.open(log_file, 'rt') as f:
                            for line in f:
                                if len(anomalies) >= count:
                                    break
                                anomalies.append(json.loads(line))
                    else:
                        with open(log_file, 'r') as f:
                            for line in f:
                                if len(anomalies) >= count:
                                    break
                                anomalies.append(json.loads(line))
                except Exception as e:
                    logger.error(f"Error reading log file {log_file}: {e}")
                    
        except Exception as e:
            logger.error(f"Failed to get recent anomalies: {e}")
            
        return anomalies[:count]

# Create a singleton instance
_rf_logger = None

def get_rf_logger(log_dir: str = "logs") -> RFLogger:
    """Get or create the RF logger singleton."""
    global _rf_logger
    if _rf_logger is None:
        _rf_logger = RFLogger(log_dir)
    return _rf_logger

def log_anomaly(anomaly: Dict, log_dir: str = "logs") -> bool:
    """Public interface for logging anomalies."""
    logger = get_rf_logger(log_dir)
    return logger.log_anomaly(anomaly)
