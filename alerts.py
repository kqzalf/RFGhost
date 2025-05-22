"""Alert management module for RFGhost.

This module handles the generation, formatting, and transmission of alerts
when RF anomalies are detected. It supports multiple alert channels including
console output, webhook notifications, and log files.
"""

import logging
import time
from datetime import datetime
from typing import Dict, Optional

import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RFGhost')

class AlertManager:
    """Manages alert generation and transmission for RF anomalies.
    
    This class handles the formatting and sending of alerts through various
    channels when RF anomalies are detected. It supports multiple alert
    formats and transmission methods.
    """
    
    def __init__(self, config: Dict):
        """Initialize the alert manager with configuration.
        
        Args:
            config: Configuration dictionary containing alert settings
        """
        self.config = config
        self.alert_count = 0
        self.last_alert_time = 0
        self.alert_cooldown = config.get('alert_cooldown', 300)  # 5 minutes default
        self.webhook_url = config.get('webhook_url')
        self.alert_format = config.get('alert_format', 'cyberpunk')
        
    def _format_alert(self, anomaly_data: Dict) -> str:
        """Format anomaly data into an alert message.
        
        Args:
            anomaly_data: Dictionary containing anomaly information
            
        Returns:
            str: Formatted alert message
        """
        if self.alert_format == 'cyberpunk':
            return self._format_cyberpunk(anomaly_data)
        return self._format_standard(anomaly_data)
        
    def _format_cyberpunk(self, anomaly_data: Dict) -> str:
        """Format alert in cyberpunk style.
        
        Args:
            anomaly_data: Dictionary containing anomaly information
            
        Returns:
            str: Cyberpunk-styled alert message
        """
        freq = anomaly_data.get('frequency', 0)
        rssi = anomaly_data.get('rssi', 0)
        entropy = anomaly_data.get('entropy', 0)
        pattern = anomaly_data.get('pattern_match', 0)
        quality = anomaly_data.get('signal_quality', 0)
        
        return (
            f"╔════════════════════════════════════════════════════════════╗\n"
            f"║                    RF ANOMALY DETECTED                      ║\n"
            f"╠════════════════════════════════════════════════════════════╣\n"
            f"║ Frequency: {freq:>8.3f} MHz                                ║\n"
            f"║ Signal Strength: {rssi:>4} dBm                             ║\n"
            f"║ Entropy: {entropy:>8.2f}                                   ║\n"
            f"║ Pattern Match: {pattern:>6.2f}                             ║\n"
            f"║ Signal Quality: {quality:>6.2f}                            ║\n"
            f"║ Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}  ║\n"
            f"╚════════════════════════════════════════════════════════════╝"
        )
        
    def _format_standard(self, anomaly_data: Dict) -> str:
        """Format alert in standard style.
        
        Args:
            anomaly_data: Dictionary containing anomaly information
            
        Returns:
            str: Standard alert message
        """
        return (
            f"RF Anomaly Detected:\n"
            f"Frequency: {anomaly_data.get('frequency', 0):.3f} MHz\n"
            f"Signal Strength: {anomaly_data.get('rssi', 0)} dBm\n"
            f"Entropy: {anomaly_data.get('entropy', 0):.2f}\n"
            f"Pattern Match: {anomaly_data.get('pattern_match', 0):.2f}\n"
            f"Signal Quality: {anomaly_data.get('signal_quality', 0):.2f}\n"
            f"Timestamp: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
        )
        
    def _check_cooldown(self) -> bool:
        """Check if enough time has passed since last alert.
        
        Returns:
            bool: True if cooldown period has passed, False otherwise
        """
        current_time = time.time()
        if current_time - self.last_alert_time < self.alert_cooldown:
            return False
        self.last_alert_time = current_time
        return True
        
    def _send_webhook(self, message: str) -> bool:
        """Send alert to webhook URL.
        
        Args:
            message: Alert message to send
            
        Returns:
            bool: True if webhook notification successful, False otherwise
        """
        if not self.webhook_url:
            return False
            
        try:
            response = requests.post(
                self.webhook_url,
                json={'message': message},
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            logger.error("Failed to send webhook alert: %s", str(e))
            return False
            
    def send_alert(self, anomaly_data: Dict) -> bool:
        """Send alert for detected anomaly.
        
        Args:
            anomaly_data: Dictionary containing anomaly information
            
        Returns:
            bool: True if alert was sent successfully, False otherwise
        """
        if not self._check_cooldown():
            return False
            
        self.alert_count += 1
        message = self._format_alert(anomaly_data)
        
        # Log alert
        logger.info("Alert #%d: %s", self.alert_count, message)
        
        # Send webhook if configured
        if self.webhook_url:
            if not self._send_webhook(message):
                logger.error("Failed to send webhook alert")
                return False
                
        return True

# Create a singleton instance
ALERT_MANAGER = None

def get_alert_manager(config: Dict = None) -> AlertManager:
    """Get or create the alert manager singleton.
    
    Args:
        config: Configuration dictionary
        
    Returns:
        AlertManager: Alert manager instance
    """
    global ALERT_MANAGER
    if ALERT_MANAGER is None:
        ALERT_MANAGER = AlertManager(config or {})
    return ALERT_MANAGER

def send_alert(anomaly_data: Dict, config: Dict = None) -> bool:
    """Public interface for sending alerts.
    
    Args:
        anomaly_data: Dictionary containing anomaly information
        config: Configuration dictionary
        
    Returns:
        bool: True if alert was sent successfully, False otherwise
    """
    manager = get_alert_manager(config)
    return manager.send_alert(anomaly_data) 