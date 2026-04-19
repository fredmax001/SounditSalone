"""
Configuration management for Sound It CLI
"""
import os
import json
from pathlib import Path
from dataclasses import dataclass, asdict
from typing import Optional


@dataclass
class CLIConfig:
    """CLI Configuration"""
    api_base_url: str = "http://localhost:8000"
    api_version: str = "v1"
    access_token: Optional[str] = None
    refresh_token: Optional[str] = None
    token_expires: Optional[str] = None
    default_format: str = "table"  # table, json, csv
    
    @property
    def api_url(self) -> str:
        """Get full API URL"""
        return f"{self.api_base_url}/api/{self.api_version}"


class ConfigManager:
    """Manage CLI configuration"""
    
    CONFIG_DIR = Path.home() / ".soundit"
    CONFIG_FILE = CONFIG_DIR / "config.json"
    
    @classmethod
    def get_config(cls) -> CLIConfig:
        """Load configuration from file"""
        if cls.CONFIG_FILE.exists():
            with open(cls.CONFIG_FILE, 'r') as f:
                data = json.load(f)
                return CLIConfig(**data)
        return CLIConfig()
    
    @classmethod
    def save_config(cls, config: CLIConfig) -> None:
        """Save configuration to file"""
        cls.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        with open(cls.CONFIG_FILE, 'w') as f:
            json.dump(asdict(config), f, indent=2)
    
    @classmethod
    def clear_config(cls) -> None:
        """Clear all configuration"""
        if cls.CONFIG_FILE.exists():
            cls.CONFIG_FILE.unlink()
    
    @classmethod
    def is_logged_in(cls) -> bool:
        """Check if user is logged in"""
        config = cls.get_config()
        return config.access_token is not None


# Environment variable overrides
def get_env_config() -> dict:
    """Get configuration from environment variables"""
    return {
        k.replace("SOUNDIT_", "").lower(): v
        for k, v in os.environ.items()
        if k.startswith("SOUNDIT_")
    }
