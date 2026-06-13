import asyncio
import logging
from typing import Any

from patchright.async_api import BrowserContext

from ..config import ScraperConfig
from ..interface.scraper import BaseScraper
from ..models.product import Product
from ..scraper.falabella import FalabellaScraper
from ..scraper.oechsle import OechsleScraper
from ..scraper.plaza_vea import PlazaVeaScraper
from ..scraper.ripley import RipleyScraper

logger = logging.getLogger(__name__)

SCRAPER_REGISTRY: dict[str, type[BaseScraper]] = {
    "falabella": FalabellaScraper,  # type: ignore
    "plaza_vea": PlazaVeaScraper,
    "ripley": RipleyScraper,
    "oechsle": OechsleScraper,
}

REQUIRED_METHODS = ["go_to_product_page", "get_products_links", "get_product_data"]


class Collector:
    def __init__(self, context: BrowserContext, config: ScraperConfig) -> None:
        self.context = context
        self.config = config

    async def collect_all(self) -> dict[str, list[Product]]:
        return {
            store: await self._collect_store(store, cls)
            for store, cls in SCRAPER_REGISTRY.items()
            if store in self.config.categories
        }

    async def _collect_store(
        self, store_name: str, scraper_class: type
    ) -> list[Product]:
        categories = self.config.categories.get(store_name, [])
        if not categories:
            logger.info("%s: no categories configured, skipping", store_name)
            return []

        scraper = scraper_class(self.context)
        if not self._is_ready(scraper):
            logger.warning("%s: incomplete scraper, skipping", store_name)
            return []

        store_products: list[Product] = []
        for category in categories:
            try:
                products = await self._collect_category(scraper, store_name, category)
                store_products.extend(products)
            except Exception as e:
                logger.error("%s/%s: %s", store_name, category, e)

        return store_products

    async def _collect_category(
        self, scraper: BaseScraper, store_name: str, category: str
    ) -> list[Product]:
        logger.info("%s/%s: navigating...", store_name, category)
        await scraper.go_to_product_page(category)
        links = await scraper.get_products_links()
        logger.info("%s/%s: %d links found", store_name, category, len(links))
        return await self._process_links(scraper, links)

    async def _process_links(
        self, scraper: BaseScraper, links: tuple[str, ...]
    ) -> list[Product]:
        products: list[Product] = []
        for i in range(0, len(links), self.config.batch_size):
            batch = links[i : i + self.config.batch_size]
            results = await asyncio.gather(
                *[scraper.get_product_data(link) for link in batch],
                return_exceptions=True,
            )
            for result in results:
                if isinstance(result, Exception):
                    logger.error("%s: %s", type(scraper).__name__, result)
                else:
                    products.append(result)  # type: ignore
        return products

    @staticmethod
    def _is_ready(scraper: Any) -> bool:
        return all(hasattr(scraper, m) for m in REQUIRED_METHODS)
