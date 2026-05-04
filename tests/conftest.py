from typing import AsyncGenerator

from patchright.async_api import (
    Browser,
    BrowserContext,
    BrowserType,
    Page,
    async_playwright,
)
from pytest import fixture


@fixture(scope="session")
async def patched_browser() -> AsyncGenerator[Browser, None]:
    async with async_playwright() as playwright:
        browser_type: BrowserType = playwright.chromium
        browser: Browser = await browser_type.launch(channel="msedge", headless=False)
        yield browser


@fixture(scope="session")
async def patched_context(
    patched_browser: Browser,
) -> AsyncGenerator[BrowserContext, None]:
    yield await patched_browser.new_context()


@fixture(scope="session")
async def patched_page(patched_context: BrowserContext) -> AsyncGenerator[Page, None]:
    yield await patched_context.new_page()
