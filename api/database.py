"""
Database configuration and session management for Bank of Canada MLOps Platform
"""

from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine, async_sessionmaker
from sqlalchemy.orm import DeclarativeBase, Session
from sqlalchemy import create_engine
import logging
from contextlib import asynccontextmanager
from typing import AsyncGenerator
import redis
import asyncio

from config import settings, DatabaseConfig

logger = logging.getLogger(__name__)


class Base(DeclarativeBase):
    """Base class for all database models"""
    pass


# Database engines
engine = create_async_engine(
    settings.DATABASE_URL.replace("postgresql://", "postgresql+asyncpg://"),
    **DatabaseConfig.get_connection_params()
)

sync_engine = create_engine(
    settings.DATABASE_URL,
    **DatabaseConfig.get_connection_params()
)

# Session factories
AsyncSessionLocal = async_sessionmaker(
    engine, 
    class_=AsyncSession, 
    expire_on_commit=False
)

SessionLocal = async_sessionmaker(sync_engine)

# Redis connection
redis_client = redis.Redis.from_url(
    settings.REDIS_URL,
    decode_responses=True,
    socket_connect_timeout=5,
    socket_timeout=5,
    retry_on_timeout=True,
    health_check_interval=30
)


async def init_db():
    """Initialize the database with all tables"""
    try:
        # Import all models to register them
        from models import (
            economic_data_models,
            ml_models,
            user_models,
            monitoring_models
        )
        
        async with engine.begin() as conn:
            # Create all tables
            await conn.run_sync(Base.metadata.create_all)
        
        logger.info("Database initialized successfully")
        
        # Create default data
        await create_default_data()
        
    except Exception as e:
        logger.error(f"Database initialization failed: {e}")
        raise


async def create_default_data():
    """Create default data for the application"""
    try:
        async with AsyncSessionLocal() as session:
            from models.user_models import User, Role
            from services.auth_service import AuthService
            
            # Create default roles
            roles_data = [
                {"name": "admin", "description": "Full system access"},
                {"name": "economist", "description": "Economic data and model access"},
                {"name": "analyst", "description": "Read-only access to reports"},
                {"name": "viewer", "description": "Dashboard viewing only"}
            ]
            
            for role_data in roles_data:
                existing_role = await session.get(Role, role_data["name"])
                if not existing_role:
                    role = Role(**role_data)
                    session.add(role)
            
            # Create default admin user
            auth_service = AuthService()
            admin_exists = await auth_service.get_user_by_email("admin@bankcanada.ca")
            if not admin_exists:
                await auth_service.create_user(
                    email="admin@bankcanada.ca",
                    username="admin",
                    password="admin123",  # Change in production
                    role_name="admin",
                    first_name="System",
                    last_name="Administrator"
                )
            
            await session.commit()
            logger.info("Default data created successfully")
            
    except Exception as e:
        logger.error(f"Failed to create default data: {e}")


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """Dependency to get database session"""
    async with AsyncSessionLocal() as session:
        try:
            yield session
        except Exception as e:
            logger.error(f"Database session error: {e}")
            await session.rollback()
            raise
        finally:
            await session.close()


async def get_redis() -> redis.Redis:
    """Get Redis client"""
    return redis_client


class DatabaseHealthCheck:
    """Database health monitoring"""
    
    @staticmethod
    async def check_postgres() -> dict:
        """Check PostgreSQL connection and performance"""
        try:
            async with AsyncSessionLocal() as session:
                result = await session.execute("SELECT 1")
                return {
                    "status": "healthy",
                    "response_time_ms": "calculate_response_time()",
                    "connection_pool": {
                        "size": engine.pool.size(),
                        "checked_in": engine.pool.checkedin(),
                        "checked_out": engine.pool.checkedout()
                    }
                }
        except Exception as e:
            logger.error(f"PostgreSQL health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}
    
    @staticmethod
    async def check_redis() -> dict:
        """Check Redis connection and performance"""
        try:
            await redis_client.ping()
            info = await redis_client.info()
            return {
                "status": "healthy",
                "memory_usage": info.get("used_memory_human"),
                "connected_clients": info.get("connected_clients"),
                "uptime_seconds": info.get("uptime_in_seconds")
            }
        except Exception as e:
            logger.error(f"Redis health check failed: {e}")
            return {"status": "unhealthy", "error": str(e)}


class TransactionManager:
    """Context manager for database transactions"""
    
    def __init__(self, session: AsyncSession):
        self.session = session
    
    async def __aenter__(self):
        return self.session
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        if exc_type:
            await self.session.rollback()
        else:
            await self.session.commit()


@asynccontextmanager
async def get_transaction() -> AsyncGenerator[AsyncSession, None]:
    """Get a database session with automatic transaction management"""
    async with AsyncSessionLocal() as session:
        async with TransactionManager(session) as tx_session:
            yield tx_session


class CacheManager:
    """Redis cache management utilities"""
    
    @staticmethod
    async def get(key: str) -> str:
        """Get value from cache"""
        try:
            return await redis_client.get(key)
        except Exception as e:
            logger.error(f"Cache get error: {e}")
            return None
    
    @staticmethod
    async def set(key: str, value: str, expire: int = 3600) -> bool:
        """Set value in cache with expiration"""
        try:
            return await redis_client.setex(key, expire, value)
        except Exception as e:
            logger.error(f"Cache set error: {e}")
            return False
    
    @staticmethod
    async def delete(key: str) -> bool:
        """Delete key from cache"""
        try:
            return await redis_client.delete(key)
        except Exception as e:
            logger.error(f"Cache delete error: {e}")
            return False
    
    @staticmethod
    async def clear_pattern(pattern: str) -> int:
        """Clear all keys matching pattern"""
        try:
            keys = await redis_client.keys(pattern)
            if keys:
                return await redis_client.delete(*keys)
            return 0
        except Exception as e:
            logger.error(f"Cache clear pattern error: {e}")
            return 0
