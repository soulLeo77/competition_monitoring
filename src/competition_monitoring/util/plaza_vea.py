from decimal import Decimal
from re import compile, IGNORECASE
from .prices import parse_price, determine_currency


def determine_availability(text: str) -> bool:
    availability_patterns = [
        r"\d+\+?\s*unidades\s*disponibles",
        r"disponible",
        r"agotado",
        r"sin\s*stock",
    ]

    text_lower = text.lower()

    if "agotado" in text_lower or "sin stock" in text_lower:
        return False

    for pattern in availability_patterns:
        if compile(pattern, IGNORECASE).search(text):
            return True

    return "unidades disponibles" in text_lower or "disponible" in text_lower


def get_discount(prices: list[str]) -> str | None:
    discount_pattern = compile(r"(-\d+%)")

    for price_text in prices:
        _match = discount_pattern.search(price_text)
        if _match:
            return _match.group(1)

    return None


def get_prices_and_currency(
    prices: list[str],
) -> tuple[Decimal, Decimal | None, str]:
    count_prices = len(prices)
    _price: str
    _original_price: str
    price: Decimal
    original_price: Decimal | None

    if count_prices >= 3:
        _price = prices[1]
        _original_price = prices[0]
        price = parse_price(_price)
        original_price = parse_price(_original_price)
    elif count_prices == 2:
        _price = prices[1]
        _original_price = prices[0]
        price = parse_price(_price)
        original_price = parse_price(_original_price)
    else:
        _price = prices[0]
        price = parse_price(_price)
        original_price = None

    currency: str = determine_currency(_price)

    return price, original_price, currency
