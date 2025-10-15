"""
Database utilities for storing and retrieving domain analysis results.
Supports PostgreSQL.
"""

import psycopg2
from psycopg2.extras import RealDictCursor, Json
from typing import Dict, Any, List, Optional
import json
from datetime import datetime
from src.utils.logger import setup_logger

logger = setup_logger(name='db')


class DatabaseConnection:
    """Context manager for database connections with connection pooling support."""
    
    def __init__(self, db_url: str):
        self.db_url = db_url
        self.conn = None
        self.cursor = None
    
    def __enter__(self):
        self.conn = psycopg2.connect(self.db_url)
        self.cursor = self.conn.cursor(cursor_factory=RealDictCursor)
        return self.cursor
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        if exc_type is not None:
            self.conn.rollback()
        else:
            self.conn.commit()
        self.cursor.close()
        self.conn.close()


def init_db(db_url: str) -> bool:
    """
    Initialize database connection and verify tables exist.
    
    Args:
        db_url: PostgreSQL connection string
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with DatabaseConnection(db_url) as cursor:
            # Check if required tables exist
            cursor.execute("""
                SELECT table_name 
                FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name IN ('domains', 'tasks', 'results')
            """)
            tables = [row['table_name'] for row in cursor.fetchall()]
            
            if len(tables) != 3:
                missing = set(['domains', 'tasks', 'results']) - set(tables)
                logger.error(f"Missing required tables: {missing}")
                logger.info("Run: psql $DATABASE_URL -f db/schema.sql")
                return False
            
            logger.info("Database connection verified")
            return True
            
    except psycopg2.Error as e:
        logger.error(f"Database connection failed: {e}")
        return False


def get_or_create_domain(cursor, domain: str) -> int:
    """
    Get domain_id for a domain, creating it if it doesn't exist.
    
    Args:
        cursor: Database cursor
        domain: Domain name
        
    Returns:
        domain_id (int)
    """
    # Try to get existing domain
    cursor.execute(
        "SELECT id FROM domains WHERE domain_name = %s",
        (domain,)
    )
    row = cursor.fetchone()
    
    if row:
        return row['id']
    
    # Create new domain
    cursor.execute(
        """
        INSERT INTO domains (domain_name, created_at, updated_at)
        VALUES (%s, NOW(), NOW())
        RETURNING id
        """,
        (domain,)
    )
    return cursor.fetchone()['id']


def get_or_create_task(cursor, task_name: str) -> int:
    """
    Get task_id for a task, creating it if it doesn't exist.
    
    Args:
        cursor: Database cursor
        task_name: Task name (e.g., 'basic-scan')
        
    Returns:
        task_id (int)
    """
    # Try to get existing task
    cursor.execute(
        "SELECT id FROM tasks WHERE name = %s",
        (task_name,)
    )
    row = cursor.fetchone()
    
    if row:
        return row['id']
    
    # Create new task
    cursor.execute(
        """
        INSERT INTO tasks (name, description)
        VALUES (%s, %s)
        RETURNING id
        """,
        (task_name, f"Automated {task_name}")
    )
    return cursor.fetchone()['id']


def save_result(db_url: str, domain: str, task: str, result_data: Dict[str, Any]) -> bool:
    """
    Save a complete domain analysis result to the database.
    
    Args:
        db_url: PostgreSQL connection string
        domain: Domain name
        task: Task name (e.g., 'basic-scan')
        result_data: Complete result JSON from orchestrator
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with DatabaseConnection(db_url) as cursor:
            # Get or create domain and task
            domain_id = get_or_create_domain(cursor, domain)
            task_id = get_or_create_task(cursor, task)
            
            # Extract status from result
            status = result_data.get('meta', {}).get('status', 'unknown')
            
            # Insert result
            cursor.execute(
                """
                INSERT INTO results (domain_id, task_id, status, data, checked_at)
                VALUES (%s, %s, %s, %s, NOW())
                """,
                (domain_id, task_id, status, Json(result_data))
            )
            
            # Update domain's last_checked timestamp
            cursor.execute(
                "UPDATE domains SET updated_at = NOW() WHERE id = %s",
                (domain_id,)
            )
            
            logger.debug(f"Saved result for {domain} (status: {status})")
            return True
            
    except psycopg2.Error as e:
        logger.error(f"Failed to save result for {domain}: {e}")
        return False


