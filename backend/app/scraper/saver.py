from pathlib import Path


OUTPUT_DIR = Path("data/raw")
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)


def save_page(filename: str, text: str):

    output_file = OUTPUT_DIR / filename

    output_file.write_text(text, encoding="utf-8")