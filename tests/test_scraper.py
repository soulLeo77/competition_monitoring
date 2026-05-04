from patchright.async_api import BrowserContext

from competition_monitoring.scraper.falabella import FalabellaScraper
from competition_monitoring.scraper.ripley import RipleyScraper
from asyncio import gather


async def test_falabella(patched_context: BrowserContext) -> None:
    scraper: FalabellaScraper = FalabellaScraper(patched_context)

    await scraper.go_to_product_page("laptops")
    product_links: tuple[str, ...] = await scraper.get_product_links()

    # Procesar en lotes de 10
    await scraper.get_product_data_batch(list(product_links), batch_size=7)

    assert product_links


async def test_ripley(patched_context: BrowserContext) -> None:
    scraper: RipleyScraper = RipleyScraper(patched_context)

    await scraper.go_to_product_page("laptops")
    product_links: tuple[str, ...] = await scraper.get_products_links()

    await gather(*[scraper.get_product_data(link) for link in product_links[:10]])

    assert product_links
