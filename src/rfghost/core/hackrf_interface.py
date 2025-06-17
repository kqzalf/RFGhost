"""HackRF interface implementation for RFGhost."""
import time
from typing import Dict, List, Optional, Tuple
import numpy as np
from pyhackrf import HackRF
from ..utils.logger import logger


class HackRFInterface:
    """Interface for HackRF device."""

    def __init__(self, config: Dict) -> None:
        """Initialize the HackRF interface.

        Args:
            config: Dictionary containing HackRF configuration
        """
        self._config = config
        self._sample_rate = config.get('sample_rate', 2000000)  # 2MHz default
        self._frequency = config.get('frequency', 433920000)  # 433.92MHz default
        self._gain = config.get('gain', 20)  # dB
        self._lna_gain = config.get('lna_gain', 40)  # dB
        self._vga_gain = config.get('vga_gain', 40)  # dB
        self._running = False
        self._device: Optional[HackRF] = None
        self._buffer_size = 16384  # Default buffer size

    def _setup_device(self) -> None:
        """Set up the HackRF device with configured parameters."""
        try:
            self._device = HackRF()
            self._device.sample_rate = self._sample_rate
            self._device.center_freq = self._frequency
            self._device.gain = self._gain
            self._device.lna_gain = self._lna_gain
            self._device.vga_gain = self._vga_gain
            logger.info("HackRF device initialized successfully")
        except Exception as e:
            logger.error(f"Failed to initialize HackRF device: {e}")
            raise

    def start_scanning(self) -> None:
        """Start the HackRF scanning process."""
        if self._running:
            logger.warning("HackRF scanning already running")
            return

        try:
            if not self._device:
                self._setup_device()
            self._running = True
            logger.info("HackRF scanning started")
        except Exception as e:
            logger.error(f"Failed to start HackRF scanning: {e}")
            raise

    def stop_scanning(self) -> None:
        """Stop the HackRF scanning process."""
        self._running = False
        if self._device:
            try:
                self._device.close()
                self._device = None
            except Exception as e:
                logger.error(f"Error closing HackRF device: {e}")
        logger.info("HackRF scanning stopped")

    def get_latest_data(self, max_samples: int = 100) -> List[Dict]:
        """Get the most recent RF signal data from HackRF.

        Args:
            max_samples: Maximum number of samples to return

        Returns:
            List of dictionaries containing signal data
        """
        if not self._device or not self._running:
            return []

        try:
            # Read raw samples from HackRF
            samples = self._device.read_samples(self._buffer_size)
            
            # Convert to power in dBm
            # HackRF provides complex I/Q samples
            power = 20 * np.log10(np.abs(samples))
            
            # Create data points
            data = []
            for i, pwr in enumerate(power[:max_samples]):
                data.append({
                    'timestamp': time.time() - (len(power) - i) / self._sample_rate,
                    'signal': float(pwr),
                    'frequency': self._frequency,
                    'gain': self._gain
                })
            
            return data
        except Exception as e:
            logger.error(f"Error reading from HackRF: {e}")
            return []

    def get_signal_statistics(self, samples: int = 100) -> Dict[str, float]:
        """Calculate statistics for recent signal data.

        Args:
            samples: Number of samples to analyze

        Returns:
            Dictionary containing signal statistics
        """
        data = self.get_latest_data(samples)
        if not data:
            return {
                'mean': 0.0,
                'std': 0.0,
                'min': 0.0,
                'max': 0.0
            }

        signals = [d['signal'] for d in data]
        return {
            'mean': float(np.mean(signals)),
            'std': float(np.std(signals)),
            'min': float(np.min(signals)),
            'max': float(np.max(signals))
        }

    def set_frequency(self, frequency: int) -> None:
        """Set the center frequency.

        Args:
            frequency: Center frequency in Hz
        """
        if self._device:
            try:
                self._device.center_freq = frequency
                self._frequency = frequency
                logger.info(f"Frequency set to {frequency} Hz")
            except Exception as e:
                logger.error(f"Failed to set frequency: {e}")
                raise

    def set_gain(self, gain: int) -> None:
        """Set the RF gain.

        Args:
            gain: RF gain in dB
        """
        if self._device:
            try:
                self._device.gain = gain
                self._gain = gain
                logger.info(f"Gain set to {gain} dB")
            except Exception as e:
                logger.error(f"Failed to set gain: {e}")
                raise 