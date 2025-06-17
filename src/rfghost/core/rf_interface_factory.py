"""Factory for creating RF interfaces."""
from typing import Dict, Any
from .rf_interface import RFInterface
from .hackrf_interface import HackRFInterface
from ..utils.logger import logger


class RFInterfaceFactory:
    """Factory class for creating RF interfaces."""

    @staticmethod
    def create_interface(config: Dict[str, Any]) -> RFInterface:
        """Create an RF interface based on configuration.

        Args:
            config: Dictionary containing interface configuration

        Returns:
            An instance of RFInterface or its subclasses

        Raises:
            ValueError: If the interface type is not supported
        """
        interface_type = config.get('type', 'simulated').lower()

        if interface_type == 'hackrf':
            logger.info("Creating HackRF interface")
            return HackRFInterface(config)
        elif interface_type == 'simulated':
            logger.info("Creating simulated RF interface")
            return RFInterface(config)
        else:
            raise ValueError(f"Unsupported RF interface type: {interface_type}") 