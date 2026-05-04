from pydantic import BaseModel


class Product(BaseModel):
    name: str
    brand: str
    price: str
    original_price: str | None
    discount: str | None
    currency: str
    availability: bool
    rating: str | None
    review_count: str | None
    url: str
    source: str
    scraped_at: str
