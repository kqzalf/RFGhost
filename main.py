"""Main entry point for RFGhost application."""
import sys
import time
import signal
from typing import Dict, Any
import yaml
from logger import logger
from anomaly_engine import AnomalyEngine
from rf_interface import RFInterface
from alerts import Alerts


def load_config(config_path: str) -> Dict[str, Any]:
    """Load configuration from YAML file.

    Args:
        config_path: Path to the configuration file

    Returns:
        Dictionary containing configuration parameters

    Raises:
        FileNotFoundError: If config file doesn't exist
        yaml.YAMLError: If config file is invalid
    """
    try:
        with open(config_path, 'r', encoding='utf-8') as file:
            return yaml.safe_load(file)
    except FileNotFoundError:
        logger.error(f"Configuration file not found: {config_path}")
        raise
    except yaml.YAMLError as error:
        logger.error(f"Invalid YAML configuration: {error}")
        raise


class RFGhost:
    """Main RFGhost application class."""

    def __init__(self, config: Dict[str, Any]) -> None:
        """Initialize RFGhost application.

        Args:
            config: Application configuration dictionary
        """
        self.config = config
        self.running = False

        # Initialize components
        self.rf_interface = RFInterface(config.get('rf_interface', {}))
        self.anomaly_engine = AnomalyEngine(
            threshold=config.get('anomaly_threshold', 2.0)
        )
        self.alerts = Alerts(config.get('alerts', {}))

        # Set up signal handlers
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)

    def _signal_handler(self, signum: int, _frame: Any) -> None:
        """Handle termination signals.

        Args:
            signum: Signal number
            _frame: Current stack frame (unused)
        """
        logger.info(f"Received signal {signum}")
        self.stop()

    def start(self) -> None:
        """Start the RFGhost application."""
        if self.running:
            logger.warning("RFGhost already running")
            return

        self.running = True
        logger.info("Starting RFGhost application")

        # Start RF scanning
        self.rf_interface.start_scanning()

        # Main processing loop
        while self.running:
            try:
                # Get latest RF data
                data = self.rf_interface.get_latest_data()
                if not data:
                    time.sleep(0.1)
                    continue

                # Extract signal values
                signals = [d['signal'] for d in data]

                # Detect anomalies
                anomalies, scores = self.anomaly_engine.detect_anomalies(signals)

                # Process any anomalies
                if any(anomalies):
                    self._handle_anomalies(data, anomalies, scores)

                # Log statistics periodically
                stats = self.rf_interface.get_signal_statistics()
                logger.debug(f"Signal statistics: {stats}")

                time.sleep(0.1)  # Prevent tight loop

            except (IOError, ValueError) as e:
                logger.error(f"Error in main loop: {e}")
                time.sleep(1)  # Prevent tight loop on error

    def stop(self) -> None:
        """Stop the RFGhost application."""
        if not self.running:
            return

        logger.info("Stopping RFGhost application")
        self.running = False
        self.rf_interface.stop_scanning()

    def _handle_anomalies(self, data: list, anomalies: list, scores: list) -> None:
        """Handle detected anomalies.

        Args:
            data: List of RF data points
            anomalies: List of boolean anomaly flags
            scores: List of anomaly scores
        """
        # Find indices of anomalies
        anomaly_indices = [i for i, is_anomaly in enumerate(anomalies) if is_anomaly]

        # Prepare alert data
        alert_data = {
            'timestamp': time.time(),
            'anomaly_count': len(anomaly_indices),
            'anomalies': [
                {
                    'timestamp': data[i]['timestamp'],
                    'signal': data[i]['signal'],
                    'score': scores[i]
                }
                for i in anomaly_indices
            ],
            'statistics': self.rf_interface.get_signal_statistics()
        }

        # Send alert
        self.alerts.send_alert('anomaly', alert_data)


def main() -> int:
    """Main application entry point.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Load configuration
        config = load_config('config.yaml')

        # Create and start application
        app = RFGhost(config)
        app.start()

        return 0

    except (FileNotFoundError, yaml.YAMLError) as error:
        logger.critical(f"Configuration error: {error}")
        return 1
    except Exception as error:  # pylint: disable=broad-exception-caught
        logger.critical(f"Unexpected error: {error}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
