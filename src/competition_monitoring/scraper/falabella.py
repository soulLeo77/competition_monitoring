from decimal import Decimal
from asyncio import gather

from patchright.async_api import BrowserContext, Locator, Page

from ..util.falabella import (
    get_prices_and_currency,
    determine_availability,
    get_rating,
    get_review_count,
)
from ..util.files import save_data
from ..paths import FALABELLA_DATA
from ..models.product import Product
from datetime import datetime
from typing import Any


class FalabellaScraper:

    BASE_URL: str = "https://www.falabella.com.pe/falabella-pe/"

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

        search_bar: Locator = page.locator("input#testId-SearchBar-Input")
        await search_bar.fill(category)
        await search_bar.press("Enter")

        await page.wait_for_load_state("domcontentloaded")

    async def get_product_links(self) -> tuple[str, ...]:
        page: Page = await self._get_page()

        products_container: Locator = page.locator("div#testId-searchResults-products")
        product_links: list[str] = await products_container.locator("a").evaluate_all(
            "elements => elements.map(el => el.href)"
        )
        return tuple(product_links)

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
            filename=f"fb_products_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json",
            destination_dir=FALABELLA_DATA,
        )

    async def get_product_data(self, product_link: str) -> Product:
        product_page: Page = await self.context.new_page()
        await product_page.goto(product_link)
        await product_page.wait_for_load_state("domcontentloaded")

        data_section: Locator = product_page.locator(
            "section.modern-pdp__details-section"
        )

        basic_info_container: Locator = data_section.locator("div.pdp-basic-info")

        brand_container: Locator = basic_info_container.locator(
            "div[class*='header'] a"
        )
        brand: str = await brand_container.inner_text()

        name_container: Locator = basic_info_container.locator("h1")
        name: str = await name_container.inner_text()

        specifications_container: Locator = data_section.locator(
            "div.product-specifications"
        )

        prices_container: Locator = specifications_container.locator(
            "div.prices-container"
        )
        prices_list: list[str] = await prices_container.locator(
            "div[id^='testId-pod-prices-'] li"
        ).evaluate_all("elements => elements.map(el => el.innerText)")

        price: Decimal
        original_price: Decimal | None
        currency: str
        price, original_price, currency = get_prices_and_currency(prices_list)

        discount_container: Locator = prices_container.locator(
            "span[id^='testId-Pod-badges-']"
        )
        discount: str | None = None
        if await discount_container.count() != 0:
            discount = await discount_container.inner_text()

        availability_container: Locator = specifications_container.locator(
            "div.dlv-opt-wrapper"
        )

        await availability_container.click()
        await product_page.wait_for_load_state("domcontentloaded")

        close_form_button: Locator = product_page.locator("button[aria-label='Cerrar']")
        await close_form_button.click()
        await product_page.wait_for_load_state("domcontentloaded")

        availability_paragraphs: list[Locator] = await availability_container.locator(
            "div[id^='testId-Availability-'] p.delivery-option-selection > span"
        ).all()
        classes_texts: list[str | None] = [
            await paragraph.get_attribute("class")
            for paragraph in availability_paragraphs
        ]
        availability: bool = determine_availability(classes_texts)

        rating_container: Locator = basic_info_container.locator("div.rr-rating-stars")
        raw_rating: str = await rating_container.locator(
            "> div > span"
        ).first.inner_text()
        rating: str | None = get_rating(raw_rating)

        review_count: str | None = get_review_count(raw_rating)

        await product_page.close()

        return Product(
            name=name,
            brand=brand,
            price=str(price),
            original_price=str(original_price) if original_price else None,
            discount=discount,
            currency=currency,
            availability=availability,
            rating=rating,
            review_count=review_count,
            url=product_link,
            source="falabella",
            scraped_at=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        )
