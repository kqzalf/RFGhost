"""Output interface for RFGhost application."""
import json
import time
from typing import Dict, Any, Optional
import serial
import paho.mqtt.client as mqtt
from logger import logger


class OutputInterface:
    """Interface for handling multiple output methods (MQTT and Serial)."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize the output interface.

        Args:
            config: Dictionary containing output configuration
        """
        self.config = config
        self.mqtt_client: Optional[mqtt.Client] = None
        self.serial_port: Optional[serial.Serial] = None
        self._setup_outputs()

    def _setup_outputs(self) -> None:
        """Set up MQTT and Serial connections based on configuration."""
        # Setup MQTT if enabled
        if self.config.get('mqtt', {}).get('enabled', False):
            self._setup_mqtt()

        # Setup Serial if enabled
        if self.config.get('serial', {}).get('enabled', False):
            self._setup_serial()

    def _setup_mqtt(self) -> None:
        """Set up MQTT client and connection."""
        mqtt_config = self.config.get('mqtt', {})
        try:
            self.mqtt_client = mqtt.Client()
            self.mqtt_client.username_pw_set(
                mqtt_config.get('username'),
                mqtt_config.get('password')
            )
            self.mqtt_client.connect(
                mqtt_config.get('host', 'localhost'),
                mqtt_config.get('port', 1883)
            )
            self.mqtt_client.loop_start()
            logger.info("MQTT connection established")
        except Exception as e:
            logger.error(f"Failed to setup MQTT: {e}")
            self.mqtt_client = None

    def _setup_serial(self) -> None:
        """Set up Serial connection."""
        serial_config = self.config.get('serial', {})
        try:
            self.serial_port = serial.Serial(
                port=serial_config.get('port', 'COM1'),
                baudrate=serial_config.get('baudrate', 9600),
                timeout=1
            )
            logger.info(f"Serial connection established on {serial_config.get('port')}")
        except Exception as e:
            logger.error(f"Failed to setup Serial: {e}")
            self.serial_port = None

    def publish_data(self, data: Dict[str, Any]) -> None:
        """Publish data to all enabled outputs.

        Args:
            data: Dictionary containing data to publish
        """
        # Add timestamp if not present
        if 'timestamp' not in data:
            data['timestamp'] = time.time()

        # Publish to MQTT if enabled
        if self.mqtt_client:
            try:
                topic = self.config.get('mqtt', {}).get('topic', 'rfghost/data')
                self.mqtt_client.publish(topic, json.dumps(data))
            except Exception as e:
                logger.error(f"Failed to publish to MQTT: {e}")

        # Publish to Serial if enabled
        if self.serial_port:
            try:
                serial_data = json.dumps(data) + '\n'
                self.serial_port.write(serial_data.encode())
            except Exception as e:
                logger.error(f"Failed to write to Serial: {e}")

    def close(self) -> None:
        """Close all output connections."""
        if self.mqtt_client:
            try:
                self.mqtt_client.loop_stop()
                self.mqtt_client.disconnect()
            except Exception as e:
                logger.error(f"Error closing MQTT connection: {e}")

        if self.serial_port:
            try:
                self.serial_port.close()
            except Exception as e:
                logger.error(f"Error closing Serial connection: {e}") 