from decimal import Decimal
from re import sub


def clean_price(price_str: str) -> str:
    return sub(r"[^\d.]", "", price_str)


def parse_price(price_str: str) -> Decimal:
    cleaned_price: str = clean_price(price_str)
    return Decimal(cleaned_price)


def determine_currency(price: str) -> str:
    return sub(r"[\d.,]", "", price).strip()
