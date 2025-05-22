import time
import logging
from typing import Dict, List, Optional
from dataclasses import dataclass
from enum import Enum
import math

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger('RFGhost')

class AnomalyType(Enum):
    GHOST_ECHO = "Ghost Echo"  # High RSSI, high entropy
    VOID_PULSE = "Void Pulse"  # Very low RSSI, high entropy
    STATIC_BURST = "Static Burst"  # Long duration, high entropy
    FREQUENCY_SHIFT = "Frequency Shift"  # Rapid frequency changes
    SIGNAL_PATTERN = "Signal Pattern"  # Repeating patterns
    UNKNOWN = "Unknown Anomaly"

@dataclass
class AnomalyThresholds:
    rssi_high: int = -50  # dBm
    rssi_low: int = -90   # dBm
    entropy_threshold: float = 0.8  # 80%
    duration_threshold: float = 2.0  # seconds
    pattern_threshold: float = 0.7  # 70% similarity

class AnomalyEngine:
    def __init__(self, thresholds: Optional[AnomalyThresholds] = None):
        """Initialize the anomaly detection engine with configurable thresholds."""
        self.thresholds = thresholds or AnomalyThresholds()
        self.history: List[Dict] = []
        self.history_size = 100  # Keep last 100 signals for pattern analysis
        
    def _calculate_signal_strength(self, rssi: int) -> float:
        """Convert RSSI to a normalized signal strength (0-1)."""
        # RSSI typically ranges from -120 to -30 dBm
        return max(0, min(1, (rssi + 120) / 90))
        
    def _detect_ghost_echo(self, signal: Dict) -> Optional[Dict]:
        """Detect strong, high-entropy signals (potential intentional transmissions)."""
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
        
    def _detect_void_pulse(self, signal: Dict) -> Optional[Dict]:
        """Detect very weak but high-entropy signals (potential hidden transmissions)."""
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
        
    def _detect_static_burst(self, signal: Dict) -> Optional[Dict]:
        """Detect long-duration, high-entropy signals (potential jamming or interference)."""
        if (signal["duration"] > self.thresholds.duration_threshold and 
            signal["entropy"] > self.thresholds.entropy_threshold):
            return {
                "type": AnomalyType.STATIC_BURST,
                "confidence": min(1.0, signal["duration"] / 5.0),  # Cap at 5 seconds
                "details": {
                    "duration": signal["duration"],
                    "entropy": signal["entropy"],
                    "frequency": signal["frequency"]
                }
            }
        return None
        
    def _detect_frequency_shift(self, signal: Dict) -> Optional[Dict]:
        """Detect rapid frequency changes in recent history."""
        if len(self.history) < 2:
            return None
            
        last_signal = self.history[-1]
        freq_diff = abs(signal["frequency"] - last_signal["frequency"])
        
        if freq_diff > 1.0:  # More than 1 MHz change
            return {
                "type": AnomalyType.FREQUENCY_SHIFT,
                "confidence": min(1.0, freq_diff / 10.0),  # Cap at 10 MHz
                "details": {
                    "from_freq": last_signal["frequency"],
                    "to_freq": signal["frequency"],
                    "shift": freq_diff
                }
            }
        return None
        
    def _detect_signal_pattern(self, signal: Dict) -> Optional[Dict]:
        """Detect repeating patterns in signal history."""
        if len(self.history) < 5:
            return None
            
        # Look for similar RSSI patterns
        pattern_length = min(5, len(self.history))
        recent_signals = self.history[-pattern_length:]
        
        # Calculate pattern similarity
        rssi_pattern = [s["rssi"] for s in recent_signals]
        similarity = self._calculate_pattern_similarity(rssi_pattern)
        
        if similarity > self.thresholds.pattern_threshold:
            return {
                "type": AnomalyType.SIGNAL_PATTERN,
                "confidence": similarity,
                "details": {
                    "pattern_length": pattern_length,
                    "similarity": similarity,
                    "frequency": signal["frequency"]
                }
            }
        return None
        
    def _calculate_pattern_similarity(self, pattern: List[int]) -> float:
        """Calculate similarity score for a pattern of RSSI values."""
        if len(pattern) < 2:
            return 0.0
            
        # Calculate differences between consecutive values
        diffs = [abs(pattern[i] - pattern[i-1]) for i in range(1, len(pattern))]
        
        # Calculate standard deviation of differences
        mean_diff = sum(diffs) / len(diffs)
        variance = sum((d - mean_diff) ** 2 for d in diffs) / len(diffs)
        std_dev = math.sqrt(variance)
        
        # Lower standard deviation means more similar pattern
        return max(0.0, 1.0 - (std_dev / 20.0))  # Normalize to 0-1
        
    def detect_anomalies(self, signal: Dict) -> List[Dict]:
        """Analyze a signal for various types of anomalies."""
        anomalies = []
        
        # Update history
        self.history.append(signal)
        if len(self.history) > self.history_size:
            self.history.pop(0)
            
        # Run all detection methods
        detection_methods = [
            self._detect_ghost_echo,
            self._detect_void_pulse,
            self._detect_static_burst,
            self._detect_frequency_shift,
            self._detect_signal_pattern
        ]
        
        for detector in detection_methods:
            anomaly = detector(signal)
            if anomaly:
                anomalies.append(anomaly)
                
        return anomalies

def get_anomaly_engine(thresholds: Optional[AnomalyThresholds] = None) -> AnomalyEngine:
    """Get or create the anomaly detection engine singleton."""
    global _anomaly_engine
    if not hasattr(get_anomaly_engine, '_anomaly_engine'):
        get_anomaly_engine._anomaly_engine = AnomalyEngine(thresholds)
    return get_anomaly_engine._anomaly_engine

def detect_anomalies(signal: Dict, thresholds: Optional[AnomalyThresholds] = None) -> List[Dict]:
    """Public interface for anomaly detection."""
    engine = get_anomaly_engine(thresholds)
    return engine.detect_anomalies(signal)
