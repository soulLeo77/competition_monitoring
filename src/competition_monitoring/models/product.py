from datetime import datetime

from pydantic import BaseModel


class Product(BaseModel):
    name: str
    brand: str
    price: float
    original_price: float | None
    discount: float | None
    currency: str
    availability: str
    rating: float | None
    review_count: int | None
    url: str
    source: str
    scraped_at: datetime
