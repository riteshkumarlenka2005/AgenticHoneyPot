"""Model Drift Detection System."""
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from collections import deque
import statistics


class DriftMetric:
    """Metric for tracking drift."""

    def __init__(self, name: str, baseline: float, threshold: float):
        """
        Initialize drift metric.
        
        Args:
            name: Metric name
            baseline: Baseline value
            threshold: Drift threshold (percentage)
        """
        self.name = name
        self.baseline = baseline
        self.threshold = threshold
        self.current_value: Optional[float] = None
        self.drift_detected = False
        self.drift_percentage = 0.0

    def update(self, value: float) -> bool:
        """
        Update metric and check for drift.
        
        Args:
            value: New metric value
            
        Returns:
            True if drift detected
        """
        self.current_value = value
        
        if self.baseline > 0:
            self.drift_percentage = abs((value - self.baseline) / self.baseline) * 100
            self.drift_detected = self.drift_percentage > self.threshold
        else:
            self.drift_detected = False
        
        return self.drift_detected

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary."""
        return {
            "name": self.name,
            "baseline": self.baseline,
            "current_value": self.current_value,
            "drift_percentage": round(self.drift_percentage, 2),
            "drift_detected": self.drift_detected,
            "threshold": self.threshold
        }


class DriftDetector:
    """
    Detect model performance drift and confidence decay.
    
    Monitors:
    - Detection accuracy
    - Confidence levels
    - Intelligence extraction rate
    - Response effectiveness
    """

    def __init__(self, baseline_window: int = 100, alert_threshold: float = 20.0):
        """
        Initialize drift detector.
        
        Args:
            baseline_window: Number of samples for baseline calculation
            alert_threshold: Percentage change to trigger alert
        """
        self.baseline_window = baseline_window
        self.alert_threshold = alert_threshold
        
        # Metric tracking
        self.metrics: Dict[str, DriftMetric] = {}
        
        # Historical data (limited window)
        self.detection_accuracy_history = deque(maxlen=baseline_window)
        self.confidence_history = deque(maxlen=baseline_window)
        self.extraction_rate_history = deque(maxlen=baseline_window)
        
        # Baseline values
        self.baselines: Dict[str, float] = {}
        self.baseline_calculated = False
        
        # Alerts
        self.alerts: List[Dict[str, Any]] = []
        self.last_alert_time: Optional[datetime] = None

    def add_sample(
        self,
        detection_accuracy: float,
        confidence: float,
        extraction_rate: float
    ) -> None:
        """
        Add new sample for drift detection.
        
        Args:
            detection_accuracy: Accuracy of scam detection (0-1)
            confidence: Average confidence score (0-1)
            extraction_rate: Intelligence extraction rate
        """
        self.detection_accuracy_history.append(detection_accuracy)
        self.confidence_history.append(confidence)
        self.extraction_rate_history.append(extraction_rate)
        
        # Calculate baseline if enough samples
        if not self.baseline_calculated and len(self.detection_accuracy_history) >= 30:
            self._calculate_baseline()

    def _calculate_baseline(self) -> None:
        """Calculate baseline metrics from historical data."""
        if len(self.detection_accuracy_history) >= 30:
            self.baselines["detection_accuracy"] = statistics.mean(
                list(self.detection_accuracy_history)[:30]
            )
            self.baselines["confidence"] = statistics.mean(
                list(self.confidence_history)[:30]
            )
            self.baselines["extraction_rate"] = statistics.mean(
                list(self.extraction_rate_history)[:30]
            )
            
            # Initialize metrics
            self.metrics["detection_accuracy"] = DriftMetric(
                "Detection Accuracy",
                self.baselines["detection_accuracy"],
                self.alert_threshold
            )
            self.metrics["confidence"] = DriftMetric(
                "Confidence Score",
                self.baselines["confidence"],
                self.alert_threshold
            )
            self.metrics["extraction_rate"] = DriftMetric(
                "Extraction Rate",
                self.baselines["extraction_rate"],
                self.alert_threshold
            )
            
            self.baseline_calculated = True

    def check_drift(self) -> Dict[str, Any]:
        """
        Check for drift in recent data.
        
        Returns:
            Drift analysis report
        """
        if not self.baseline_calculated:
            return {
                "status": "insufficient_data",
                "message": "Need at least 30 samples to establish baseline",
                "samples_collected": len(self.detection_accuracy_history)
            }
        
        # Calculate recent averages (last 10 samples)
        recent_window = min(10, len(self.detection_accuracy_history))
        
        recent_accuracy = statistics.mean(
            list(self.detection_accuracy_history)[-recent_window:]
        )
        recent_confidence = statistics.mean(
            list(self.confidence_history)[-recent_window:]
        )
        recent_extraction = statistics.mean(
            list(self.extraction_rate_history)[-recent_window:]
        )
        
        # Update metrics and check for drift
        drift_detected = False
        drift_detected |= self.metrics["detection_accuracy"].update(recent_accuracy)
        drift_detected |= self.metrics["confidence"].update(recent_confidence)
        drift_detected |= self.metrics["extraction_rate"].update(recent_extraction)
        
        # Generate alert if drift detected
        if drift_detected:
            self._generate_alert()
        
        return {
            "status": "drift_detected" if drift_detected else "normal",
            "drift_detected": drift_detected,
            "metrics": {
                name: metric.to_dict()
                for name, metric in self.metrics.items()
            },
            "samples_analyzed": len(self.detection_accuracy_history),
            "recent_window": recent_window
        }

    def check_confidence_decay(
        self, confidence_values: List[float], window_size: int = 10
    ) -> Dict[str, Any]:
        """
        Check for confidence decay over time.
        
        Args:
            confidence_values: List of confidence values over time
            window_size: Window for trend analysis
            
        Returns:
            Confidence decay analysis
        """
        if len(confidence_values) < window_size:
            return {
                "status": "insufficient_data",
                "decay_detected": False
            }
        
        # Calculate trend (simple linear regression)
        recent = confidence_values[-window_size:]
        
        # Check if confidence is decreasing
        first_half = statistics.mean(recent[:window_size // 2])
        second_half = statistics.mean(recent[window_size // 2:])
        
        decay_rate = ((second_half - first_half) / first_half) * 100 if first_half > 0 else 0
        decay_detected = decay_rate < -10  # 10% decrease
        
        return {
            "status": "decay_detected" if decay_detected else "normal",
            "decay_detected": decay_detected,
            "decay_rate": round(decay_rate, 2),
            "first_half_avg": round(first_half, 3),
            "second_half_avg": round(second_half, 3),
            "samples_analyzed": len(recent)
        }

    def _generate_alert(self) -> None:
        """Generate drift alert."""
        current_time = datetime.utcnow()
        
        # Throttle alerts (max one per hour)
        if self.last_alert_time:
            time_since_last = current_time - self.last_alert_time
            if time_since_last < timedelta(hours=1):
                return
        
        alert = {
            "timestamp": current_time.isoformat(),
            "type": "model_drift",
            "severity": self._calculate_severity(),
            "metrics": {
                name: metric.to_dict()
                for name, metric in self.metrics.items()
                if metric.drift_detected
            },
            "message": self._generate_alert_message()
        }
        
        self.alerts.append(alert)
        self.last_alert_time = current_time

    def _calculate_severity(self) -> str:
        """Calculate alert severity."""
        max_drift = max(
            metric.drift_percentage
            for metric in self.metrics.values()
            if metric.drift_detected
        )
        
        if max_drift > 50:
            return "critical"
        elif max_drift > 30:
            return "high"
        elif max_drift > 20:
            return "medium"
        else:
            return "low"

    def _generate_alert_message(self) -> str:
        """Generate human-readable alert message."""
        drifted_metrics = [
            metric.name
            for metric in self.metrics.values()
            if metric.drift_detected
        ]
        
        if len(drifted_metrics) == 1:
            return f"Significant drift detected in {drifted_metrics[0]}"
        else:
            metrics_str = ", ".join(drifted_metrics)
            return f"Significant drift detected in multiple metrics: {metrics_str}"

    def get_alerts(self, since: Optional[datetime] = None) -> List[Dict[str, Any]]:
        """
        Get alerts, optionally filtered by time.
        
        Args:
            since: Only return alerts after this time
            
        Returns:
            List of alerts
        """
        if since is None:
            return self.alerts
        
        return [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert["timestamp"]) > since
        ]

    def reset_baseline(self) -> None:
        """Reset baseline and start fresh calibration."""
        self.detection_accuracy_history.clear()
        self.confidence_history.clear()
        self.extraction_rate_history.clear()
        self.baselines.clear()
        self.metrics.clear()
        self.baseline_calculated = False
        self.alerts.clear()

    def get_status(self) -> Dict[str, Any]:
        """
        Get current drift detector status.
        
        Returns:
            Status information
        """
        return {
            "baseline_calculated": self.baseline_calculated,
            "samples_collected": len(self.detection_accuracy_history),
            "baseline_window": self.baseline_window,
            "alert_threshold": self.alert_threshold,
            "baselines": self.baselines,
            "active_alerts": len([
                alert for alert in self.alerts
                if datetime.fromisoformat(alert["timestamp"]) > 
                   datetime.utcnow() - timedelta(hours=24)
            ])
        }
