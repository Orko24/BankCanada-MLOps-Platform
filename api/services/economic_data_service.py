"""
Economic data service for fetching and processing economic indicators
Enhanced with Databricks integration and hybrid database support
"""

import logging
import asyncio
import pandas as pd
from typing import List, Optional, Dict, Any
from datetime import datetime, timedelta
import httpx

from .hybrid_database import HybridDatabaseService
from config import settings

logger = logging.getLogger(__name__)

class EconomicDataService:
    """Service for managing economic data operations with Databricks support"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.hybrid_db = HybridDatabaseService()
        self.bank_canada_url = settings.BANK_CANADA_API_URL
        self.indicators = settings.ECONOMIC_INDICATORS
    
    async def initialize(self):
        """Initialize the service and database connections"""
        await self.hybrid_db.initialize()
        await self._setup_economic_tables()
    
    async def _setup_economic_tables(self):
        """Setup economic data tables in the appropriate database"""
        try:
            # Economic indicators table schema
            indicators_schema = {
                "id": "BIGINT",
                "code": "STRING", 
                "name": "STRING",
                "description": "STRING",
                "unit": "STRING",
                "frequency": "STRING",
                "source": "STRING",
                "category": "STRING",
                "is_active": "BOOLEAN",
                "created_at": "TIMESTAMP",
                "updated_at": "TIMESTAMP"
            }
            
            # Economic data points table schema
            data_points_schema = {
                "id": "BIGINT",
                "indicator_id": "BIGINT",
                "date": "DATE",
                "value": "DOUBLE",
                "is_forecast": "BOOLEAN",
                "confidence_level": "DOUBLE",
                "revision_flag": "STRING",
                "quality_flag": "STRING",
                "created_at": "TIMESTAMP"
            }
            
            # Create tables
            await self.hybrid_db.create_table("economic_indicators", indicators_schema)
            await self.hybrid_db.create_table("economic_data_points", data_points_schema)
            
            self.logger.info("Economic data tables setup completed")
            
        except Exception as e:
            self.logger.error(f"Failed to setup economic tables: {e}")
    
    async def start_data_ingestion(self):
        """Start background data ingestion task"""
        self.logger.info("Starting economic data ingestion...")
        
        try:
            # Check database status
            status = await self.hybrid_db.get_status()
            self.logger.info(f"Database status: {status['active_database']}")
            
            # Start ingestion for each indicator
            for indicator in self.indicators:
                await self._ingest_indicator_data(indicator)
                await asyncio.sleep(1)  # Rate limiting
            
            self.logger.info("Economic data ingestion completed")
            return True
            
        except Exception as e:
            self.logger.error(f"Data ingestion failed: {e}")
            return False
    
    async def _ingest_indicator_data(self, indicator_code: str):
        """Ingest data for a specific economic indicator"""
        try:
            # Fetch data from Bank of Canada API
            data = await self._fetch_from_bank_canada(indicator_code)
            
            if data and len(data) > 0:
                # Convert to DataFrame for easier processing
                df = pd.DataFrame(data)
                
                # Use Databricks for large datasets, PostgreSQL for smaller ones
                prefer_databricks = len(df) > 1000  # Use Databricks for large datasets
                
                # Insert data using hybrid database
                query = self._build_insert_query("economic_data_points", df)
                await self.hybrid_db.execute_query(query, prefer_databricks=prefer_databricks)
                
                self.logger.info(f"Ingested {len(df)} records for {indicator_code}")
            else:
                self.logger.warning(f"No data available for {indicator_code}")
                
        except Exception as e:
            self.logger.error(f"Failed to ingest data for {indicator_code}: {e}")
    
    async def _fetch_from_bank_canada(self, indicator_code: str) -> List[Dict[str, Any]]:
        """Fetch data from Bank of Canada API"""
        try:
            # Mock data for now - replace with actual API call
            # In production: use httpx to call Bank of Canada Valet API
            mock_data = [
                {
                    "date": "2024-01-01",
                    "value": 3.25,
                    "indicator_code": indicator_code
                },
                {
                    "date": "2024-01-02", 
                    "value": 3.30,
                    "indicator_code": indicator_code
                }
            ]
            
            return mock_data
            
        except Exception as e:
            self.logger.error(f"Failed to fetch data from Bank of Canada API: {e}")
            return []
    
    def _build_insert_query(self, table_name: str, df: pd.DataFrame) -> str:
        """Build INSERT query for DataFrame"""
        if df.empty:
            return ""
        
        columns = ', '.join(df.columns)
        values_list = []
        
        for _, row in df.iterrows():
            values = []
            for value in row:
                if pd.isna(value):
                    values.append("NULL")
                elif isinstance(value, str):
                    values.append(f"'{value}'")
                else:
                    values.append(str(value))
            values_list.append(f"({', '.join(values)})")
        
        values_str = ', '.join(values_list)
        return f"INSERT INTO {table_name} ({columns}) VALUES {values_str}"
    
    async def fetch_indicator_data(self, indicator_code: str, start_date: Optional[datetime] = None, end_date: Optional[datetime] = None) -> Dict[str, Any]:
        """Fetch data for a specific economic indicator"""
        try:
            self.logger.info(f"Fetching data for indicator: {indicator_code}")
            
            # Build query with date filters
            query = f"""
            SELECT * FROM economic_data_points edp
            JOIN economic_indicators ei ON edp.indicator_id = ei.id
            WHERE ei.code = '{indicator_code}'
            """
            
            if start_date:
                query += f" AND edp.date >= '{start_date.strftime('%Y-%m-%d')}'"
            if end_date:
                query += f" AND edp.date <= '{end_date.strftime('%Y-%m-%d')}'"
            
            query += " ORDER BY edp.date DESC LIMIT 1000"
            
            # Execute query using hybrid database
            result_df = await self.hybrid_db.execute_query(query)
            
            if result_df is not None and not result_df.empty:
                return {
                    "indicator_code": indicator_code,
                    "status": "success",
                    "data_points": len(result_df),
                    "latest_date": result_df['date'].max() if 'date' in result_df.columns else None,
                    "data": result_df.to_dict('records')
                }
            else:
                return {"indicator_code": indicator_code, "status": "no_data", "data": []}
                
        except Exception as e:
            self.logger.error(f"Failed to fetch indicator data: {e}")
            return {"indicator_code": indicator_code, "status": "error", "error": str(e)}
    
    async def get_service_status(self) -> Dict[str, Any]:
        """Get economic data service status"""
        db_status = await self.hybrid_db.get_status()
        
        return {
            "service": "economic_data",
            "status": "operational",
            "database": db_status,
            "supported_indicators": len(self.indicators),
            "bank_canada_api": self.bank_canada_url
        }
