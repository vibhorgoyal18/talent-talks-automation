from __future__ import annotations

import os
from functools import lru_cache
from pathlib import Path
from typing import Any

from dotenv import dotenv_values


class ConfigLoader:
    """Loads environment-specific properties from a .env/.env.example file."""

    def __init__(self, env: str | None = None) -> None:
        self._env = (env or os.getenv("TEST_ENV", "default")).lower()
        root = Path(__file__).resolve().parents[1]
        primary = root / ".env"
        fallback_file = root / ".env.example"
        if primary.exists():
            self._config_path = primary
        elif fallback_file.exists():
            self._config_path = fallback_file
        else:
            raise FileNotFoundError("Neither .env nor .env.example found at project root")

        # Load from .env file
        raw_values = dotenv_values(self._config_path)
        
        # Override with OS environment variables (for CI/CD)
        for key, value in os.environ.items():
            if "__" in key or key.lower() in ["base_url", "headless", "timeout", "trace", "browser", "slow_mo"]:
                raw_values[key] = value
        
        self._namespaced = self._build_namespaced(raw_values)

    @staticmethod
    def _build_namespaced(values: dict[str, str | None]) -> dict[str, dict[str, str]]:
        sections: dict[str, dict[str, str]] = {"default": {}}
        for key, value in values.items():
            if key is None or value is None:
                continue
            normalized_value = value.strip()
            if "__" in key:
                prefix, option = key.split("__", 1)
                prefix = prefix.lower()
                option = option.lower()
                sections.setdefault(prefix, {})[option] = normalized_value
            else:
                sections.setdefault("default", {})[key.lower()] = normalized_value
        return sections

    def _get_section(self, name: str) -> dict[str, str]:
        return self._namespaced.get(name, {})

    def get(self, option: str, fallback: Any | None = None) -> Any:
        option = option.lower()
        env_section = self._get_section(self._env)
        if option in env_section:
            return env_section[option]
        default_section = self._get_section("default")
        return default_section.get(option, fallback)

    def get_int(self, option: str, fallback: int = 0) -> int:
        raw_value = self.get(option)
        if raw_value is None:
            return fallback
        try:
            return int(raw_value)
        except ValueError:
            return fallback

    def as_dict(self) -> dict[str, Any]:
        merged = dict(self._get_section("default"))
        merged.update(self._get_section(self._env))
        return merged


@lru_cache(maxsize=1)
def get_config(env: str | None = None) -> ConfigLoader:
    return ConfigLoader(env=env)
