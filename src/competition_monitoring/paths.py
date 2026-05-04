from pathlib import Path

_PROYECT_DIR: Path = Path(__file__).parents[2]
_DATA_DIR: Path = _PROYECT_DIR / ".data"
_PRODUCTS_DATA_DIR: Path = _DATA_DIR / "products"
FALABELLA_DATA: Path = _PRODUCTS_DATA_DIR / "falabella"

for dir in (_DATA_DIR, _PRODUCTS_DATA_DIR, FALABELLA_DATA):
    dir.mkdir(exist_ok=True, parents=True)
