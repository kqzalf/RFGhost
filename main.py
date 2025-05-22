#!/usr/bin/env python3
"""Main module for RF anomaly detection system.

This module provides the main entry point and control flow for the RF anomaly
detection system, including frequency scanning and anomaly processing.
"""

import logging
import signal
import sys
import time
from typing import Dict, Optional, Any
from rf_interface import get_rf_interface, scan_frequency
from anomaly_engine import get_anomaly_engine
from logger import RFLogger
from alerts import AlertManager

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RFGhost')

class RFGhost:
    """Main RF anomaly detection system."""
    
    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the RF anomaly detection system.
        
        Args:
            config: Optional configuration dictionary
        """
        self.config = config or {}
        self.rf = get_rf_interface()
        self.anomaly_engine = get_anomaly_engine()
        self.logger = RFLogger()
        self.alert_manager = AlertManager(webhook_url=self.config.get("webhook_url", ""))
        self.running = False
        self.frequencies = self.config.get("frequencies", [433.92, 868.0, 915.0])
        self.scan_interval = self.config.get("scan_interval", 1.0)
        
    def _handle_shutdown(self, _signum: int, _frame: Any) -> None:
        """Handle shutdown signal.
        
        Args:
            _signum: Signal number (unused)
            _frame: Current stack frame (unused)
        """
        logger.info("Shutting down...")
        self.running = False
        
    def _scan_frequency(self, freq: float) -> Optional[Dict[str, Any]]:
        """Scan a frequency for signals.
        
        Args:
            freq: Frequency to scan in MHz
            
        Returns:
            Signal data if successful, None otherwise
        """
        try:
            signal_data = scan_frequency(freq)
            self.logger.log_signal(signal_data)
            return signal_data
        except (ValueError, IOError, OSError) as e:
            logger.error("Error scanning frequency %.3f MHz: %s", freq, str(e))
            return None
            
    def _process_anomalies(self, signal_data: Dict[str, Any]) -> None:
        """Process signal data for anomalies.
        
        Args:
            signal_data: Signal data to analyze
        """
        try:
            anomalies = self.anomaly_engine.detect_anomalies(signal_data)
            if anomalies:
                anomaly_data = {
                    "signal": signal_data,
                    "anomalies": [a.value for a in anomalies]
                }
                self.logger.log_anomaly(anomaly_data)
                self.alert_manager.send_alert(anomaly_data)
        except (ValueError, IOError, OSError, KeyError) as e:
            logger.error("Error processing anomalies: %s", str(e))
            
    def run(self) -> None:
        """Run the RF anomaly detection system."""
        try:
            # Set up signal handlers
            signal.signal(signal.SIGINT, self._handle_shutdown)
            signal.signal(signal.SIGTERM, self._handle_shutdown)
            
            logger.info("Starting RF anomaly detection system...")
            self.running = True
            
            while self.running:
                for freq in self.frequencies:
                    if not self.running:
                        break
                        
                    signal_data = self._scan_frequency(freq)
                    if signal_data:
                        self._process_anomalies(signal_data)
                        
                    time.sleep(self.scan_interval)
                    
            logger.info("RF anomaly detection system stopped.")
            
        except (ValueError, IOError, OSError, KeyError) as e:
            logger.error("Error in main loop: %s", str(e))
            sys.exit(1)
            
def main() -> None:
    """Main entry point."""
    config = {
        "frequencies": [433.92, 868.0, 915.0],
        "scan_interval": 1.0,
        "webhook_url": ""  # Add your webhook URL here
    }
    
    rfghost = RFGhost(config)
    rfghost.run()
    
if __name__ == "__main__":
    main()
