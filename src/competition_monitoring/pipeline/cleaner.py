from re import sub, search, IGNORECASE

from ..models.product import Product

SOURCE_MAP: dict[str, str] = {
    "falabella": "Falabella",
    "ripley": "Ripley",
    "plaza_vea": "Plaza Vea",
    "oechsle": "Oechsle",
}


def normalize_source(product: Product) -> Product:
    key = product.source.strip().lower().replace(" ", "_")
    product.source = SOURCE_MAP.get(key, product.source.strip())
    return product


def clean_currency(product: Product) -> Product:
    raw = product.currency.strip()
    m = search(r"(S/|s/|US\$|\$|€)", raw, IGNORECASE)
    product.currency = m.group(1).upper().replace("S/", "S/") if m else raw[:2] if len(raw) >= 2 else raw
    return product


def clean_brand(product: Product) -> Product:
    product.brand = sub(r"\n+\d+(?:\.\d+)?$", "", product.brand).strip()
    product.brand = sub(r"\s+", " ", product.brand)
    return product


def clean_name(product: Product) -> Product:
    product.name = sub(r"\s+", " ", product.name).strip()
    return product


def clean_original_price_none(product: Product) -> Product:
    if product.original_price and product.original_price.strip().lower() == "none":
        product.original_price = None
    return product


def clean_discount(product: Product) -> Product:
    if product.discount:
        product.discount = product.discount.strip()
    return product


def clean_rating(product: Product) -> Product:
    if product.rating:
        product.rating = product.rating.strip()
    return product


def clean_review_count(product: Product) -> Product:
    if product.review_count:
        product.review_count = product.review_count.strip()
    return product


def clean_url(product: Product) -> Product:
    product.url = product.url.strip()
    return product


def clean_scraped_at(product: Product) -> Product:
    product.scraped_at = product.scraped_at.strip()
    return product


def clean_availability(product: Product) -> Product:
    if isinstance(product.availability, str):
        product.availability = product.availability.strip().lower() in ("true", "1", "yes")
    return product


def clean_product(product: Product) -> Product:
    for cleaner in (
        normalize_source,
        clean_name,
        clean_brand,
        clean_currency,
        clean_original_price_none,
        clean_discount,
        clean_rating,
        clean_review_count,
        clean_url,
        clean_scraped_at,
        clean_availability,
    ):
        product = cleaner(product)
    return product


def clean_all_products(
    products_by_store: dict[str, list[Product]],
) -> dict[str, list[Product]]:
    return {
        store: [clean_product(p) for p in products]
        for store, products in products_by_store.items()
    }
