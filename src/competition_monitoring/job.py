import asyncio
import logging
from pathlib import Path

from patchright.async_api import async_playwright

from .config import ScraperConfig
from .pipeline.cleaner import clean_all_products
from .pipeline.collector import Collector
from .pipeline.exporter import ExcelExporter

logger = logging.getLogger(__name__)


async def _job(config: ScraperConfig | None = None) -> Path:
    if config is None:
        config = ScraperConfig()

    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=config.headless, channel="msedge")
        context = await browser.new_context(
            user_agent=(
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 (KHTML, like Gecko) "
                "Chrome/125.0.0.0 Safari/537.36"
            )
        )
        try:
            collector = Collector(context, config)
            products_by_store = await collector.collect_all()

            products_by_store = clean_all_products(products_by_store)

            exporter = ExcelExporter(config.output_path, config.categories)
            output = exporter.export(products_by_store)

            total = sum(len(p) for p in products_by_store.values())
            logger.info(
                "Pipeline complete: %d products from %d stores -> %s",
                total,
                len(products_by_store),
                str(output),
            )
            return output
        finally:
            await context.close()
            await browser.close()


def run_job(config: ScraperConfig | None = None) -> Path:
    return asyncio.run(_job(config))
