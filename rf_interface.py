"""RF interface for RFGhost application."""
from typing import Dict, List, Optional
import time
import threading
from queue import Queue
import numpy as np
from logger import logger


class RFInterface:
    """Interface for RF signal acquisition and processing.

    This class handles RF signal acquisition, processing, and provides
    methods for signal analysis and monitoring.
    """

    def __init__(self, config: Dict) -> None:
        """Initialize the RF interface.

        Args:
            config: Dictionary containing RF interface configuration
        """
        self._config = config
        self._sample_rate = config.get('sample_rate', 1000)
        self._frequency = config.get('frequency', 433.92)  # MHz
        self._gain = config.get('gain', 20)  # dB
        self._running = False
        self._data_queue = Queue(maxsize=1000)
        self._scan_thread: Optional[threading.Thread] = None

    def start_scanning(self) -> None:
        """Start the RF scanning process in a background thread."""
        if self._running:
            logger.warning("RF scanning already running")
            return

        self._running = True
        self._scan_thread = threading.Thread(target=self._scan_loop)
        self._scan_thread.daemon = True
        self._scan_thread.start()
        logger.info("RF scanning started")

    def stop_scanning(self) -> None:
        """Stop the RF scanning process."""
        self._running = False
        if self._scan_thread is not None:
            self._scan_thread.join(timeout=5)
        logger.info("RF scanning stopped")

    def _scan_loop(self) -> None:
        """Main scanning loop that runs in background thread."""
        while self._running:
            try:
                # Simulate RF signal acquisition
                # In a real implementation, this would read from hardware
                signal = self._acquire_signal()
                # Add timestamp and metadata
                data = {
                    'timestamp': time.time(),
                    'signal': signal,
                    'frequency': self._frequency,
                    'gain': self._gain
                }
                # Add to queue, drop oldest if full
                if not self._data_queue.full():
                    self._data_queue.put(data)
                else:
                    self._data_queue.get()  # Remove oldest
                    self._data_queue.put(data)
                # Sleep to maintain sample rate
                time.sleep(1.0 / self._sample_rate)
            except (IOError, ValueError) as e:
                logger.error(f"Error in scan loop: {e}")
                time.sleep(1)  # Prevent tight loop on error

    def _acquire_signal(self) -> float:
        """Acquire a single RF signal sample.

        Returns:
            float: Signal strength in dBm
        """
        # Simulate signal acquisition
        # In a real implementation, this would read from hardware
        return np.random.normal(-50, 5)  # Simulated signal strength

    def get_latest_data(self, max_samples: int = 100) -> List[Dict]:
        """Get the most recent RF signal data.

        Args:
            max_samples: Maximum number of samples to return

        Returns:
            List of dictionaries containing signal data
        """
        data = []
        while not self._data_queue.empty() and len(data) < max_samples:
            data.append(self._data_queue.get())
        return data

    def get_signal_statistics(self, samples: int = 100) -> Dict[str, float]:
        """Calculate statistics for recent signal data.

        Args:
            samples: Number of samples to analyze

        Returns:
            Dictionary containing signal statistics
        """
        data = self.get_latest_data(samples)
        if not data:
            return self._get_empty_statistics()

        signals = [d['signal'] for d in data]
        return {
            'mean': float(np.mean(signals)),
            'std': float(np.std(signals)),
            'min': float(np.min(signals)),
            'max': float(np.max(signals))
        }

    @staticmethod
    def _get_empty_statistics() -> Dict[str, float]:
        """Get empty statistics dictionary.

        Returns:
            Dictionary with zero values for all statistics
        """
        return {
            'mean': 0.0,
            'std': 0.0,
            'min': 0.0,
            'max': 0.0
        }
