from patchright.async_api import BrowserContext

from competition_monitoring.scraper.falabella import FalabellaScraper
from competition_monitoring.scraper.oechsle import OechsleScraper
from competition_monitoring.scraper.plaza_vea import PlazaVeaScraper
from competition_monitoring.scraper.ripley import RipleyScraper

# from asyncio import gather


async def test_falabella(patched_context: BrowserContext) -> None:
    scraper: FalabellaScraper = FalabellaScraper(patched_context)

    await scraper.go_to_product_page("laptops")
    product_links: tuple[str, ...] = await scraper.get_products_links()

    await scraper.get_product_data_batch(product_links, batch_size=7)

    assert product_links


async def test_ripley(patched_headed_context: BrowserContext) -> None:
    scraper: RipleyScraper = RipleyScraper(patched_headed_context)

    await scraper.go_to_product_page("laptops")
    product_links: tuple[str, ...] = await scraper.get_products_links()

    await scraper.get_product_data_batch(product_links, batch_size=5)

    assert product_links


async def test_plaza_vea(patched_headed_context: BrowserContext) -> None:
    scraper: PlazaVeaScraper = PlazaVeaScraper(patched_headed_context)

    await scraper.go_to_product_page("laptops")
    product_links: tuple[str, ...] = await scraper.get_products_links()

    await scraper.get_product_data_batch(product_links, batch_size=5)

    assert product_links


async def test_oechsle(patched_headed_context: BrowserContext) -> None:
    scraper: OechsleScraper = OechsleScraper(patched_headed_context)

    await scraper.go_to_product_page("laptops")
    product_links: tuple[str, ...] = await scraper.get_products_links()

    await scraper.get_product_data_batch(product_links, batch_size=5)

    assert product_links
