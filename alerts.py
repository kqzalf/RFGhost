"""Alert system for RFGhost application."""
from typing import Dict, List, Optional
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import json
import requests
from logger import logger


class Alerts:
    """Alert system for sending notifications about RF anomalies.

    This class handles various types of alerts including email, webhook,
    and local logging notifications.
    """

    def __init__(self, config: Dict) -> None:
        """Initialize the alert system.

        Args:
            config: Dictionary containing alert configuration
        """
        self.config = config
        self.email_config = config.get('email', {})
        self.webhook_config = config.get('webhook', {})
        self.logger = logger

    def send_email(self, subject: str, message: str) -> bool:
        """Send an email alert.

        Args:
            subject: Email subject
            message: Email message body

        Returns:
            bool: True if email was sent successfully
        """
        if not self.email_config.get('enabled', False):
            return False

        try:
            msg = MIMEMultipart()
            msg['From'] = self.email_config['from']
            msg['To'] = self.email_config['to']
            msg['Subject'] = subject
            msg.attach(MIMEText(message, 'plain'))

            with smtplib.SMTP(self.email_config['smtp_server'], 
                            self.email_config['smtp_port']) as server:
                if self.email_config.get('use_tls', True):
                    server.starttls()
                if self.email_config.get('username'):
                    server.login(self.email_config['username'],
                               self.email_config['password'])
                server.send_message(msg)
            return True
        except Exception as e:
            self.logger.error(f"Failed to send email: {e}")
            return False

    def send_webhook(self, data: Dict) -> bool:
        """Send a webhook alert.

        Args:
            data: Dictionary containing alert data

        Returns:
            bool: True if webhook was sent successfully
        """
        if not self.webhook_config.get('enabled', False):
            return False

        try:
            headers = {'Content-Type': 'application/json'}
            response = requests.post(
                self.webhook_config['url'],
                data=json.dumps(data),
                headers=headers,
                timeout=5
            )
            return response.status_code == 200
        except Exception as e:
            self.logger.error(f"Failed to send webhook: {e}")
            return False

    def send_alert(self, alert_type: str, data: Dict) -> None:
        """Send an alert through configured channels.

        Args:
            alert_type: Type of alert (e.g., 'anomaly', 'error')
            data: Dictionary containing alert data
        """
        message = f"RFGhost Alert - {alert_type}\n"
        message += json.dumps(data, indent=2)

        # Log the alert
        self.logger.warning(message)

        # Send email if configured
        if self.email_config.get('enabled', False):
            self.send_email(f"RFGhost {alert_type.title()} Alert", message)

        # Send webhook if configured
        if self.webhook_config.get('enabled', False):
            self.send_webhook({
                'type': alert_type,
                'data': data,
                'timestamp': data.get('timestamp')
            })
