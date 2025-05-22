"""Alert management module for RFGhost.

This module handles sending alerts to various channels (Slack, webhooks, etc.)
when anomalies are detected.
"""

import logging
import requests
from typing import Dict, Any, Optional

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
            else:
                logger.error("Failed to send alert: %s", response.text)
                return False
                
        except Exception as e:
            logger.error("Error sending alert: %s", str(e))
            return False
            
    def _format_alert(self, anomaly_data: Dict[str, Any]) -> Dict[str, Any]:
        """Format anomaly data into an alert message.
        
        Args:
            anomaly_data: Dictionary containing anomaly information
            
        Returns:
            Formatted alert message
        """
        return {
            "text": f"*RFGhost Alert:* `{anomaly_data['type']}`\n"
                   f"> Freq: {anomaly_data['details']['frequency']} MHz | "
                   f"Confidence: {anomaly_data['confidence']:.1%}",
            "attachments": [{
                "color": self._get_alert_color(anomaly_data),
                "fields": [
                    {
                        "title": "Details",
                        "value": self._format_details(anomaly_data),
                        "short": False
                    }
                ]
            }]
        }
        
    def _get_alert_color(self, anomaly_data: Dict[str, Any]) -> str:
        """Get the color for the alert based on anomaly type.
        
        Args:
            anomaly_data: Dictionary containing anomaly information
            
        Returns:
            Color code for the alert
        """
        colors = {
            "ghost_echo": "#FF0000",  # Red
            "void_pulse": "#FFA500",  # Orange
            "static_burst": "#FFFF00",  # Yellow
            "freq_shift": "#00FF00",  # Green
            "pattern": "#0000FF"  # Blue
        }
        return colors.get(anomaly_data["type"], "#808080")  # Default to gray
        
    def _format_details(self, anomaly_data: Dict[str, Any]) -> str:
        """Format the details section of the alert.
        
        Args:
            anomaly_data: Dictionary containing anomaly information
            
        Returns:
            Formatted details string
        """
        details = anomaly_data["details"]
        return "\n".join(f"{k}: {v}" for k, v in details.items())

def get_alert_manager(webhook_url: str) -> AlertManager:
    """Get or create the global alert manager instance.
    
    Args:
        webhook_url: URL for the webhook
        
    Returns:
        AlertManager instance
    """
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager(webhook_url)
    return _alert_manager

# Global instance
_alert_manager: Optional[AlertManager] = None 