"""Configuration management for the voice number generator."""

import os
from pathlib import Path
from typing import Optional


class Config:
    """Configuration class for API keys and settings."""
    
    def __init__(self, config_file: Optional[str] = None):
        """
        Initialize configuration.
        
        Args:
            config_file: Path to config file (optional)
        """
        self.config_file = config_file or "config.env"
        self._load_config()
    
    def _load_config(self):
        """Load configuration from file if it exists."""
        config_path = Path(self.config_file)
        if config_path.exists():
            with open(config_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#'):
                        if '=' in line:
                            key, value = line.split('=', 1)
                            os.environ[key.strip()] = value.strip()
    
    @property
    def openai_api_key(self) -> Optional[str]:
        """Get OpenAI API key from environment or config file."""
        return os.getenv('OPENAI_API_KEY')
    
    def is_configured(self) -> bool:
        """Check if API key is configured."""
        return self.openai_api_key is not None