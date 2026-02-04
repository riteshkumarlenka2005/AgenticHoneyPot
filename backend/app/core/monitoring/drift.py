"""Agentic drift detection for monitoring agent behavior."""
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from dataclasses import dataclass, field
import statistics


@dataclass
class ResponseQualityMetrics:
    """Metrics for response quality assessment."""
    timestamp: datetime
    confidence_score: float
    coherence_score: float
    persona_consistency: float
    intelligence_extraction_rate: float


class DriftDetector:
    """
    Detects drift in agent performance and behavior.
    
    Monitors:
    - Response quality degradation
    - Confidence decay over time
    - Persona consistency
    - Intelligence extraction effectiveness
    """
    
    def __init__(
        self,
        window_size: int = 50,
        alert_threshold: float = 0.15
    ):
        """
        Initialize drift detector.
        
        Args:
            window_size: Number of recent interactions to consider
            alert_threshold: Threshold for drift alert (0-1)
        """
        self.window_size = window_size
        self.alert_threshold = alert_threshold
        self.metrics_history: List[ResponseQualityMetrics] = []
        self.baseline_metrics: Optional[Dict[str, float]] = None
        self.drift_alerts: List[Dict[str, Any]] = []
    
    def record_interaction(
        self,
        response: str,
        confidence: float,
        persona_maintained: bool,
        intelligence_extracted: int
    ):
        """
        Record an interaction for drift monitoring.
        
        Args:
            response: The generated response
            confidence: Confidence score (0-1)
            persona_maintained: Whether persona was maintained
            intelligence_extracted: Number of intelligence items extracted
        """
        metrics = ResponseQualityMetrics(
            timestamp=datetime.utcnow(),
            confidence_score=confidence,
            coherence_score=self._calculate_coherence(response),
            persona_consistency=1.0 if persona_maintained else 0.0,
            intelligence_extraction_rate=min(intelligence_extracted / 3.0, 1.0)
        )
        
        self.metrics_history.append(metrics)
        
        # Keep only recent history
        if len(self.metrics_history) > self.window_size * 2:
            self.metrics_history = self.metrics_history[-self.window_size:]
        
        # Set baseline after sufficient data
        if not self.baseline_metrics and len(self.metrics_history) >= 20:
            self._establish_baseline()
        
        # Check for drift
        if self.baseline_metrics:
            self._check_for_drift()
    
    def _calculate_coherence(self, response: str) -> float:
        """
        Calculate coherence score for a response.
        
        Simple heuristic based on response characteristics.
        """
        if not response:
            return 0.0
        
        score = 0.5  # Base score
        
        # Length appropriateness
        word_count = len(response.split())
        if 10 <= word_count <= 100:
            score += 0.2
        
        # Sentence structure
        sentences = response.split('.')
        if 1 <= len(sentences) <= 5:
            score += 0.2
        
        # Question presence (shows engagement)
        if '?' in response:
            score += 0.1
        
        return min(1.0, score)
    
    def _establish_baseline(self):
        """Establish baseline metrics from recent history."""
        recent = self.metrics_history[-20:]
        
        self.baseline_metrics = {
            "confidence": statistics.mean(m.confidence_score for m in recent),
            "coherence": statistics.mean(m.coherence_score for m in recent),
            "persona_consistency": statistics.mean(m.persona_consistency for m in recent),
            "intelligence_rate": statistics.mean(m.intelligence_extraction_rate for m in recent)
        }
    
    def _check_for_drift(self):
        """Check if current performance has drifted from baseline."""
        if len(self.metrics_history) < 10:
            return
        
        recent = self.metrics_history[-10:]
        
        current_metrics = {
            "confidence": statistics.mean(m.confidence_score for m in recent),
            "coherence": statistics.mean(m.coherence_score for m in recent),
            "persona_consistency": statistics.mean(m.persona_consistency for m in recent),
            "intelligence_rate": statistics.mean(m.intelligence_extraction_rate for m in recent)
        }
        
        # Calculate drift for each metric
        drifts = {}
        for key in self.baseline_metrics:
            baseline = self.baseline_metrics[key]
            current = current_metrics[key]
            
            if baseline > 0:
                drift = abs(baseline - current) / baseline
                drifts[key] = drift
        
        # Check if any metric has drifted significantly
        max_drift = max(drifts.values()) if drifts else 0.0
        
        if max_drift > self.alert_threshold:
            self._create_drift_alert(drifts, current_metrics)
    
    def _create_drift_alert(
        self,
        drifts: Dict[str, float],
        current_metrics: Dict[str, float]
    ):
        """Create a drift alert."""
        # Find metric with maximum drift
        max_drift_metric = max(drifts, key=drifts.get)
        
        alert = {
            "timestamp": datetime.utcnow(),
            "severity": "high" if drifts[max_drift_metric] > 0.3 else "medium",
            "metric": max_drift_metric,
            "drift_amount": drifts[max_drift_metric],
            "baseline_value": self.baseline_metrics[max_drift_metric],
            "current_value": current_metrics[max_drift_metric],
            "all_drifts": drifts,
            "recommendation": self._get_recommendation(max_drift_metric, drifts[max_drift_metric])
        }
        
        self.drift_alerts.append(alert)
    
    def _get_recommendation(self, metric: str, drift_amount: float) -> str:
        """Get recommendation based on drift."""
        if metric == "confidence":
            return "Agent confidence is declining. Consider reviewing detection models or retraining."
        elif metric == "coherence":
            return "Response coherence is degrading. Check LLM parameters or prompt templates."
        elif metric == "persona_consistency":
            return "Persona consistency is dropping. Review persona instructions and guardrails."
        elif metric == "intelligence_rate":
            return "Intelligence extraction is declining. Review extraction patterns and strategies."
        else:
            return "Monitor agent behavior and consider system reset if drift continues."
    
    def get_recent_alerts(self, hours: int = 24) -> List[Dict[str, Any]]:
        """Get drift alerts from the last N hours."""
        cutoff = datetime.utcnow() - timedelta(hours=hours)
        return [
            alert for alert in self.drift_alerts
            if alert["timestamp"] >= cutoff
        ]
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get overall health status of the agent."""
        if not self.baseline_metrics or len(self.metrics_history) < 10:
            return {
                "status": "initializing",
                "message": "Gathering baseline data"
            }
        
        recent = self.metrics_history[-10:]
        
        current_metrics = {
            "confidence": statistics.mean(m.confidence_score for m in recent),
            "coherence": statistics.mean(m.coherence_score for m in recent),
            "persona_consistency": statistics.mean(m.persona_consistency for m in recent),
            "intelligence_rate": statistics.mean(m.intelligence_extraction_rate for m in recent)
        }
        
        # Calculate overall health score
        health_score = statistics.mean(current_metrics.values())
        
        # Determine status
        if health_score >= 0.8:
            status = "healthy"
        elif health_score >= 0.6:
            status = "degraded"
        elif health_score >= 0.4:
            status = "concerning"
        else:
            status = "critical"
        
        recent_alerts = self.get_recent_alerts(hours=1)
        
        return {
            "status": status,
            "health_score": health_score,
            "current_metrics": current_metrics,
            "baseline_metrics": self.baseline_metrics,
            "recent_alerts": len(recent_alerts),
            "total_interactions": len(self.metrics_history)
        }
    
    def reset_baseline(self):
        """Reset baseline metrics (e.g., after system update)."""
        self.baseline_metrics = None
        self.drift_alerts = []
        
        # Re-establish baseline from recent history if enough data
        if len(self.metrics_history) >= 20:
            self._establish_baseline()
