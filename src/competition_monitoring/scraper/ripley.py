from patchright.async_api import BrowserContext, Page


class RipleyScraper:
    def __init__(self, context: BrowserContext):
        self.context: BrowserContext = context
        self.page: Page | None = None

    async def _get_page(self) -> Page:
        if self.page is None:
            self.page = await self.context.new_page()
        return self.page
