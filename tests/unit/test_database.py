"""Unit tests for database utilities

Tests database connection, result persistence, and query functions.
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from src.utils.db import (
    save_result,
    update_domain_flags,
)


class TestDatabaseConnection:
    """Test database connection management"""

    @patch('src.utils.db.psycopg2.connect')
    def test_init_db_success(self, mock_connect):
        """Test successful database initialization"""
        from src.utils.db import init_db
        
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value = mock_cursor
        mock_connect.return_value = mock_conn
        
        result = init_db("postgresql://localhost/test")
        assert result is True
        mock_connect.assert_called_once()

    @patch('src.utils.db.psycopg2.connect')
    def test_init_db_failure(self, mock_connect):
        """Test database initialization failure"""
        from src.utils.db import init_db
        
        mock_connect.side_effect = Exception("Connection failed")
        result = init_db("postgresql://localhost/test")
        assert result is False


class TestSaveResult:
    """Test result persistence"""

    @patch('src.utils.db.psycopg2.connect')
    def test_save_result_minimal(self, mock_connect):
        """Test saving minimal valid result"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        result = {
            "domain": "example.com",
            "status": "success",
            "timestamp": "2025-10-15T10:00:00Z",
        }
        
        # Should not raise
        save_result(result, "postgresql://localhost/test", task_id=1)

    def test_save_result_invalid_structure(self):
        """Test saving result with invalid structure"""
        invalid_result = {"invalid": "data"}
        
        with pytest.raises(KeyError):
            save_result(invalid_result, "postgresql://localhost/test", task_id=1)


class TestUpdateDomainFlags:
    """Test domain flag updates"""

    @patch('src.utils.db.psycopg2.connect')
    def test_update_flags_both_true(self, mock_connect):
        """Test updating flags with both True"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        update_domain_flags(
            "example.com",
            is_registered=True,
            is_active=True,
            database_url="postgresql://localhost/test"
        )
        
        mock_cursor.execute.assert_called_once()

    @patch('src.utils.db.psycopg2.connect')
    def test_update_flags_partial(self, mock_connect):
        """Test updating only one flag"""
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        update_domain_flags(
            "example.com",
            is_registered=True,
            is_active=None,
            database_url="postgresql://localhost/test"
        )
        
        mock_cursor.execute.assert_called_once()


class TestDatabaseQueries:
    """Test database query functions"""

    @patch('src.utils.db.psycopg2.connect')
    def test_get_domains(self, mock_connect):
        """Test retrieving domain list"""
        from src.utils.db import get_domains
        
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchall.return_value = [
            (1, "example.com", "2025-10-15"),
            (2, "test.com", "2025-10-15"),
        ]
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        domains = get_domains("postgresql://localhost/test")
        assert len(domains) == 2

    @patch('src.utils.db.psycopg2.connect')
    def test_get_stats(self, mock_connect):
        """Test retrieving database statistics"""
        from src.utils.db import get_stats
        
        mock_conn = Mock()
        mock_cursor = Mock()
        mock_cursor.fetchone.return_value = (10, 25)
        mock_conn.cursor.return_value.__enter__.return_value = mock_cursor
        mock_connect.return_value.__enter__.return_value = mock_conn
        
        stats = get_stats("postgresql://localhost/test")
        assert "total_domains" in stats
        assert "total_results" in stats


@pytest.mark.db
class TestDatabaseIntegration:
    """Integration tests requiring actual database
    
    These tests are marked with @pytest.mark.db and can be skipped
    if no test database is available.
    """

    def test_full_workflow(self):
        """Test complete database workflow
        
        This test requires TEST_DATABASE_URL environment variable
        """
        pytest.skip("Integration test - requires database")

    def test_concurrent_writes(self):
        """Test concurrent result writes"""
        pytest.skip("Integration test - requires database")
