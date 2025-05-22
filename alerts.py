import requests
import logging
import time
from typing import Dict, Optional, List
from datetime import datetime
import random
import json

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RFGhost')

class AlertStyle:
    """Cyberpunk/ARG-style alert messages and formatting."""
    
    # Alert headers for different anomaly types
    HEADERS = {
        "Ghost Echo": [
            "⚡ *SIGNAL BREACH DETECTED* ⚡",
            "🌌 *VOID TRANSMISSION INTERCEPTED* 🌌",
            "🔮 *ANOMALOUS SIGNAL PATTERN* 🔮"
        ],
        "Void Pulse": [
            "🌑 *VOID PULSE DETECTED* 🌑",
            "⚫ *SHADOW TRANSMISSION* ⚫",
            "🌠 *GHOST SIGNAL EMERGING* 🌠"
        ],
        "Static Burst": [
            "📡 *STATIC BURST DETECTED* 📡",
            "⚡ *SIGNAL INTERFERENCE* ⚡",
            "🌪️ *FREQUENCY DISTURBANCE* 🌪️"
        ],
        "Frequency Shift": [
            "🔄 *FREQUENCY SHIFT DETECTED* 🔄",
            "🌊 *SIGNAL DRIFT OBSERVED* 🌊",
            "🌀 *FREQUENCY ANOMALY* 🌀"
        ],
        "Signal Pattern": [
            "🎭 *PATTERN RECOGNIZED* 🎭",
            "🔍 *REPEATING SEQUENCE* 🔍",
            "🎯 *SIGNAL PATTERN MATCH* 🎯"
        ]
    }
    
    # Narrative snippets for different confidence levels
    NARRATIVES = {
        "high": [
            "The signal is strong and clear. Something is definitely out there.",
            "This is not a false positive. The pattern is unmistakable.",
            "The void is speaking. We're receiving a clear transmission."
        ],
        "medium": [
            "There's something here, but the signal is weak.",
            "A pattern emerges from the static. Worth investigating.",
            "The signal fades in and out, but it's definitely there."
        ],
        "low": [
            "A whisper in the static. Could be nothing, could be everything.",
            "The signal is faint, but the pattern is intriguing.",
            "Something's there, but it's hard to make out."
        ]
    }
    
    # Technical details formatting
    DETAILS = {
        "rssi": lambda x: f"Signal Strength: {x} dBm",
        "entropy": lambda x: f"Entropy: {x:.1f}%",
        "duration": lambda x: f"Duration: {x:.1f}s",
        "frequency": lambda x: f"Frequency: {x:.3f} MHz",
        "confidence": lambda x: f"Confidence: {x:.0f}%"
    }

class AlertManager:
    def __init__(self, webhook_url: str, retry_count: int = 3, retry_delay: float = 1.0):
        """Initialize the alert manager.
        
        Args:
            webhook_url: Slack webhook URL
            retry_count: Number of retries for failed requests
            retry_delay: Delay between retries in seconds
        """
        self.webhook_url = webhook_url
        self.retry_count = retry_count
        self.retry_delay = retry_delay
        self.last_alert_time = {}  # Track last alert time per anomaly type
        
    def _get_confidence_level(self, confidence: float) -> str:
        """Convert confidence score to level."""
        if confidence >= 0.8:
            return "high"
        elif confidence >= 0.5:
            return "medium"
        return "low"
        
    def _format_technical_details(self, details: Dict) -> str:
        """Format technical details in a readable way."""
        formatted = []
        for key, value in details.items():
            if key in AlertStyle.DETAILS:
                formatted.append(AlertStyle.DETAILS[key](value))
        return " | ".join(formatted)
        
    def _should_throttle(self, anomaly_type: str) -> bool:
        """Check if we should throttle alerts for this type."""
        current_time = time.time()
        if anomaly_type in self.last_alert_time:
            # Throttle to at most one alert per minute per type
            if current_time - self.last_alert_time[anomaly_type] < 60:
                return True
        self.last_alert_time[anomaly_type] = current_time
        return False
        
    def _create_alert_message(self, anomaly: Dict) -> Dict:
        """Create a formatted alert message for Slack."""
        anomaly_type = anomaly["type"]
        details = anomaly["details"]
        confidence = anomaly.get("confidence", 0.5)
        
        # Get random header and narrative
        headers = AlertStyle.HEADERS.get(anomaly_type, ["*ANOMALY DETECTED*"])
        narratives = AlertStyle.NARRATIVES[self._get_confidence_level(confidence)]
        
        header = random.choice(headers)
        narrative = random.choice(narratives)
        technical = self._format_technical_details(details)
        
        # Create the message blocks
        blocks = [
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"{header}\n{narrative}"
                }
            },
            {
                "type": "divider"
            },
            {
                "type": "section",
                "text": {
                    "type": "mrkdwn",
                    "text": f"*Technical Details:*\n{technical}"
                }
            },
            {
                "type": "context",
                "elements": [
                    {
                        "type": "mrkdwn",
                        "text": f"Detected at {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}"
                    }
                ]
            }
        ]
        
        return {
            "blocks": blocks,
            "text": f"RFGhost Alert: {anomaly_type}"  # Fallback text
        }
        
    def send_alert(self, anomaly: Dict) -> bool:
        """Send an alert to Slack.
        
        Args:
            anomaly: The anomaly data to alert about
            
        Returns:
            bool: True if alert was sent successfully
        """
        if self._should_throttle(anomaly["type"]):
            logger.info(f"Throttling alert for {anomaly['type']}")
            return False
            
        message = self._create_alert_message(anomaly)
        
        for attempt in range(self.retry_count):
            try:
                response = requests.post(
                    self.webhook_url,
                    json=message,
                    timeout=5
                )
                response.raise_for_status()
                return True
            except requests.RequestException as e:
                logger.error(f"Failed to send alert (attempt {attempt + 1}/{self.retry_count}): {e}")
                if attempt < self.retry_count - 1:
                    time.sleep(self.retry_delay)
                    
        return False

# Create a singleton instance
_alert_manager = None

def get_alert_manager(webhook_url: str) -> AlertManager:
    """Get or create the alert manager singleton."""
    global _alert_manager
    if _alert_manager is None:
        _alert_manager = AlertManager(webhook_url)
    return _alert_manager

def send_alert(anomaly: Dict, webhook_url: str) -> bool:
    """Public interface for sending alerts."""
    manager = get_alert_manager(webhook_url)
    return manager.send_alert(anomaly)
