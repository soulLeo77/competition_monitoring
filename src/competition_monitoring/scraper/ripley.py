from asyncio import gather
from datetime import datetime
from typing import Any

from patchright.async_api import BrowserContext, Frame, Locator, Page, Request

from ..interface.scraper import BaseScraper
from ..models.product import Product
from ..paths import RIPLEY_DATA
from ..util.files import save_data
from ..util.ripley import get_prices_and_currency, get_rating, get_review_count


class RipleyScraper(BaseScraper):

    BASE_URL: str = "https://simple.ripley.com.pe/"

    def __init__(self, context: BrowserContext):
        self.context: BrowserContext = context
        self.page: Page | None = None

    async def _get_page(self) -> Page:
        if self.page is None:
            self.page = await self.context.new_page()
        return self.page

    async def go_to_home_page(self) -> None:
        page: Page = await self._get_page()
        await page.goto(self.BASE_URL)
        await page.wait_for_load_state("domcontentloaded")

    async def go_to_product_page(self, category: str) -> None:
        page: Page = await self._get_page()

        # await self._cloudflare_handler(page)
        await page.goto(self.BASE_URL)
        await page.wait_for_load_state("domcontentloaded")
        await page.wait_for_timeout(1500)
        await self._verify_cloudflare_warning(page)

        search_bar: Locator = page.locator("input[role='searchbox']")
        await search_bar.wait_for(state="visible")
        await search_bar.fill(category)
        await page.keyboard.press("Enter")

        products_container: Locator = page.locator(
            "section[data-testid='product-list']"
        )
        await products_container.wait_for()

    async def get_products_links(self) -> tuple[str, ...]:
        page: Page = await self._get_page()

        products_container: Locator = page.locator(
            "section[data-testid='product-list']"
        )
        products_links: list[str] = await products_container.locator("a").evaluate_all(
            "elements => elements.map(el => el.href)"
        )
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
            filename=f"rp_products_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.json",
            destination_dir=RIPLEY_DATA,
        )

    async def get_product_data(self, product_link: str):
        product_page: Page = await self.context.new_page()
        await product_page.goto(product_link)
        await product_page.wait_for_load_state("domcontentloaded")
        await self._verify_cloudflare_warning(product_page)

        data_section: Locator = product_page.locator(
            "div[data-testid='product-details'] div[class*='product-summary-container']"
        )

        header_container: Locator = data_section.locator(
            "div[class*='product-header-container']"
        )

        brand: str = await header_container.locator(
            "div[class*='brand-container']"
        ).inner_text()
        name: str = await header_container.locator("h1").inner_text()

        prices_container: Locator = data_section.locator(
            "div[class*='product-price-container']"
        )

        prices: list[str] = await prices_container.locator(
            "span[class*='price-value']"
        ).evaluate_all("elements => elements.map(el => el.innerText)")

        price, original_price, currency = get_prices_and_currency(prices)

        discount_container: Locator = prices_container.locator(
            "span[class*='discount-badge']"
        )
        discount: str | None = None
        if await discount_container.count() > 0:
            discount = await discount_container.inner_text()

        raiting_container: Locator = product_page.locator(
            "div[class*='rating-and-reviews--content'] div.rating-and-reviews--summary-rating"
        )
        raw_rating: str | None = None
        raw_review_count: str | None = None

        if await raiting_container.count() > 0:
            raw_rating = await raiting_container.locator("strong").inner_text()
            raw_review_count = await raiting_container.locator("span").inner_text()

        rating: str | None = get_rating(raw_rating) if raw_rating else None
        review_count: str | None = (
            get_review_count(raw_review_count) if raw_review_count else None
        )

        await product_page.wait_for_timeout(2000)
        await product_page.close()

        return Product(
            name=name,
            brand=brand,
            price=str(price),
            original_price=str(original_price) if original_price else None,
            discount=discount,
            currency=currency,
            availability=True,
            rating=rating,
            review_count=review_count,
            url=product_link,
            source="Ripley",
            scraped_at=datetime.now().strftime("%Y-%m-%d_%H-%M-%S"),
        )

    async def _verify_cloudflare_warning(self, page: Page) -> None:
        element = page.locator("*", has_text="seguridad en curso").nth(0)
        is_visible = await element.is_visible()

        if is_visible:
            await element.wait_for(state="detached")
            await element.wait_for(state="hidden")
