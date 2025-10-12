import os
from urllib.parse import urlparse

try:
    from dotenv import load_dotenv  # type: ignore
except Exception:  # pragma: no cover
    load_dotenv = None  # fallback if not installed yet


def load_env() -> None:
    """Load environment variables from a .env file if python-dotenv is available."""
    if load_dotenv:
        # .env at repo root
        env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
        if os.path.exists(env_path):
            load_dotenv(env_path)


def get_database_url() -> str:
    load_env()
    url = os.getenv("DATABASE_URL")
    if url:
        return url

    # Fallback to discrete vars if DATABASE_URL is missing
    name = os.getenv("DB_NAME", "domenai")
    user = os.getenv("DB_USER", "domenai")
    password = os.getenv("DB_PASSWORD", "")
    host = os.getenv("DB_HOST", "localhost")
    port = os.getenv("DB_PORT", "5432")
    return f"postgresql://{user}:{password}@{host}:{port}/{name}"


def db_url_to_psycopg_kwargs(db_url: str) -> dict:
    """Convert a PostgreSQL URL into psycopg2.connect kwargs."""
    parsed = urlparse(db_url)
    # Support both postgres:// and postgresql://
    if parsed.scheme not in ("postgres", "postgresql"):
        raise ValueError(f"Unsupported DB scheme: {parsed.scheme}")

    # username:password@host:port
    username = parsed.username or ""
    password = parsed.password or ""
    hostname = parsed.hostname or "localhost"
    port = parsed.port or 5432
    dbname = (parsed.path or "/").lstrip("/") or "postgres"

    return {
        "dbname": dbname,
        "user": username,
        "password": password,
        "host": hostname,
        "port": port,
    }


def get_db_connect_kwargs() -> dict:
    """Return psycopg2.connect(**kwargs) from env configuration."""
    return db_url_to_psycopg_kwargs(get_database_url())
