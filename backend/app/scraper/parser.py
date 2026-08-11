import requests
from bs4 import BeautifulSoup


def download_page(url: str) -> BeautifulSoup:
    response = requests.get(url, timeout=15)
    response.raise_for_status()

    print("=" * 80)
    print("Requested :", url)
    print("Final URL :", response.url)
    print("Status    :", response.status_code)

    # Save the raw HTML for inspection
    with open("debug.html", "w", encoding="utf-8") as f:
        f.write(response.text)

    soup = BeautifulSoup(response.text, "html.parser")

    print("Title :", soup.title)

    return soup