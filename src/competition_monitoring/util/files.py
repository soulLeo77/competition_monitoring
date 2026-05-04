from pathlib import Path
from typing import Any
from json import dump


def save_data(data: list[dict[str, Any]], filename: str, destination_dir: Path) -> None:
    file_path: Path = destination_dir / filename

    with file_path.open("w", encoding="utf-8") as f:
        dump(data, f, ensure_ascii=False, indent=4)
