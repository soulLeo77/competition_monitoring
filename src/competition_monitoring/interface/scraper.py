from abc import ABC, abstractmethod

from ..models.product import Product


class BaseScraper(ABC):
    @abstractmethod
    async def go_to_product_page(self, category: str) -> None:
        pass

    @abstractmethod
    async def get_products_links(self) -> tuple[str, ...]:
        pass

    @abstractmethod
    async def get_product_data(self, product_link: str) -> Product:
        pass
