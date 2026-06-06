import argparse
import json
import logging
from pathlib import Path

from .config import ScraperConfig
from .job import run_job

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    datefmt="%H:%M:%S",
)


def _load_config(path: str | None) -> ScraperConfig:
    if path:
        with Path(path).open("r", encoding="utf-8") as f:
            data = json.load(f)
        return ScraperConfig(**data)
    return ScraperConfig()


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Competition Monitoring - Product Scraper Pipeline"
    )
    parser.add_argument(
        "-c",
        "--config",
        help="Path to JSON config file (optional)",
    )
    parser.add_argument(
        "-o",
        "--output",
        help="Output Excel file path",
    )
    parser.add_argument(
        "--headed",
        action="store_true",
        help="Run browser in headed mode (visible)",
    )
    parser.add_argument(
        "--batch-size",
        type=int,
        default=5,
        help="Number of products to scrape concurrently (default: 5)",
    )
    args = parser.parse_args()

    config = _load_config(args.config)

    if args.output:
        config.output_path = args.output
    if args.headed:
        config.headless = False
    if args.batch_size:
        config.batch_size = args.batch_size

    output = run_job(config)
    print(f"\nReport generated: {str(output)}")


if __name__ == "__main__":
    main()
