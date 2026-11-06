# Download official scheme documents into data/raw.

from pathlib import Path

import requests

DOCUMENTS = {
    "cmegp.html": "https://bankofmaharashtra.bank.in/cmegp",
    "pmegp.html": "https://bankofmaharashtra.bank.in/pmegp",
    "msme-schemes.html": "https://bankofmaharashtra.bank.in/government-schemes-for-msme",
}


def fetch_documents(
    output_dir: Path = Path("data/raw"), timeout: int = 20
) -> list[Path]:
    output_dir.mkdir(parents=True, exist_ok=True)
    downloaded: list[Path] = []
    errors: list[str] = []

    for filename, url in DOCUMENTS.items():
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()
            destination = output_dir / filename
            destination.write_text(response.text, encoding="utf-8")
            downloaded.append(destination)
        except requests.RequestException as error:
            errors.append(f"{url}: {error}")

    if errors:
        for error in errors:
            print(f"Download failed - {error}")
    return downloaded


if __name__ == "__main__":
    paths = fetch_documents()
    print(f"Downloaded {len(paths)} document(s).")
