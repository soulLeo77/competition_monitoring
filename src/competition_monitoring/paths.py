from pathlib import Path

_PROYECT_DIR: Path = Path(__file__).parents[2]
_DATA_DIR: Path = _PROYECT_DIR / ".data"
_PRODUCTS_DATA_DIR: Path = _DATA_DIR / "products"
FALABELLA_DATA: Path = _PRODUCTS_DATA_DIR / "falabella"
RIPLEY_DATA: Path = _PRODUCTS_DATA_DIR / "ripley"

for dir in (_DATA_DIR, _PRODUCTS_DATA_DIR, FALABELLA_DATA, RIPLEY_DATA):
    dir.mkdir(exist_ok=True, parents=True)
