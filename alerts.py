"""Alert management module for RFGhost.

This module handles sending alerts to various channels (Slack, webhooks, etc.)
when anomalies are detected.
"""

import logging
from typing import Dict, Any, Optional
import requests

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RFGhost')

class AlertManager:
    """Manages sending alerts to various channels."""

    def __init__(self, webhook_url: str):
        """Initialize the alert manager.

        Args:
            webhook_url: URL for the webhook (e.g., Slack webhook)
        """
        self.webhook_url = webhook_url

    def send_alert(self, anomaly_data: Dict[str, Any]) -> bool:
        """Send an alert for a detected anomaly.

        Args:
            anomaly_data: Dictionary containing anomaly information
        Returns:
            True if alert was sent successfully, False otherwise
        """
        try:
            # Format the alert message
            message = self._format_alert(anomaly_data)
            # Send to webhook
            response = requests.post(
                self.webhook_url,
                json=message,
                timeout=5
            )
            if response.status_code == 200:
                logger.info("Alert sent successfully")
                return True
            logger.error("Failed to send alert: %s", response.text)
            return False
        except (requests.RequestException, ValueError) as e:
            logger.error("Error sending alert: %s", str(e))
            return False

    def _format_alert(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format the alert message for sending.

        Args:
            anomaly_data: Dictionary containing anomaly information
        Returns:
            Formatted message dictionary
        """
        anomalies = anomaly_data.get('anomalies', [])
        signal = anomaly_data.get('signal', {})
        return {
            "text": f"RF Anomaly Detected: {anomalies}\nDetails: {signal}"
        }

global_alert_manager: Optional[AlertManager] = None

