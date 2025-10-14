"""Configuration loader for YAML and environment variables"""
import os
import yaml
from pathlib import Path
from typing import Dict, Any


def get_project_root() -> Path:
    """Get the project root directory"""
    return Path(__file__).parent.parent.parent


def load_config(config_path: str = None) -> Dict[str, Any]:
    """
    Load configuration from YAML file.
    
    Args:
        config_path: Optional path to config file. Defaults to config.yaml in project root.
        
    Returns:
        Dict containing configuration
    """
    if config_path is None:
        config_path = get_project_root() / "config.yaml"
    else:
        config_path = Path(config_path)
    
    if not config_path.exists():
        raise FileNotFoundError(f"Config file not found: {config_path}")
    
    with open(config_path, 'r') as f:
        config = yaml.safe_load(f)
    
    # Override with environment variables if present
    if 'DATABASE_URL' in os.environ:
        if 'database' not in config:
            config['database'] = {}
        config['database']['postgres_url'] = os.environ['DATABASE_URL']
    
    return config


def get_database_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract database configuration"""
    return config.get('database', {})


def get_logging_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract logging configuration"""
    return config.get('logging', {})


def get_orchestrator_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract orchestrator configuration"""
    return config.get('orchestrator', {})


def get_network_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract network configuration"""
    return config.get('network', {})


def get_checks_config(config: Dict[str, Any]) -> Dict[str, Any]:
    """Extract checks configuration"""
    return config.get('checks', {})
