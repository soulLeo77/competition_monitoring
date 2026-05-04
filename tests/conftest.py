from typing import AsyncGenerator

from patchright.async_api import (
    Browser,
    BrowserContext,
    BrowserType,
    Page,
    async_playwright,
)
from pytest import fixture
from competition_monitoring.user_agent import get_headed_user_agent


@fixture(scope="session")
async def patched_browser() -> AsyncGenerator[Browser, None]:
    async with async_playwright() as playwright:
        browser_type: BrowserType = playwright.chromium
        browser: Browser = await browser_type.launch(channel="msedge", headless=False)
        yield browser


@fixture(scope="session")
async def headed_user_agent(patched_browser: Browser) -> AsyncGenerator[str, None]:
    page: Page = await patched_browser.new_page()
    yield await get_headed_user_agent(page)
    await page.close()


@fixture(scope="session")
async def patched_headed_context(
    patched_browser: Browser, headed_user_agent: str
) -> AsyncGenerator[BrowserContext, None]:
    yield await patched_browser.new_context(user_agent=headed_user_agent)


@fixture(scope="session")
async def patched_context(
    patched_browser: Browser,
) -> AsyncGenerator[BrowserContext, None]:
    yield await patched_browser.new_context()


@fixture(scope="session")
async def patched_page(patched_context: BrowserContext) -> AsyncGenerator[Page, None]:
    yield await patched_context.new_page()