def get_domains(db_url: str, limit: Optional[int] = None) -> List[Dict[str, Any]]:
    """
    Get list of all domains from database.
    
    Args:
        db_url: PostgreSQL connection string
        limit: Optional limit on number of domains to return
        
    Returns:
        List of domain dictionaries with id, domain_name, created_at, updated_at
    """
    try:
        with DatabaseConnection(db_url) as cursor:
            query = "SELECT * FROM domains ORDER BY updated_at DESC"
            if limit:
                query += f" LIMIT {limit}"
            
            cursor.execute(query)
            return cursor.fetchall()
            
    except psycopg2.Error as e:
        logger.error(f"Failed to get domains: {e}")
        return []


def get_domain_results(
    db_url: str, 
    domain: str, 
    limit: Optional[int] = 10
) -> List[Dict[str, Any]]:
    """
    Get recent results for a specific domain.
    
    Args:
        db_url: PostgreSQL connection string
        domain: Domain name
        limit: Number of recent results to return (default: 10)
        
    Returns:
        List of result dictionaries
    """
    try:
        with DatabaseConnection(db_url) as cursor:
            cursor.execute(
                """
                SELECT r.id, r.status, r.data, r.checked_at, t.name as task_name
                FROM results r
                JOIN domains d ON r.domain_id = d.id
                JOIN tasks t ON r.task_id = t.id
                WHERE d.domain_name = %s
                ORDER BY r.checked_at DESC
                LIMIT %s
                """,
                (domain, limit)
            )
            return cursor.fetchall()
            
    except psycopg2.Error as e:
        logger.error(f"Failed to get results for {domain}: {e}")
        return []


def get_latest_results(db_url: str, limit: int = 20) -> List[Dict[str, Any]]:
    """
    Get the most recent analysis results across all domains.
    
    Args:
        db_url: PostgreSQL connection string
        limit: Number of results to return (default: 20)
        
    Returns:
        List of result dictionaries with domain info
    """
    try:
        with DatabaseConnection(db_url) as cursor:
            cursor.execute(
                """
                SELECT 
                    r.id, 
                    d.domain_name, 
                    t.name as task_name,
                    r.status, 
                    r.data, 
                    r.checked_at
                FROM results r
                JOIN domains d ON r.domain_id = d.id
                JOIN tasks t ON r.task_id = t.id
                ORDER BY r.checked_at DESC
                LIMIT %s
                """,
                (limit,)
            )
            return cursor.fetchall()
            
    except psycopg2.Error as e:
        logger.error(f"Failed to get latest results: {e}")
        return []


def get_stats(db_url: str) -> Dict[str, Any]:
    """
    Get database statistics.
    
    Args:
        db_url: PostgreSQL connection string
        
    Returns:
        Dictionary with statistics
    """
    try:
        with DatabaseConnection(db_url) as cursor:
            stats = {}
            
            # Count domains
            cursor.execute("SELECT COUNT(*) as count FROM domains")
            stats['total_domains'] = cursor.fetchone()['count']
            
            # Count results
            cursor.execute("SELECT COUNT(*) as count FROM results")
            stats['total_results'] = cursor.fetchone()['count']
            
            # Count by status
            cursor.execute("""
                SELECT status, COUNT(*) as count 
                FROM results 
                GROUP BY status
            """)
            stats['results_by_status'] = {row['status']: row['count'] for row in cursor.fetchall()}
            
            # Last check time
            cursor.execute("SELECT MAX(checked_at) as last_check FROM results")
            last_check = cursor.fetchone()['last_check']
            stats['last_check'] = last_check.isoformat() if last_check else None
            
            return stats
            
    except psycopg2.Error as e:
        logger.error(f"Failed to get stats: {e}")
        return {}


