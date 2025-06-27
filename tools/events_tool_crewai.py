import os
import asyncpg
import asyncio
from datetime import datetime, timedelta
from typing import Optional, Dict, List, Any
from decouple import config

class EventsTool:
    """Tool for directly accessing event data from the RDS PostgreSQL database."""
    
    def __init__(self):
        # Database connection parameters from environment variables or .env
        self.db_host = os.environ.get('DB_HOST') or config('DB_HOST', default='eventbrite-events-db-instance-1.crymic44oulo.us-east-2.rds.amazonaws.com')
        self.db_name = os.environ.get('DB_NAME') or config('DB_NAME', default='events_db')
        self.db_user = os.environ.get('DB_USER') or config('DB_USER', default='rds_admin')
        self.db_password = os.environ.get('DB_PASSWORD') or config('DB_PASSWORD', default='Amazonwebservices777!')
        self.db_port = int(os.environ.get('DB_PORT') or config('DB_PORT', default='5432'))
        self.pool = None
        
    async def _init_db_pool(self):
        """Initialize the database connection pool if it doesn't exist"""
        if self.pool is None:
            try:
                self.pool = await asyncpg.create_pool(
                    host=self.db_host,
                    database=self.db_name,
                    user=self.db_user,
                    password=self.db_password,
                    port=self.db_port,
                    min_size=1,
                    max_size=10,
                    command_timeout=60
                )
                print(f"Database connection pool established successfully")
            except Exception as e:
                print(f"Failed to create database pool: {str(e)}")
                raise

    async def _get_todays_events_async(self, postal_code: Optional[str] = None) -> str:
        """Get events happening today from the database"""
        await self._init_db_pool()
        
        try:
            async with self.pool.acquire() as connection:
                # Get today's date
                today = datetime.now().date()
                
                # Base query for today's events using correct column names
                base_query = """
                    SELECT name, start_date, venue_name, postal_code, summary
                    FROM events 
                    WHERE start_date = $1
                """
                
                # Add postal code filter if provided
                if postal_code:
                    query = base_query + " AND postal_code = $2 ORDER BY name"
                    rows = await connection.fetch(query, today, int(postal_code))
                else:
                    query = base_query + " ORDER BY name"
                    rows = await connection.fetch(query, today)
                
                if not rows:
                    location_filter = f" in postal code {postal_code}" if postal_code else ""
                    return f"No events found for today{location_filter}."
                
                # Format the results
                events_list = []
                for row in rows:
                    event_info = f"""
Event: {row['name']}
Date: {row['start_date']}
Venue: {row['venue_name'] or 'Not specified'}
Postal Code: {row['postal_code'] or 'Not specified'}
Summary: {row['summary'][:200] if row['summary'] else 'No summary available'}...
                    """
                    events_list.append(event_info.strip())
                
                return f"Found {len(events_list)} events for today:\n\n" + "\n\n".join(events_list)
                
        except Exception as e:
            return f"Error retrieving today's events: {str(e)}"    
    async def _get_events_by_postal_code_async(self, postal_code: str, days_back: int = 7) -> str:
        """Get events by postal code for the last specified number of days"""
        await self._init_db_pool()
        
        try:
            async with self.pool.acquire() as connection:
                # Calculate date range
                end_date = datetime.now().date()
                start_date = end_date - timedelta(days=days_back)
                
                # Fixed query using correct column names
                query = """
                    SELECT name, start_date, venue_name, postal_code, summary
                    FROM events 
                    WHERE postal_code = $1 
                    AND start_date BETWEEN $2 AND $3
                    ORDER BY start_date DESC, name
                """
                
                # Ensure we have a fresh connection by checking if it's valid
                await connection.execute("SELECT 1")
                
                rows = await connection.fetch(query, int(postal_code), start_date, end_date)
                
                if not rows:
                    return f"No events found in postal code {postal_code} for the last {days_back} days."
                
                # Format the results
                events_list = []
                for row in rows:
                    event_info = f"""
Event: {row['name']}
Date: {row['start_date']}
Venue: {row['venue_name'] or 'Not specified'}
Postal Code: {row['postal_code'] or 'Not specified'}
Summary: {row['summary'][:200] if row['summary'] else 'No summary available'}...
                    """
                    events_list.append(event_info.strip())
                
                return f"Found {len(events_list)} events in postal code {postal_code} (last {days_back} days):\n\n" + "\n\n".join(events_list)
                
        except Exception as e:
            # If we get a connection error, try to reset the pool
            if "connection" in str(e).lower():
                print(f"Connection error detected, resetting pool: {e}")
                if self.pool:
                    await self.pool.close()
                    self.pool = None
                await self._init_db_pool()
                # Retry once with fresh pool
                try:
                    async with self.pool.acquire() as connection:
                        rows = await connection.fetch(query, int(postal_code), start_date, end_date)
                        if not rows:
                            return f"No events found in postal code {postal_code} for the last {days_back} days."
                        
                        events_list = []
                        for row in rows:
                            event_info = f"""
Event: {row['name']}
Date: {row['start_date']}
Venue: {row['venue_name'] or 'Not specified'}
Postal Code: {row['postal_code'] or 'Not specified'}
Summary: {row['summary'][:200] if row['summary'] else 'No summary available'}...
                            """
                            events_list.append(event_info.strip())
                        
                        return f"Found {len(events_list)} events in postal code {postal_code} (last {days_back} days):\n\n" + "\n\n".join(events_list)
                except Exception as retry_e:
                    return f"Error retrieving events for postal code {postal_code} (retry failed): {str(retry_e)}"
            
            return f"Error retrieving events for postal code {postal_code}: {str(e)}"

    def _run_sync(self, coro):
        """Helper to run async code in sync context"""
        import concurrent.futures
        import threading
        
        def run_in_thread():
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                return loop.run_until_complete(coro)
            finally:
                loop.close()
        
        with concurrent.futures.ThreadPoolExecutor() as executor:
            future = executor.submit(run_in_thread)
            return future.result()

    def get_todays_events(self, postal_code: Optional[str] = None) -> str:
        """
        Get events happening today, optionally filtered by postal code.
        
        Args:
            postal_code (str, optional): Optional postal code to filter events
            
        Returns:
            str: List of events happening today
        """
        return self._run_sync(self._get_todays_events_async(postal_code))

    def get_events_by_postal_code(self, postal_code: str, days_back: int = 7) -> str:
        """
        Get events for a specific postal code within the last specified number of days.
        
        Args:
            postal_code (str): Postal code to search for events
            days_back (int): Number of days back to search (default: 7)
            
        Returns:
            str: List of events in the specified postal code
        """
        return self._run_sync(self._get_events_by_postal_code_async(postal_code, days_back))

    async def close(self):
        """Close the database connection pool"""
        if self.pool:
            await self.pool.close()
            self.pool = None
