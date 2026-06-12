from decimal import Decimal
from re import compile

from patchright.async_api import Locator

from .prices import parse_price


async def get_prices(container: Locator) -> tuple[Decimal, Decimal | None]:
    raw_price: str = await container.locator("p[class='price']").inner_text()
    raw_original_price: str | None = None
    if await (ori_price_cont := container.locator("p.priceList")).count() > 0:
        raw_original_price = await ori_price_cont.inner_text()

    pattern = compile(r"\b\d{1,3}(?:,\d{3})*\.\d{2}\b")

    _match_price = pattern.search(raw_price)

    if not _match_price:
        raise ValueError(f"Invalid price: {raw_price}")

    price: Decimal = parse_price(_match_price.group(0))

    original_price: Decimal | None = None
    if raw_original_price:
        _match_original_price = pattern.search(raw_original_price)

        if _match_original_price:
            original_price = parse_price(_match_original_price.group(0))

    return price, original_price


async def get_discount(container: Locator) -> str | None:
    discount: str | None = None
    if (
        await (
            discount_cont := container.locator("p[class='price'] span.percentage")
        ).count()
        > 0
    ):
        discount = await discount_cont.inner_text()
    return discount


async def get_availability(container: Locator) -> bool:
    if await container.count() > 0:
        return True
    return False
