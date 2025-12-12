"""
Typed context wrapper for step definitions.

This module provides a typed wrapper class for behave context,
enabling IDE navigation (Cmd+Click) and IntelliSense for all context attributes.

Usage in step files:
    from features.steps.step_context import StepContext

    @when("I do something")
    def step_do_something(context):
        ctx = StepContext(context)
        ctx.wrapper.click("#button")  # Full IntelliSense + Cmd+Click works
        ctx.logger.info("Done")
        ctx.data_loader.find_by_key(...)
"""
from __future__ import annotations

import logging
from typing import TYPE_CHECKING

from core.web.playwright_wrapper import PlaywrightWrapper
from utils.config_loader import ConfigLoader
from utils.data_loader import JsonDataLoader

if TYPE_CHECKING:
    from behave.runner import Context


class StepContext:
    """Typed wrapper for behave context providing IDE navigation support."""
    
    def __init__(self, context: Context) -> None:
        self._context = context
    
    @property
    def wrapper(self) -> PlaywrightWrapper:
        """Get the PlaywrightWrapper for browser interactions."""
        return self._context.wrapper  # type: ignore[return-value]
    
    @property
    def logger(self) -> logging.Logger:
        """Get the logger for logging messages."""
        return self._context.logger  # type: ignore[return-value]
    
    @property
    def config(self) -> ConfigLoader:
        """Get the ConfigLoader for configuration access."""
        return self._context.config_loader  # type: ignore[return-value]
    
    @property
    def data_loader(self) -> JsonDataLoader:
        """Get the JsonDataLoader for test data access."""
        return self._context.data_loader  # type: ignore[return-value]
    
    @property
    def base_url(self) -> str:
        """Get the base URL from configuration."""
        return self.config.get("base_url")
