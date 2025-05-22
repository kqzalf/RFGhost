"""Main entry point for RFGhost application."""
import sys
import yaml
from typing import Dict, Any
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
        
        # Main application logic here
        # This is a placeholder for the actual implementation
        
        return 0
        
    except Exception as error:
        logger.critical(f"Application error: {error}")
        return 1


if __name__ == '__main__':
    sys.exit(main())
