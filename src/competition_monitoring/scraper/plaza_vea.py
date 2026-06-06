from asyncio import gather
from datetime import datetime
from decimal import Decimal
from typing import Any

from patchright.async_api import BrowserContext, Locator, Page

from ..interface.scraper import BaseScraper
from ..models.product import Product
from ..paths import PLAZA_VEA_DATA
from ..util.files import save_data
from ..util.plaza_vea import (
    determine_availability,
    get_discount,
    get_prices_and_currency,
)


class PlazaVeaScraper(BaseScraper):

    BASE_URL: str = "https://www.plazavea.com.pe/"

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
        await page.wait_for_load_state("load")
        await page.wait_for_timeout(500)

        search_bar: Locator = page.locator("input#search_box")
        await search_bar.wait_for(state="attached")
        await search_bar.fill(category)
        await page.keyboard.press("Enter")

        await page.wait_for_load_state("load")
        await page.wait_for_timeout(5000)

    async def get_products_links(self) -> tuple[str, ...]:
        page: Page = await self._get_page()

        products_container: Locator = page.locator("div[id*='section-']")

        products_links: list[str] = await products_container.locator(
            "div[class*='productImage'] a"
        ).evaluate_all("elements => elements.map(el => el.href)")

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
            filename=f"pv_products_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json",
            destination_dir=PLAZA_VEA_DATA,
        )

    async def get_product_data(self, product_link: str) -> Product:
        product_page: Page = await self.context.new_page()
        await product_page.goto(product_link)
        await product_page.wait_for_load_state("domcontentloaded")

        data_section: Locator = product_page.locator("div.ProductCard__information")

        basic_info_container: Locator = data_section.locator(
            "div.ProductCard__information__productdata"
        )

        brand_container: Locator = basic_info_container.locator("a")
        brand: str = await brand_container.inner_text()

        name_container: Locator = basic_info_container.locator("h1 > div")
        name: str = await name_container.inner_text()

        prices_section: Locator = data_section.locator("div.ProductCard__prices")

        prices_list: list[str] = await prices_section.locator(
            "div[class*='ProductCard__content']"
        ).evaluate_all("elements => elements.map(el => el.innerText)")

        price: Decimal
        original_price: Decimal | None
        currency: str
        price, original_price, currency = get_prices_and_currency(prices_list)

        discount: str | None = None
        discount_container = prices_section.locator("div[class*='tag--online']")
        if await discount_container.count() > 0:
            discount_text: str = await discount_container.inner_text()
            discount = get_discount([discount_text])

        availability_text: str = await data_section.locator(
            "div.notifyme, div[class*='stock']"
        ).first.inner_text()
        availability: bool = determine_availability(availability_text)

        await product_page.close()

        return Product(
            name=name,
            brand=brand,
            price=str(price),
            original_price=str(original_price) if original_price else None,
            discount=discount,
            currency=currency,
            availability=availability,
            rating=None,
            review_count=None,
            url=product_link,
            source="plaza_vea",
            scraped_at=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        )
