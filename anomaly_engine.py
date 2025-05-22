"""RF anomaly detection engine.

This module implements various algorithms for detecting anomalies in RF signals,
including ghost echoes, void pulses, static bursts, and frequency shifts.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any
import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RFGhost')

class AnomalyType(Enum):
    """Types of RF anomalies."""
    GHOST_ECHO = "ghost_echo"
    VOID_PULSE = "void_pulse"
    STATIC_BURST = "static_burst"
    FREQ_SHIFT = "freq_shift"
    KNOWN_SIGNAL = "known_signal"

@dataclass
class AnomalyThresholds:
    """Configuration thresholds for anomaly detection."""
    rssi_threshold: int = -80  # dBm
    lqi_threshold: int = 50    # 0-255
    quality_threshold: float = 0.3  # 0-1
    entropy_threshold: float = 0.7  # 0-1
    freq_shift_threshold: float = 0.1  # MHz
    static_burst_duration: float = 0.5  # seconds
    ghost_echo_delay: float = 0.1  # seconds
    void_pulse_duration: float = 0.2  # seconds

class AnomalyEngine:
    """Engine for detecting RF anomalies."""

    def __init__(self, config: Optional[Dict[str, Any]] = None):
        """Initialize the anomaly engine.

        Args:
            config: Optional configuration dictionary
        """
        self.thresholds = AnomalyThresholds(**(config or {}))
        self.signal_history: List[Dict[str, Any]] = []
        self.history_size = 100

    def _detect_ghost_echo(self, signal: Dict[str, Any]) -> bool:
        """Detect ghost echo pattern.

        Args:
            signal: Current signal data

        Returns:
            True if ghost echo detected
        """
        if len(self.signal_history) < 2:
            return False

        # Check for delayed signal repetition
        prev_signal = self.signal_history[-1]
        if (abs(signal["rssi"] - prev_signal["rssi"]) < 5 and
            abs(signal["lqi"] - prev_signal["lqi"]) < 10):
            return True

        return False

    def _detect_void_pulse(self, signal: Dict[str, Any]) -> bool:
        """Detect void pulse pattern.

        Args:
            signal: Current signal data

        Returns:
            True if void pulse detected
        """
        if len(self.signal_history) < 2:
            return False

        # Check for sudden signal drop
        prev_signal = self.signal_history[-1]
        if (signal["rssi"] < self.thresholds.rssi_threshold and
            prev_signal["rssi"] > self.thresholds.rssi_threshold):
            return True

        return False

    def _detect_static_burst(self, signal: Dict[str, Any]) -> bool:
        """Detect static burst pattern.

        Args:
            signal: Current signal data

        Returns:
            True if static burst detected
        """
        if len(self.signal_history) < 2:
            return False

        # Check for sustained high signal
        if (signal["rssi"] > self.thresholds.rssi_threshold and
            signal["lqi"] < self.thresholds.lqi_threshold):
            return True

        return False

    def _detect_freq_shift(self, signal: Dict[str, Any]) -> bool:
        """Detect frequency shift.

        Args:
            signal: Current signal data

        Returns:
            True if frequency shift detected
        """
        if len(self.signal_history) < 2:
            return False

        # Check for sudden frequency change
        prev_signal = self.signal_history[-1]
        freq_diff = abs(signal["frequency"] - prev_signal["frequency"])
        if freq_diff > self.thresholds.freq_shift_threshold:
            return True

        return False

    def _detect_known_signal(self, signal: Dict[str, Any]) -> bool:
        """Detect known signal pattern.

        Args:
            signal: Current signal data

        Returns:
            True if known signal detected
        """
        # Check signal characteristics against known patterns
        if (signal["quality"] > self.thresholds.quality_threshold and
            signal["entropy"] < self.thresholds.entropy_threshold):
            return True

        return False

    def _calculate_signal_strength(self, signal: Dict[str, Any]) -> float:
        """Calculate signal strength score.

        Args:
            signal: Signal data

        Returns:
            Signal strength score (0-1)
        """
        rssi_norm = max(0, min(1, (signal["rssi"] + 120) / 90))
        lqi_norm = signal["lqi"] / 255
        return 0.7 * rssi_norm + 0.3 * lqi_norm

    def _calculate_entropy(self, signal: Dict[str, Any]) -> float:
        """Calculate signal entropy.

        Args:
            signal: Signal data

        Returns:
            Entropy score (0-1)
        """
        rssi_samples = signal["samples"]["rssi"]
        hist, _ = np.histogram(rssi_samples, bins=256, density=True)
        hist = hist[hist > 0]
        entropy = -np.sum(hist * np.log2(hist))
        return min(1.0, entropy / 8.0)

    def detect_anomalies(self, signal: Dict[str, Any]) -> List[AnomalyType]:
        """Detect anomalies in the signal.

        Args:
            signal: Signal data to analyze

        Returns:
            List of detected anomaly types
        """
        try:
            # Update signal history
            self.signal_history.append(signal)
            if len(self.signal_history) > self.history_size:
                self.signal_history.pop(0)

            # Detect anomalies
            anomalies = []

            if self._detect_ghost_echo(signal):
                anomalies.append(AnomalyType.GHOST_ECHO)

            if self._detect_void_pulse(signal):
                anomalies.append(AnomalyType.VOID_PULSE)

            if self._detect_static_burst(signal):
                anomalies.append(AnomalyType.STATIC_BURST)

            if self._detect_freq_shift(signal):
                anomalies.append(AnomalyType.FREQ_SHIFT)

            if self._detect_known_signal(signal):
                anomalies.append(AnomalyType.KNOWN_SIGNAL)

            return anomalies

        except (ValueError, KeyError, TypeError) as e:
            logger.error("Error detecting anomalies: %s", str(e))
            return []

def get_anomaly_engine(thresholds: Optional[AnomalyThresholds] = None) -> AnomalyEngine:
    """Get or create the global anomaly engine instance.

    Args:
        thresholds: Optional configuration thresholds

    Returns:
        AnomalyEngine instance
    """
    global _anomaly_engine
    if _anomaly_engine is None:
        _anomaly_engine = AnomalyEngine(thresholds)
    return _anomaly_engine

# Global instance
_anomaly_engine: Optional[AnomalyEngine] = None