def update_domain_flags(db_url: str, domain: str, is_registered: Optional[bool] = None, is_active: Optional[bool] = None) -> bool:
    """
    Update is_registered and is_active flags for a domain.
    Used by orchestrator after running WHOIS and active checks.
    
    Args:
        db_url: PostgreSQL connection string
        domain: Domain name
        is_registered: Registration status (True/False/None)
        is_active: Activity status (True/False/None)
        
    Returns:
        True if successful, False otherwise
    """
    try:
        with DatabaseConnection(db_url) as cursor:
            # Get domain_id
            domain_id = get_or_create_domain(cursor, domain)
            
            # Build UPDATE query for fields that are provided
            updates = []
            params = []
            
            if is_registered is not None:
                updates.append("is_registered = %s")
                params.append(is_registered)
            
            if is_active is not None:
                updates.append("is_active = %s")
                params.append(is_active)
            
            if not updates:
                # Nothing to update
                return True
            
            # Always update updated_at
            updates.append("updated_at = NOW()")
            params.append(domain_id)
            
            query = f"UPDATE domains SET {', '.join(updates)} WHERE id = %s"
            cursor.execute(query, params)
            
            logger.debug(f"Updated flags for {domain}: is_registered={is_registered}, is_active={is_active}")
            return True
            
    except psycopg2.Error as e:
        logger.error(f"Failed to update flags for {domain}: {e}")
        return False


def get_domain_flags(db_url: str, domain: str) -> Dict[str, Optional[bool]]:
    """
    Get is_registered and is_active flags for a domain.
    
    Args:
        db_url: PostgreSQL connection string
        domain: Domain name
        
    Returns:
        Dictionary with 'is_registered' and 'is_active' keys (can be None)
    """
    try:
        with DatabaseConnection(db_url) as cursor:
            cursor.execute(
                "SELECT is_registered, is_active FROM domains WHERE domain_name = %s",
                (domain,)
            )
            row = cursor.fetchone()
            
            if row:
                return {
                    'is_registered': row['is_registered'],
                    'is_active': row['is_active']
                }
            else:
                return {
                    'is_registered': None,
                    'is_active': None
                }
                
    except psycopg2.Error as e:
        logger.error(f"Failed to get flags for {domain}: {e}")
        return {'is_registered': None, 'is_active': None}


def insert_captured_domain(db_url: str, domain: str, source_domain: str = None) -> bool:
    """
    Insert a captured .lt domain into the database for future checking.
    
    This is used when discovering new .lt domains from redirect chains.
    If the domain already exists, this is a no-op.
    
    Args:
        db_url: PostgreSQL connection string
        domain: Domain name to insert
        source_domain: Original domain that redirected to this (for logging)
        
    Returns:
        True if inserted (new domain), False if already exists or error
    """
    try:
        with DatabaseConnection(db_url) as cursor:
            # Check if domain already exists
            cursor.execute(
                "SELECT id FROM domains WHERE domain_name = %s",
                (domain,)
            )
            existing = cursor.fetchone()
            
            if existing:
                logger.debug(f"Domain {domain} already exists (id={existing['id']})")
                return False
            
            # Insert new domain
            cursor.execute(
                """
                INSERT INTO domains (domain_name, created_at, updated_at)
                VALUES (%s, NOW(), NOW())
                RETURNING id
                """,
                (domain,)
            )
            domain_id = cursor.fetchone()['id']
            
            source_info = f" (from {source_domain})" if source_domain else ""
            logger.info(f"✅ Inserted captured domain: {domain}{source_info} (id={domain_id})")
            return True
            
    except psycopg2.Error as e:
        logger.error(f"Failed to insert domain {domain}: {e}")
        return False

