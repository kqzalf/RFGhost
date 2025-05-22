#!/usr/bin/env python3
"""RFGhost - RF Anomaly Detection System

This module implements the main RFGhost system that monitors RF frequencies
for anomalies and potential security threats.
"""

import argparse
import logging
import signal
import sys
import time
from typing import Dict, List, Optional, Any
import yaml
from pathlib import Path

from rf_interface import get_rf_interface, scan_frequency
from anomaly_engine import get_anomaly_engine, AnomalyThresholds, detect_anomalies
from logger import get_rf_logger, log_anomaly
from alerts import get_alert_manager, send_alert

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('RFGhost')

class RFGhost:
    """Main RFGhost system class for monitoring and detecting RF anomalies."""
    
    def __init__(self, config_path: str = "config.yaml") -> None:
        """Initialize RFGhost with configuration.
        
        Args:
            config_path: Path to the configuration YAML file
        """
        self.config = self._load_config(config_path)
        self.running = True
        self.scan_interval = self.config.get("scan_interval", 1.0)
        self.frequencies = self.config["frequencies"]
        
        # Initialize components
        self.rf_interface = get_rf_interface()
        self.anomaly_engine = get_anomaly_engine(
            AnomalyThresholds(
                rssi_high=self.config.get("rssi_threshold_high", -50),
                rssi_low=self.config.get("rssi_threshold_low", -90),
                entropy_threshold=self.config.get("entropy_threshold", 0.8),
                duration_threshold=self.config.get("duration_threshold", 2.0),
                pattern_threshold=self.config.get("pattern_threshold", 0.7)
            )
        )
        self.logger = get_rf_logger(self.config.get("log_dir", "logs"))
        self.alert_manager = get_alert_manager(self.config["slack_webhook"])
        
        # Set up signal handlers
        signal.signal(signal.SIGINT, self._handle_shutdown)
        signal.signal(signal.SIGTERM, self._handle_shutdown)
        
    def _load_config(self, config_path: str) -> Dict[str, Any]:
        """Load and validate configuration from YAML file.
        
        Args:
            config_path: Path to the configuration file
            
        Returns:
            Dict containing the configuration
            
        Raises:
            ValueError: If required configuration keys are missing
            FileNotFoundError: If config file doesn't exist
            yaml.YAMLError: If config file is invalid YAML
        """
        try:
            with open(config_path, encoding='utf-8') as f:
                config = yaml.safe_load(f)
                
            # Validate required configuration
            required_keys = ["frequencies", "slack_webhook"]
            missing_keys = [key for key in required_keys if key not in config]
            if missing_keys:
                raise ValueError(f"Missing required configuration keys: {missing_keys}")
                
            return config
        except FileNotFoundError:
            logger.error(f"Configuration file not found: {config_path}")
            sys.exit(1)
        except yaml.YAMLError as e:
            logger.error(f"Invalid YAML in configuration file: {e}")
            sys.exit(1)
        except Exception as e:
            logger.error(f"Failed to load configuration: {e}")
            sys.exit(1)
            
    def _handle_shutdown(self, signum: int, frame: Any) -> None:
        """Handle shutdown signals gracefully.
        
        Args:
            signum: Signal number
            frame: Current stack frame
        """
        logger.info("Shutting down RFGhost...")
        self.running = False
        
    def _scan_frequency(self, freq: float) -> Optional[Dict[str, Any]]:
        """Scan a frequency with error handling.
        
        Args:
            freq: Frequency to scan in MHz
            
        Returns:
            Dict containing signal data or None if scan failed
        """
        try:
            return scan_frequency(freq)
        except Exception as e:
            logger.error(f"Error scanning frequency {freq} MHz: {e}")
            return None
            
    def _process_anomalies(self, anomalies: List[Dict[str, Any]]) -> None:
        """Process detected anomalies.
        
        Args:
            anomalies: List of detected anomalies
        """
        for anomaly in anomalies:
            try:
                # Log the anomaly
                if self.logger.log_anomaly(anomaly):
                    logger.info(f"Logged anomaly: {anomaly['type']}")
                    
                # Send alert
                if self.alert_manager.send_alert(anomaly):
                    logger.info(f"Sent alert for: {anomaly['type']}")
                    
            except Exception as e:
                logger.error(f"Error processing anomaly: {e}")
                
    def run(self) -> None:
        """Main program loop."""
        logger.info("Starting RFGhost...")
        logger.info(f"Monitoring frequencies: {self.frequencies}")
        
        while self.running:
            try:
                for freq in self.frequencies:
                    if not self.running:
                        break
                        
                    # Scan frequency
                    signal_data = self._scan_frequency(freq)
                    if signal_data is None:
                        continue
                        
                    # Detect anomalies
                    anomalies = detect_anomalies(signal_data)
                    if anomalies:
                        self._process_anomalies(anomalies)
                        
                    # Sleep between scans
                    time.sleep(self.scan_interval)
                    
            except Exception as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(5)  # Wait before retrying
                
        logger.info("RFGhost shutdown complete")

def parse_args() -> argparse.Namespace:
    """Parse command line arguments.
    
    Returns:
        Parsed command line arguments
    """
    parser = argparse.ArgumentParser(description="RFGhost - RF Anomaly Detector")
    parser.add_argument(
        "-c", "--config",
        default="config.yaml",
        help="Path to configuration file"
    )
    parser.add_argument(
        "-d", "--debug",
        action="store_true",
        help="Enable debug logging"
    )
    return parser.parse_args()

def main() -> None:
    """Main entry point."""
    args = parse_args()
    
    # Set logging level
    if args.debug:
        logging.getLogger().setLevel(logging.DEBUG)
        
    # Create and run RFGhost
    rfghost = RFGhost(args.config)
    rfghost.run()

if __name__ == "__main__":
    main()
