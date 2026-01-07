# apps/agent_app/src/agenticAI_full_workflow/utils/db_manager.py
import os
from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver
from psycopg_pool import AsyncConnectionPool
from dotenv import load_dotenv
from shared_core.logger.logging import log

load_dotenv()

class DatabaseManager:
    def __init__(self):
        self.pool = None
        self.checkpointer = None
        self.uri = os.getenv("POSTGRES_URL")

    async def get_checkpointer(self):
        """
        Industry-Ready Checkpointer: Manages its own connection pool 
        to avoid 'PoolClosed' errors on Windows/Async environments.
        """
        if not self.uri:
            log.error("POSTGRES_URL not found in environment variables!")
            raise ValueError("POSTGRES_URL is missing in .env file")

        if self.checkpointer is None:
            try:
                # Manually manage the connection pool for persistent access
                # open=False is safer, we open it explicitly below
                # kwargs={"autocommit": True} is REQUIRED for 'CREATE INDEX CONCURRENTLY' in setup()
                self.pool = AsyncConnectionPool(
                    conninfo=self.uri, 
                    max_size=20, 
                    open=False,
                    kwargs={"autocommit": True}
                )
                await self.pool.open()
                
                # Instantiate Saver with the matching pool
                self.checkpointer = AsyncPostgresSaver(self.pool)
                
                # Critical: This creates the tables in your Postgres DB automatically
                await self.checkpointer.setup()
                log.info("Successfully connected to Postgres and initialized Checkpointer.")
                
            except Exception as e:
                log.error(f"Failed to initialize Postgres Checkpointer: {e}")
                raise e
                
        return self.checkpointer

# Safe to instantiate at module level
db_manager = DatabaseManager()