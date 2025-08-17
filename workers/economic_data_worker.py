"""
Economic Data Background Worker

This worker handles:
- Periodic data ingestion from Bank of Canada APIs
- Data quality monitoring and validation
- Model retraining triggers
- Alert generation for anomalies
"""

import os
import time
import logging
import asyncio
from datetime import datetime, timedelta
from typing import List, Dict, Any
import requests
import pandas as pd
import psycopg2
import redis
import json

# Setup logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

class EconomicDataWorker:
    """Background worker for economic data processing"""
    
    def __init__(self):
        self.db_url = os.getenv('DATABASE_URL')
        self.redis_url = os.getenv('REDIS_URL') 
        self.api_url = os.getenv('BANK_CANADA_API_URL', 'https://www.bankofcanada.ca/valet/')
        
        # Economic indicators to monitor
        self.indicators = [
            'CPIXCORE',  # Core CPI
            'CPIX',      # Total CPI
            'UNRATE',    # Unemployment rate
            'GDP',       # GDP
            'POLRATE',   # Policy rate
            'FXUSDCAD'   # USD/CAD exchange rate
        ]
        
        # Setup connections
        self.setup_connections()
    
    def setup_connections(self):
        """Setup database and Redis connections"""
        try:
            # Redis connection
            self.redis_client = redis.from_url(self.redis_url)
            logger.info("Connected to Redis")
            
            # Test database connection
            conn = psycopg2.connect(self.db_url)
            conn.close()
            logger.info("Database connection verified")
            
        except Exception as e:
            logger.error(f"Failed to setup connections: {e}")
            raise
    
    def fetch_bank_canada_data(self, series_code: str) -> Dict[str, Any]:
        """Fetch data from Bank of Canada API"""
        try:
            url = f"{self.api_url}observations/{series_code}/json"
            params = {
                'recent': 10,  # Get last 10 observations
                'order_dir': 'desc'
            }
            
            response = requests.get(url, params=params, timeout=30)
            response.raise_for_status()
            
            data = response.json()
            observations = data.get('observations', [])
            
            logger.info(f"Fetched {len(observations)} observations for {series_code}")
            return {
                'series_code': series_code,
                'observations': observations,
                'fetched_at': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Failed to fetch data for {series_code}: {e}")
            return {
                'series_code': series_code,
                'observations': [],
                'error': str(e),
                'fetched_at': datetime.now().isoformat()
            }
    
    def validate_data_quality(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate data quality and detect anomalies"""
        series_code = data['series_code']
        observations = data['observations']
        
        if not observations:
            return {
                'series_code': series_code,
                'quality_score': 0.0,
                'issues': ['No data available'],
                'status': 'failed'
            }
        
        issues = []
        quality_score = 1.0
        
        # Check for missing values
        missing_count = sum(1 for obs in observations if not obs.get('v'))
        if missing_count > 0:
            issues.append(f"{missing_count} missing values")
            quality_score -= 0.2
        
        # Check data freshness
        latest_date = observations[0].get('d') if observations else None
        if latest_date:
            latest_dt = datetime.fromisoformat(latest_date)
            days_old = (datetime.now() - latest_dt).days
            if days_old > 30:
                issues.append(f"Data is {days_old} days old")
                quality_score -= 0.3
        
        # Check for outliers (simple check)
        values = [float(obs['v']) for obs in observations if obs.get('v')]
        if len(values) > 3:
            mean_val = sum(values) / len(values)
            std_val = (sum((x - mean_val) ** 2 for x in values) / len(values)) ** 0.5
            outliers = [v for v in values if abs(v - mean_val) > 3 * std_val]
            if outliers:
                issues.append(f"{len(outliers)} potential outliers detected")
                quality_score -= 0.1
        
        return {
            'series_code': series_code,
            'quality_score': max(0.0, quality_score),
            'issues': issues,
            'status': 'passed' if quality_score > 0.7 else 'warning' if quality_score > 0.4 else 'failed',
            'validated_at': datetime.now().isoformat()
        }
    
    def store_data_in_cache(self, series_code: str, data: Dict[str, Any]):
        """Store processed data in Redis cache"""
        try:
            cache_key = f"economic_data:{series_code}"
            self.redis_client.setex(
                cache_key, 
                3600,  # 1 hour expiry
                json.dumps(data)
            )
            logger.info(f"Cached data for {series_code}")
        except Exception as e:
            logger.error(f"Failed to cache data for {series_code}: {e}")
    
    def check_alert_conditions(self, series_code: str, quality_result: Dict[str, Any]):
        """Check if alerts should be triggered"""
        alerts = []
        
        # Data quality alerts
        if quality_result['quality_score'] < 0.5:
            alerts.append({
                'type': 'data_quality',
                'severity': 'high',
                'message': f"Poor data quality for {series_code}: {quality_result['issues']}",
                'series_code': series_code,
                'timestamp': datetime.now().isoformat()
            })
        
        # Store alerts in Redis for API to pick up
        if alerts:
            alert_key = f"alerts:{series_code}:{int(time.time())}"
            self.redis_client.setex(alert_key, 86400, json.dumps(alerts))  # 24 hour expiry
            logger.warning(f"Generated {len(alerts)} alerts for {series_code}")
    
    def process_indicator(self, series_code: str):
        """Process a single economic indicator"""
        logger.info(f"Processing indicator: {series_code}")
        
        try:
            # Fetch data
            raw_data = self.fetch_bank_canada_data(series_code)
            
            # Validate quality
            quality_result = self.validate_data_quality(raw_data)
            
            # Store in cache
            processed_data = {
                'raw_data': raw_data,
                'quality_result': quality_result,
                'processed_at': datetime.now().isoformat()
            }
            self.store_data_in_cache(series_code, processed_data)
            
            # Check for alerts
            self.check_alert_conditions(series_code, quality_result)
            
            logger.info(f"Successfully processed {series_code} - Quality: {quality_result['quality_score']:.2f}")
            
        except Exception as e:
            logger.error(f"Failed to process {series_code}: {e}")
    
    async def run_periodic_tasks(self):
        """Run periodic data ingestion and monitoring"""
        logger.info("Starting periodic data processing...")
        
        while True:
            try:
                start_time = time.time()
                
                # Process all indicators
                for indicator in self.indicators:
                    self.process_indicator(indicator)
                    # Small delay between indicators to be nice to the API
                    await asyncio.sleep(2)
                
                # Log processing stats
                processing_time = time.time() - start_time
                logger.info(f"Completed processing cycle in {processing_time:.2f} seconds")
                
                # Store processing stats
                stats = {
                    'indicators_processed': len(self.indicators),
                    'processing_time': processing_time,
                    'timestamp': datetime.now().isoformat()
                }
                self.redis_client.setex('worker_stats', 3600, json.dumps(stats))
                
                # Wait 5 minutes before next cycle
                await asyncio.sleep(300)
                
            except Exception as e:
                logger.error(f"Error in processing cycle: {e}")
                await asyncio.sleep(60)  # Wait 1 minute before retrying
    
    def run(self):
        """Main worker entry point"""
        logger.info("Economic Data Worker starting...")
        
        try:
            # Run the async event loop
            asyncio.run(self.run_periodic_tasks())
        except KeyboardInterrupt:
            logger.info("Worker stopped by user")
        except Exception as e:
            logger.error(f"Worker failed: {e}")
            raise

if __name__ == "__main__":
    worker = EconomicDataWorker()
    worker.run()
