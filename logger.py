"""Logging module for RFGhost application."""
import logging
import sys
from typing import Optional


class RFLogger:
    """Custom logger class for RFGhost application.
    
    This class provides a centralized logging mechanism with configurable
    log levels and output formats.
    """
    
    def __init__(self, name: str = "RFGhost", level: int = logging.INFO) -> None:
        """Initialize the logger.
        
        Args:
            name: Name of the logger instance
            level: Logging level (default: INFO)
        """
        self.logger = logging.getLogger(name)
        self.logger.setLevel(level)
        
        if not self.logger.handlers:
            self._setup_handlers()
    
    def _setup_handlers(self) -> None:
        """Set up logging handlers with proper formatting."""
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
        )
        
        # Console handler
        console_handler = logging.StreamHandler(sys.stdout)
        console_handler.setFormatter(formatter)
        self.logger.addHandler(console_handler)
        
        # File handler
        file_handler = logging.FileHandler('rfghost.log')
        file_handler.setFormatter(formatter)
        self.logger.addHandler(file_handler)
    
    def debug(self, message: str) -> None:
        """Log a debug message.
        
        Args:
            message: Debug message to log
        """
        self.logger.debug(message)
    
    def info(self, message: str) -> None:
        """Log an info message.
        
        Args:
            message: Info message to log
        """
        self.logger.info(message)
    
    def warning(self, message: str) -> None:
        """Log a warning message.
        
        Args:
            message: Warning message to log
        """
        self.logger.warning(message)
    
    def error(self, message: str) -> None:
        """Log an error message.
        
        Args:
            message: Error message to log
        """
        self.logger.error(message)
    
    def critical(self, message: str) -> None:
        """Log a critical message.
        
        Args:
            message: Critical message to log
        """
        self.logger.critical(message)


# Create a default logger instance
logger = RFLogger()
