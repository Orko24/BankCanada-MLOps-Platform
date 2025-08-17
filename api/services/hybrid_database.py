"""
Hybrid database service - Databricks primary, PostgreSQL fallback
"""

import logging
from typing import Optional, Dict, Any, List
import pandas as pd
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import text

from .databricks_service import DatabricksService
from .credit_monitor import CreditMonitorService
from database import get_db

logger = logging.getLogger(__name__)

class HybridDatabaseService:
    """Hybrid database service with smart routing"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.databricks = DatabricksService()
        self.credit_monitor = CreditMonitorService()
        self.databricks_available = False
    
    async def initialize(self):
        """Initialize both database connections"""
        try:
            self.databricks_available = await self.databricks.connect()
            await self.credit_monitor.check_credit_usage()
            self.logger.info(f"Hybrid database initialized - Databricks: {self.databricks_available}")
        except Exception as e:
            self.logger.error(f"Failed to initialize hybrid database: {e}")
            self.databricks_available = False
    
    async def execute_query(self, query: str, prefer_databricks: bool = True) -> Optional[pd.DataFrame]:
        """Execute query with intelligent routing"""
        try:
            # Check if we should use Databricks
            should_use_databricks = (
                prefer_databricks and 
                self.databricks_available and 
                not self.credit_monitor.is_fallback_mode()
            )
            
            if should_use_databricks:
                self.logger.info("Executing query on Databricks")
                result = await self.databricks.execute_query(query)
                if result is not None:
                    return result
                else:
                    self.logger.warning("Databricks query failed, falling back to PostgreSQL")
            
            # Fallback to PostgreSQL
            self.logger.info("Executing query on PostgreSQL fallback")
            return await self._execute_postgresql_query(query)
            
        except Exception as e:
            self.logger.error(f"Hybrid query execution failed: {e}")
            return None
    
    async def _execute_postgresql_query(self, query: str) -> Optional[pd.DataFrame]:
        """Execute query on PostgreSQL"""
        try:
            # Convert Databricks SQL to PostgreSQL compatible if needed
            pg_query = self._convert_to_postgresql(query)
            
            # Execute using SQLAlchemy
            async for db in get_db():
                result = await db.execute(text(pg_query))
                data = result.fetchall()
                if result.keys():
                    columns = list(result.keys())
                    return pd.DataFrame(data, columns=columns)
                else:
                    return pd.DataFrame()
                
        except Exception as e:
            self.logger.error(f"PostgreSQL query failed: {e}")
            return None
    
    def _convert_to_postgresql(self, databricks_query: str) -> str:
        """Convert Databricks-specific SQL to PostgreSQL compatible"""
        # Basic conversions - you'd expand this based on your needs
        pg_query = databricks_query
        
        # Example conversions:
        pg_query = pg_query.replace("USING DELTA", "")
        pg_query = pg_query.replace("OPTIMIZE", "-- OPTIMIZE not supported")
        pg_query = pg_query.replace("DESCRIBE EXTENDED", "SELECT column_name, data_type FROM information_schema.columns WHERE")
        
        return pg_query
    
    async def create_table(self, table_name: str, schema: Dict[str, str], prefer_databricks: bool = True):
        """Create table in appropriate database"""
        try:
            should_use_databricks = (
                prefer_databricks and 
                self.databricks_available and 
                not self.credit_monitor.is_fallback_mode()
            )
            
            if should_use_databricks:
                self.logger.info(f"Creating table {table_name} on Databricks")
                return await self.databricks.create_table_if_not_exists(table_name, schema)
            else:
                self.logger.info(f"Creating table {table_name} on PostgreSQL")
                return await self._create_postgresql_table(table_name, schema)
                
        except Exception as e:
            self.logger.error(f"Failed to create table {table_name}: {e}")
            return False
    
    async def _create_postgresql_table(self, table_name: str, schema: Dict[str, str]) -> bool:
        """Create table in PostgreSQL"""
        try:
            # Convert Databricks types to PostgreSQL types
            pg_schema = {}
            for col_name, col_type in schema.items():
                pg_type = self._convert_to_postgresql_type(col_type)
                pg_schema[col_name] = pg_type
            
            columns = []
            for col_name, col_type in pg_schema.items():
                columns.append(f"{col_name} {col_type}")
            
            create_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(columns)}
            )
            """
            
            async for db in get_db():
                await db.execute(text(create_query))
                await db.commit()
                
            self.logger.info(f"PostgreSQL table {table_name} created successfully")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create PostgreSQL table {table_name}: {e}")
            return False
    
    def _convert_to_postgresql_type(self, databricks_type: str) -> str:
        """Convert Databricks data types to PostgreSQL equivalents"""
        type_mapping = {
            "STRING": "TEXT",
            "BIGINT": "BIGINT", 
            "INT": "INTEGER",
            "DOUBLE": "DOUBLE PRECISION",
            "FLOAT": "REAL",
            "BOOLEAN": "BOOLEAN",
            "TIMESTAMP": "TIMESTAMP",
            "DATE": "DATE",
            "DECIMAL": "DECIMAL"
        }
        
        return type_mapping.get(databricks_type.upper(), "TEXT")
    
    async def get_status(self) -> Dict[str, Any]:
        """Get status of both database systems"""
        credit_status = await self.credit_monitor.check_credit_usage()
        
        return {
            "databricks": {
                "available": self.databricks_available,
                "fallback_mode": self.credit_monitor.is_fallback_mode(),
                "host": self.databricks.host
            },
            "postgresql": {
                "available": True,  # Assume always available locally
                "status": "fallback"
            },
            "credit_usage": credit_status,
            "active_database": "databricks" if (self.databricks_available and not self.credit_monitor.is_fallback_mode()) else "postgresql",
            "recommendations": await self.credit_monitor.get_recommendations()
        }
    
    async def simulate_credit_usage(self, usage_percent: float):
        """Simulate credit usage for testing"""
        await self.credit_monitor.simulate_credit_usage(usage_percent)
        return await self.get_status()
    
    def close(self):
        """Close all database connections"""
        if self.databricks:
            self.databricks.close()
