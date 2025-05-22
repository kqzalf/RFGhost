"""Anomaly detection engine for RF signal analysis.

This module implements various algorithms for detecting anomalies in RF signals,
including ghost echoes, void pulses, static bursts, and frequency shifts.
"""

import logging
from dataclasses import dataclass
from enum import Enum
from typing import Dict, List, Optional, Any, Callable

import numpy as np

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RFGhost')

class AnomalyType(Enum):
    """Types of RF anomalies that can be detected."""
    GHOST_ECHO = "ghost_echo"      # Strong, high-entropy signals
    VOID_PULSE = "void_pulse"      # Weak but high-entropy signals
    STATIC_BURST = "static_burst"  # Sudden bursts of static
    FREQ_SHIFT = "freq_shift"      # Unexpected frequency shifts
    PATTERN = "pattern"            # Known signal patterns

@dataclass
class AnomalyThresholds:
    """Configuration thresholds for anomaly detection."""
    rssi_high: int = -50  # dBm
    rssi_low: int = -90   # dBm
    entropy_threshold: float = 0.8  # 80%
    duration_threshold: float = 2.0  # seconds
    pattern_threshold: float = 0.7  # 70% similarity

class AnomalyEngine:
    """Engine for detecting anomalies in RF signals."""
    
    def __init__(self, thresholds: Optional[AnomalyThresholds] = None):
        """Initialize the anomaly detection engine.
        
        Args:
            thresholds: Configuration thresholds for detection
        """
        self.thresholds = thresholds or AnomalyThresholds()
        self.history: List[Dict[str, Any]] = []
        self.history_size = 100  # Keep last 100 signals for pattern analysis
        
    def _calculate_signal_strength(self, rssi: int) -> float:
        """Convert RSSI to a normalized signal strength (0-1).
        
        Args:
            rssi: Signal strength in dBm
            
        Returns:
            Normalized signal strength between 0 and 1
        """
        # RSSI typically ranges from -120 to -30 dBm
        return max(0, min(1, (rssi + 120) / 90))
        
    def _calculate_entropy(self, samples: List[int]) -> float:
        """Calculate Shannon entropy of signal samples.
        
        Args:
            samples: List of signal samples
            
        Returns:
            Entropy value between 0 and 1
        """
        if not samples:
            return 0.0
            
        # Convert to numpy array for efficient processing
        samples_array = np.array(samples)
        
        # Calculate histogram
        hist, _ = np.histogram(samples_array, bins=256, density=True)
        hist = hist[hist > 0]  # Remove zero bins
        
        # Calculate entropy
        entropy = -np.sum(hist * np.log2(hist))
        return min(1.0, entropy / 8.0)  # Normalize to 0-1 range
        
    def _detect_ghost_echo(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect strong, high-entropy signals (potential intentional transmissions).
        
        Args:
            signal: Signal data dictionary
            
        Returns:
            Anomaly dictionary if detected, None otherwise
        """
        if (signal["rssi"] > self.thresholds.rssi_high and 
            signal["entropy"] > self.thresholds.entropy_threshold):
            return {
                "type": AnomalyType.GHOST_ECHO,
                "confidence": self._calculate_signal_strength(signal["rssi"]),
                "details": {
                    "rssi": signal["rssi"],
                    "entropy": signal["entropy"],
                    "frequency": signal["frequency"]
                }
            }
        return None
        
    def _detect_void_pulse(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect very weak but high-entropy signals (potential hidden transmissions).
        
        Args:
            signal: Signal data dictionary
            
        Returns:
            Anomaly dictionary if detected, None otherwise
        """
        if (signal["rssi"] < self.thresholds.rssi_low and 
            signal["entropy"] > self.thresholds.entropy_threshold):
            return {
                "type": AnomalyType.VOID_PULSE,
                "confidence": 1 - self._calculate_signal_strength(signal["rssi"]),
                "details": {
                    "rssi": signal["rssi"],
                    "entropy": signal["entropy"],
                    "frequency": signal["frequency"]
                }
            }
        return None
        
    def _detect_static_burst(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect sudden bursts of static noise.
        
        Args:
            signal: Signal data dictionary
            
        Returns:
            Anomaly dictionary if detected, None otherwise
        """
        if len(self.history) < 2:
            return None
            
        prev_signal = self.history[-1]
        rssi_diff = abs(signal["rssi"] - prev_signal["rssi"])
        
        if (rssi_diff > 20 and  # Sudden change in signal strength
            signal["entropy"] > 0.9):  # High entropy indicates noise
            return {
                "type": AnomalyType.STATIC_BURST,
                "confidence": min(1.0, rssi_diff / 40.0),
                "details": {
                    "rssi_diff": rssi_diff,
                    "entropy": signal["entropy"],
                    "frequency": signal["frequency"]
                }
            }
        return None
        
    def _detect_frequency_shift(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect unexpected frequency shifts.
        
        Args:
            signal: Signal data dictionary
            
        Returns:
            Anomaly dictionary if detected, None otherwise
        """
        if len(self.history) < 2:
            return None
            
        prev_signal = self.history[-1]
        freq_diff = abs(signal["frequency"] - prev_signal["frequency"])
        
        if freq_diff > 0.1:  # More than 100 kHz shift
            return {
                "type": AnomalyType.FREQ_SHIFT,
                "confidence": min(1.0, freq_diff / 1.0),  # Normalize to 0-1
                "details": {
                    "freq_diff": freq_diff,
                    "old_freq": prev_signal["frequency"],
                    "new_freq": signal["frequency"]
                }
            }
        return None
        
    def _detect_signal_pattern(self, signal: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Detect known signal patterns.
        
        Args:
            signal: Signal data dictionary
            
        Returns:
            Anomaly dictionary if detected, None otherwise
        """
        if "pattern_match" in signal and signal["pattern_match"] > self.thresholds.pattern_threshold:
            return {
                "type": AnomalyType.PATTERN,
                "confidence": signal["pattern_match"],
                "details": {
                    "pattern_score": signal["pattern_match"],
                    "frequency": signal["frequency"]
                }
            }
        return None
        
    def detect_anomalies(self, signal: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Analyze a signal for various types of anomalies.
        
        Args:
            signal: Signal data dictionary
            
        Returns:
            List of detected anomalies
        """
        anomalies = []
        
        # Update history
        self.history.append(signal)
        if len(self.history) > self.history_size:
            self.history.pop(0)
            
        # Run all detection methods
        detection_methods: List[Callable[[Dict[str, Any]], Optional[Dict[str, Any]]]] = [
            self._detect_ghost_echo,
            self._detect_void_pulse,
            self._detect_static_burst,
            self._detect_frequency_shift,
            self._detect_signal_pattern
        ]
        
        for detector in detection_methods:
            try:
                anomaly = detector(signal)
                if anomaly:
                    anomalies.append(anomaly)
            except Exception as e:
                logger.error("Error in anomaly detection: %s", str(e))
                
        return anomalies

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
