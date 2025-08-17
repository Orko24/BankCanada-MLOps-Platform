"""
Databricks credit monitoring service
"""

import logging
import os
from typing import Dict, Any, List
import asyncio

logger = logging.getLogger(__name__)

class CreditMonitorService:
    """Monitor Databricks credit usage and trigger fallbacks"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.threshold = float(os.getenv("DATABRICKS_CREDIT_THRESHOLD", "80"))
        self.workspace_client = None
        self.credit_usage = 0.0
        self.fallback_mode = False
        self.monthly_limit = 100.0  # Default monthly credit limit
    
    async def check_credit_usage(self) -> Dict[str, Any]:
        """Check current credit usage percentage"""
        try:
            # In real implementation, you'd call Databricks billing API
            # For now, simulate credit checking
            # This would be: self.workspace_client.billing.get_usage()
            
            usage_data = {
                "usage_percent": self.credit_usage,
                "credits_used": self.credit_usage * self.monthly_limit / 100,
                "monthly_limit": self.monthly_limit,
                "fallback_mode": self.fallback_mode,
                "threshold": self.threshold,
                "status": "monitoring"
            }
            
            # Trigger fallback if over threshold
            if self.credit_usage >= self.threshold:
                if not self.fallback_mode:
                    self.fallback_mode = True
                    self.logger.warning(f"Credit usage {self.credit_usage}% exceeds threshold {self.threshold}%. Activating fallback mode.")
            else:
                if self.fallback_mode:
                    self.fallback_mode = False
                    self.logger.info(f"Credit usage {self.credit_usage}% below threshold. Deactivating fallback mode.")
            
            return usage_data
            
        except Exception as e:
            self.logger.error(f"Credit monitoring failed: {e}")
            return {"usage_percent": 100, "fallback_mode": True, "error": str(e)}
    
    async def simulate_credit_usage(self, usage_percent: float):
        """Manually set credit usage for testing"""
        self.credit_usage = max(0, min(100, usage_percent))
        await self.check_credit_usage()
        self.logger.info(f"Simulated credit usage set to {self.credit_usage}%")
    
    def is_fallback_mode(self) -> bool:
        """Check if we're in fallback mode"""
        return self.fallback_mode
    
    def reset_fallback(self):
        """Reset fallback mode (for testing or manual override)"""
        self.fallback_mode = False
        self.credit_usage = 0.0
        self.logger.info("Fallback mode reset")
    
    async def get_recommendations(self) -> List[str]:
        """Get cost optimization recommendations"""
        recommendations = []
        
        if self.credit_usage > 90:
            recommendations.append("Critical: Consider pausing non-essential workloads")
        elif self.credit_usage > 75:
            recommendations.append("Warning: Approaching credit limit - optimize queries")
        elif self.credit_usage > 50:
            recommendations.append("Monitor: Track usage more frequently")
        else:
            recommendations.append("Normal: Usage within expected range")
        
        return recommendations
