from __future__ import annotations

from typing import TYPE_CHECKING

import allure

if TYPE_CHECKING:
    from core.web.playwright_wrapper import PlaywrightWrapper


class AllureManager:
    """Utility helpers around Allure attachments."""

    @staticmethod
    def attach_screenshot(wrapper: "PlaywrightWrapper", name: str) -> None:
        """Attach a screenshot from Playwright wrapper to Allure report."""
        try:
            png = wrapper.get_screenshot_bytes()
        except Exception:
            return
        allure.attach(png, name=name, attachment_type=allure.attachment_type.PNG)

    @staticmethod
    def attach_text(name: str, content: str) -> None:
        """Attach text content to Allure report."""
        allure.attach(content, name=name, attachment_type=allure.attachment_type.TEXT)

    @staticmethod
    def attach_trace(trace_path: str, name: str = "trace") -> None:
        """Attach Playwright trace file to Allure report."""
        try:
            with open(trace_path, "rb") as f:
                allure.attach(
                    f.read(),
                    name=f"{name}.zip",
                    attachment_type=allure.attachment_type.ZIP
                )
        except Exception:
            pass
