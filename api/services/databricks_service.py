"""
Databricks SQL and compute service integration
"""

import logging
import os
from typing import Optional, Dict, Any, List
import pandas as pd

logger = logging.getLogger(__name__)

class DatabricksService:
    """Service for Databricks SQL and compute operations"""
    
    def __init__(self):
        self.logger = logging.getLogger(__name__)
        self.host = os.getenv("DATABRICKS_HOST")
        self.token = os.getenv("DATABRICKS_TOKEN") 
        self.warehouse_id = os.getenv("DATABRICKS_SQL_WAREHOUSE_ID")
        self.connection = None
        self.workspace_client = None
        
    async def connect(self):
        """Establish connection to Databricks"""
        try:
            if not self.token:
                self.logger.warning("No Databricks token provided - using fallback mode")
                return False
            
            # Import here to avoid issues if databricks packages not installed
            try:
                from databricks import sql
                from databricks.sdk import WorkspaceClient
            except ImportError as e:
                self.logger.error(f"Databricks packages not installed: {e}")
                return False
                
            self.connection = sql.connect(
                server_hostname=self.host,
                http_path=f"/sql/1.0/warehouses/{self.warehouse_id}",
                access_token=self.token
            )
            
            self.workspace_client = WorkspaceClient(
                host=f"https://{self.host}",
                token=self.token
            )
            
            self.logger.info("Successfully connected to Databricks")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to connect to Databricks: {e}")
            return False
    
    async def execute_query(self, query: str) -> Optional[pd.DataFrame]:
        """Execute SQL query and return DataFrame"""
        try:
            if not self.connection:
                await self.connect()
                
            if not self.connection:
                return None
                
            cursor = self.connection.cursor()
            cursor.execute(query)
            
            # Fetch results and convert to DataFrame
            columns = [desc[0] for desc in cursor.description]
            data = cursor.fetchall()
            
            return pd.DataFrame(data, columns=columns)
            
        except Exception as e:
            self.logger.error(f"Query execution failed: {e}")
            return None
    
    async def create_table_if_not_exists(self, table_name: str, schema: Dict[str, str]):
        """Create table with given schema if it doesn't exist"""
        try:
            columns = []
            for col_name, col_type in schema.items():
                columns.append(f"{col_name} {col_type}")
            
            create_query = f"""
            CREATE TABLE IF NOT EXISTS {table_name} (
                {', '.join(columns)}
            ) USING DELTA
            """
            
            result = await self.execute_query(create_query)
            self.logger.info(f"Table {table_name} ready")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to create table {table_name}: {e}")
            return False
    
    async def insert_dataframe(self, table_name: str, df: pd.DataFrame):
        """Insert DataFrame into Databricks table"""
        try:
            if df.empty:
                self.logger.warning("Empty DataFrame provided for insert")
                return False
            
            # Convert DataFrame to SQL INSERT statements
            # In production, you'd use more efficient bulk insert methods
            placeholders = ', '.join(['?' for _ in df.columns])
            columns = ', '.join(df.columns)
            
            insert_query = f"INSERT INTO {table_name} ({columns}) VALUES ({placeholders})"
            
            cursor = self.connection.cursor()
            for _, row in df.iterrows():
                cursor.execute(insert_query, tuple(row))
            
            self.logger.info(f"Inserted {len(df)} rows into {table_name}")
            return True
            
        except Exception as e:
            self.logger.error(f"Failed to insert data into {table_name}: {e}")
            return False
    
    def close(self):
        """Close Databricks connection"""
        if self.connection:
            self.connection.close()
