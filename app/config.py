"""Configuration management for lookup-cli."""

import os
import yaml
from pathlib import Path
from typing import Dict, Any, Optional


class Config:
    """Manages configuration for the lookup-cli tool."""
    
    def __init__(self):
        self.config_dir = Path.home() / ".lu"
        self.config_file = self.config_dir / "config.yaml"
        self._config: Dict[str, Any] = {}
        self.load_config()
    
    def load_config(self) -> None:
        """Load configuration from file."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                self._config = yaml.safe_load(f) or {}
        else:
            self._config = self.get_default_config()
    
    def save_config(self) -> None:
        """Save configuration to file."""
        self.config_dir.mkdir(exist_ok=True)
        with open(self.config_file, 'w', encoding='utf-8') as f:
            yaml.dump(self._config, f, default_flow_style=False, allow_unicode=True)
    
    def get_default_config(self) -> Dict[str, Any]:
        """Get default configuration."""
        return {
            "provider": "openai",
            "models": {
                "openai": {
                    "model": "gpt-3.5-turbo",
                    "api_key": "",
                    "base_url": "https://api.openai.com/v1"
                },
                "dashscope": {
                    "model": "qwen-turbo",
                    "api_key": ""
                },
                "custom": {
                    "model": "gpt-3.5-turbo",
                    "api_key": "",
                    "base_url": ""
                }
            },
            "default_target_language": "en",
            "primary_language": "zh-cn"
        }
    
    def get(self, key: str, default: Any = None) -> Any:
        """Get configuration value."""
        keys = key.split('.')
        value = self._config
        for k in keys:
            if isinstance(value, dict) and k in value:
                value = value[k]
            else:
                return default
        return value
    
    def set(self, key: str, value: Any) -> None:
        """Set configuration value."""
        keys = key.split('.')
        config = self._config
        for k in keys[:-1]:
            if k not in config:
                config[k] = {}
            config = config[k]
        config[keys[-1]] = value
    
    def get_current_model_config(self) -> Dict[str, Any]:
        """Get current model configuration."""
        provider = self.get("provider", "openai")
        return self.get(f"models.{provider}", {})
    
    def update_provider_config(self, provider: str, config: Dict[str, Any]) -> None:
        """Update provider configuration."""
        self.set("provider", provider)
        for key, value in config.items():
            self.set(f"models.{provider}.{key}", value)
        self.save_config()
