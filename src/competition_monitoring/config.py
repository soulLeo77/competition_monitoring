from dataclasses import dataclass, field
from pathlib import Path

from .paths import REPORTS_DIR


@dataclass
class ScraperConfig:
    categories: dict[str, list[str]] = field(
        default_factory=lambda: {
            "falabella": ["laptops"],
            "plaza_vea": ["laptops"],
            "ripley": ["laptops"],
            "oechsle": ["laptops"],
        }
    )
    output_path: Path = REPORTS_DIR / "products_report.xlsx"
    batch_size: int = 5
    headless: bool = False
