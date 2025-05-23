"""Anomaly detection engine for RFGhost application."""
from typing import Dict, List, Optional, Tuple
import numpy as np
from logger import logger


class AnomalyEngine:
    """Engine for detecting anomalies in RF signals.

    This class implements various statistical methods to detect
    anomalies in RF signal patterns.
    """

    def __init__(self, threshold: float = 2.0) -> None:
        """Initialize the anomaly detection engine.

        Args:
            threshold: Standard deviation threshold for anomaly detection
        """
        self.threshold = threshold
        self.baseline: Optional[np.ndarray] = None
        self.logger = logger

    def set_baseline(self, data: List[float]) -> None:
        """Set the baseline data for anomaly detection.

        Args:
            data: List of baseline signal measurements
        """
        self.baseline = np.array(data)
        self.logger.info(f"Baseline set with {len(data)} samples")

    def detect_anomalies(self, data: List[float]) -> Tuple[List[bool], List[float]]:
        """Detect anomalies in the given signal data.

        Args:
            data: List of signal measurements to analyze

        Returns:
            Tuple containing:
            - List of boolean values indicating anomalies
            - List of anomaly scores
        """
        if self.baseline is None:
            self.logger.warning("No baseline set, using input data as baseline")
            self.set_baseline(data)

        signal = np.array(data)
        mean = np.mean(self.baseline)
        std = np.std(self.baseline)

        if std == 0:
            self.logger.warning("Zero standard deviation in baseline")
            return [False] * len(data), [0.0] * len(data)

        z_scores = np.abs((signal - mean) / std)
        anomalies = z_scores > self.threshold

        return anomalies.tolist(), z_scores.tolist()

    def get_statistics(self) -> Dict[str, float]:
        """Get current statistics of the baseline data.

        Returns:
            Dictionary containing statistical measures
        """
        if self.baseline is None:
            return self._get_empty_statistics()

        return {
            'mean': float(np.mean(self.baseline)),
            'std': float(np.std(self.baseline)),
            'min': float(np.min(self.baseline)),
            'max': float(np.max(self.baseline))
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
