from re import compile
from pathlib import Path
from ..paths import FALABELLA_DATA
from typing import Any
from json import dump
from decimal import Decimal
from .prices import parse_price, determine_currency


def determine_availability(texts: list[str | None]) -> bool:
    for class_text in texts:
        if not class_text:
            continue

        if "green" in class_text:
            return True

    return False


def get_rating(text: str) -> str | None:
    rating_pattern = compile(r"^\s*([0-9]+(?:\.[0-9]+)?)\s*\(")
    _match = rating_pattern.search(text)
    if not _match:
        return None

    return _match.group(1)


def get_prices_and_currency_fb(
    prices: list[str],
) -> tuple[Decimal, Decimal | None, str]:
    count_prices = len(prices)
    _price: str
    _original_price: str
    price: Decimal
    original_price: Decimal | None

    if count_prices == 3:
        _price = prices[1]
        _original_price = prices[2]
        price = parse_price(_price)
        original_price = parse_price(_original_price)
    elif count_prices == 2:
        _price = prices[0]
        _original_price = prices[1]
        price = parse_price(_price)
        original_price = parse_price(_original_price)
    else:
        _price = prices[0]
        price = parse_price(_price)
        original_price = None

    currency: str = determine_currency(_price)

    return price, original_price, currency


def save_data(data: list[dict[str, Any]], filename: str) -> None:
    file_path: Path = FALABELLA_DATA / filename
    with file_path.open("w", encoding="utf-8") as f:
        dump(data, f, ensure_ascii=False, indent=4)
