from decimal import Decimal
from .prices import parse_price, determine_currency
from re import compile


def get_prices_and_currency(
    prices: list[str],
) -> tuple[Decimal, Decimal | None, str]:
    count_prices = len(prices)
    _price: str
    _original_price: str
    price: Decimal
    original_price: Decimal | None

    if count_prices in (
        3,
        2,
    ):
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


def get_rating(raw_rating: str) -> str | None:
    rating_pattern = compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*")

    if not (_match := rating_pattern.search(raw_rating)):
        return None

    return _match.group(1)


def get_review_count(raw_review_count: str) -> str | None:
    review_count_pattern = compile(r"\((\d+).*\)")
    if not (_match := review_count_pattern.search(raw_review_count)):
        return None

    return _match.group(1)
