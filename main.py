"""Main entry point for RFGhost application."""
import sys
from typing import Dict, Any
import yaml
from logger import logger
from anomaly_engine import AnomalyEngine


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


def main() -> int:
    """Main application entry point.

    Returns:
        Exit code (0 for success, non-zero for failure)
    """
    try:
        # Load configuration
        config = load_config('config.yaml')

        # Initialize components
        engine = AnomalyEngine(
            threshold=config.get('anomaly_threshold', 2.0)
        )

        logger.info("RFGhost application started")

        # Example main logic: set baseline and detect anomalies
        baseline_data = [1.0, 1.1, 0.9, 1.05, 1.02]
        engine.set_baseline(baseline_data)
        test_data = [1.0, 1.2, 3.0, 0.95, 1.03]
        anomalies, scores = engine.detect_anomalies(test_data)
        logger.info(f"Test data: {test_data}")
        logger.info(f"Anomaly scores: {scores}")
        logger.info(f"Anomalies detected: {anomalies}")

        return 0

    except (FileNotFoundError, yaml.YAMLError) as error:
        logger.critical(f"Configuration error: {error}")
        return 1
    except Exception as error:  # pylint: disable=broad-exception-caught
        logger.critical(f"Unexpected error: {error}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
