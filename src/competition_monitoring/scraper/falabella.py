from patchright.async_api import BrowserContext, Locator, Page


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
        await page.wait_for_load_state("networkidle")

        search_bar: Locator = page.locator("input#testId-SearchBar-Input")
        await search_bar.fill(category)
        await search_bar.press("Enter")

        await page.wait_for_load_state("networkidle")

    async def get_product_links(self): ...
