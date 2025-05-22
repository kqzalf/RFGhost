"""RF interface module for CC1101 transceiver.

This module provides an interface for communicating with the CC1101 RF transceiver
and performing signal detection and analysis.
"""

import logging
import time
from typing import Dict, List, Optional, Any, Tuple
import numpy as np
import spidev

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RFGhost')

class RFInterface:
    """Interface for CC1101 RF transceiver."""

    def __init__(self, bus: int = 0, device: int = 0):
        """Initialize the RF interface.

        Args:
            bus: SPI bus number
            device: SPI device number
        """
        self.spi = spidev.SpiDev()
        self.bus = bus
        self.device = device
        self.sample_rate = 1000  # Hz
        self.sample_duration = 0.1  # seconds
        self.rssi_offset = 74  # dBm

    def _open_spi(self) -> None:
        """Open SPI connection to CC1101."""
        try:
            self.spi.open(self.bus, self.device)
            self.spi.max_speed_hz = 1000000
            self.spi.mode = 0
        except (IOError, OSError) as e:
            logger.error("Failed to open SPI connection: %s", str(e))
            raise

    def _close_spi(self) -> None:
        """Close SPI connection."""
        try:
            self.spi.close()
        except (IOError, OSError) as e:
            logger.error("Failed to close SPI connection: %s", str(e))

    def _write_register(self, address: int, value: int) -> None:
        """Write to CC1101 register.

        Args:
            address: Register address
            value: Value to write
        """
        try:
            self.spi.xfer([address, value])
        except (IOError, OSError) as e:
            logger.error("Failed to write register: %s", str(e))
            raise

    def _read_register(self, address: int) -> int:
        """Read from CC1101 register.

        Args:
            address: Register address

        Returns:
            Register value
        """
        try:
            response = self.spi.xfer([address | 0x80, 0])
            return response[1]
        except (IOError, OSError) as e:
            logger.error("Failed to read register: %s", str(e))
            raise

    def _set_frequency(self, freq_mhz: float) -> None:
        """Set CC1101 frequency.

        Args:
            freq_mhz: Frequency in MHz
        """
        # Convert MHz to Hz
        freq_hz = int(freq_mhz * 1000000)

        # Calculate frequency registers
        freq_reg = freq_hz / (26 * 1000000)
        freq_reg = int(freq_reg * 65536)

        # Write frequency registers
        self._write_register(0x0D, (freq_reg >> 16) & 0xFF)  # FREQ2
        self._write_register(0x0E, (freq_reg >> 8) & 0xFF)   # FREQ1
        self._write_register(0x0F, freq_reg & 0xFF)          # FREQ0

    def _get_rssi(self) -> int:
        """Get current RSSI value.

        Returns:
            RSSI value in dBm
        """
        rssi = self._read_register(0x33)  # RSSI register
        if rssi >= 128:
            rssi = (rssi - 256) / 2 - self.rssi_offset
        else:
            rssi = rssi / 2 - self.rssi_offset
        return int(rssi)

    def _get_lqi(self) -> int:
        """Get current LQI value.

        Returns:
            LQI value (0-255)
        """
        return self._read_register(0x34)  # LQI register

    def _get_signal_quality(self) -> float:
        """Calculate signal quality from RSSI and LQI.

        Returns:
            Signal quality (0-1)
        """
        rssi = self._get_rssi()
        lqi = self._get_lqi()

        # Normalize RSSI (-120 to -30 dBm)
        rssi_norm = max(0, min(1, (rssi + 120) / 90))

        # Normalize LQI (0-255)
        lqi_norm = lqi / 255

        # Combine metrics (weighted average)
        return 0.7 * rssi_norm + 0.3 * lqi_norm

    def _sample_signal(self, duration: float) -> Tuple[List[int], List[int]]:
        """Sample signal for specified duration.

        Args:
            duration: Sampling duration in seconds

        Returns:
            Tuple of (RSSI samples, LQI samples)
        """
        samples = int(duration * self.sample_rate)
        rssi_samples = []
        lqi_samples = []

        for _ in range(samples):
            rssi_samples.append(self._get_rssi())
            lqi_samples.append(self._get_lqi())
            time.sleep(1 / self.sample_rate)

        return rssi_samples, lqi_samples

    def scan_frequency(self, freq_mhz: float) -> Dict[str, Any]:
        """Scan a frequency for signals.

        Args:
            freq_mhz: Frequency to scan in MHz

        Returns:
            Dictionary containing signal data
        """
        try:
            # Set frequency
            self._set_frequency(freq_mhz)

            # Sample signal
            rssi_samples, lqi_samples = self._sample_signal(self.sample_duration)

            # Calculate statistics
            rssi_mean = np.mean(rssi_samples)
            rssi_std = np.std(rssi_samples)
            lqi_mean = np.mean(lqi_samples)

            # Calculate signal quality
            quality = self._get_signal_quality()

            # Calculate entropy
            hist, _ = np.histogram(rssi_samples, bins=256, density=True)
            hist = hist[hist > 0]
            entropy = -np.sum(hist * np.log2(hist))
            entropy = min(1.0, entropy / 8.0)  # Normalize to 0-1

            return {
                "frequency": freq_mhz,
                "rssi": int(rssi_mean),
                "rssi_std": float(rssi_std),
                "lqi": int(lqi_mean),
                "quality": float(quality),
                "entropy": float(entropy),
                "samples": {
                    "rssi": rssi_samples,
                    "lqi": lqi_samples
                }
            }

        except (ValueError, IOError, OSError) as e:
            logger.error("Error scanning frequency: %s", str(e))
            raise

    def __enter__(self) -> 'RFInterface':
        """Context manager entry."""
        self._open_spi()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        """Context manager exit."""
        self._close_spi()

def get_rf_interface(bus: int = 0, device: int = 0) -> RFInterface:
    """Get or create the global RF interface instance.

    Args:
        bus: SPI bus number
        device: SPI device number

    Returns:
        RFInterface instance
    """
    global _rf_interface
    if _rf_interface is None:
        _rf_interface = RFInterface(bus, device)
    return _rf_interface

def scan_frequency(freq_mhz: float) -> Dict[str, Any]:
    """Scan a frequency for signals.

    Args:
        freq_mhz: Frequency to scan in MHz

    Returns:
        Dictionary containing signal data
    """
    with get_rf_interface() as rf:
        return rf.scan_frequency(freq_mhz)

# Global instance
_rf_interface: Optional[RFInterface] = None

