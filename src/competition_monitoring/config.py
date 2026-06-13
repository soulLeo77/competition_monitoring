from dataclasses import dataclass, field
from datetime import datetime
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
    output_path: Path = (
        REPORTS_DIR
        / f"products_report_{datetime.now().strftime('%Y-%m-%d_%H-%M-%S')}.xlsx"
    )
    batch_size: int = 5
    headless: bool = False
