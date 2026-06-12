from asyncio import gather
from datetime import datetime
from decimal import Decimal
from typing import Any

from patchright.async_api import BrowserContext, Locator, Page

from ..interface.scraper import BaseScraper
from ..models.product import Product
from ..paths import OECHSLE_DATA
from ..util.files import save_data
from ..util.oechsle import get_availability, get_discount, get_prices


class OechsleScraper(BaseScraper):

    BASE_URL: str = "https://www.oechsle.pe/"

    def __init__(self, context: BrowserContext) -> None:
        self.context: BrowserContext = context
        self.page: Page | None = None

    async def _get_page(self) -> Page:
        if self.page is None:
            self.page = await self.context.new_page()
        return self.page

    async def go_to_home_page(self) -> None:
        page: Page = await self._get_page()
        await page.goto(self.BASE_URL)
        await page.wait_for_load_state("networkidle")

    async def go_to_product_page(self, category: str) -> None:
        page: Page = await self._get_page()

        await page.goto(self.BASE_URL)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(500)

        search_bar: Locator = page.locator("input#inputIntelligentSearch")
        await search_bar.fill(category)
        await page.keyboard.press("Enter")

        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(4000)

    async def get_products_links(self) -> tuple[str, ...]:
        page: Page = await self._get_page()

        products_container: Locator = page.locator("div.PLP__products")

        products_links: list[str] = await products_container.locator(
            "div[class*='container-images'] a"
        ).evaluate_all("e => e.map(el => el.href)")

        return tuple(products_links)

    async def get_product_data_batch(
        self, product_links: tuple[str, ...], batch_size: int = 10
    ) -> None:
        data: list[dict[str, Any]] = list()
        for i in range(0, len(product_links), batch_size):
            batch = product_links[i : i + batch_size]
            batch_data = await gather(*[self.get_product_data(link) for link in batch])
            data.extend([item.model_dump() for item in batch_data])

        save_data(
            data=data,
            filename=f"oe_products_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json",
            destination_dir=OECHSLE_DATA,
        )

    async def get_product_data(self, product_link: str) -> Product:
        product_page: Page = await self.context.new_page()
        await product_page.goto(product_link)
        await product_page.wait_for_load_state("domcontentloaded")

        script = await product_page.evaluate("""
            () => {
                const scripts = document.querySelectorAll('script[type="application/ld+json"]');
                try {
                    const script = Array.from(scripts).find(script => script.textContent);
                    return JSON.parse(script.textContent);                          
                } catch (e) {}
                return null;
            }
        """)

        name: str = script["name"]
        brand: str = script["brand"]["name"]

        price_container: Locator = product_page.locator("#containerPrice")

        price: Decimal
        original_price: Decimal | None
        price, original_price = await get_prices(price_container)

        discount: str | None = await get_discount(price_container)

        availability_container: Locator = product_page.locator(
            "#text-available-product"
        )
        availability: bool = await get_availability(availability_container)

        currency: str = script["offers"]["priceCurrency"]

        await product_page.close()

        return Product(
            name=name.strip(),
            brand=brand.strip(),
            price=str(price),
            original_price=str(original_price) if original_price else None,
            discount=discount,
            currency=currency,
            availability=availability,
            rating=None,
            review_count=None,
            url=product_link,
            source="oechsle",
            scraped_at=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        )
