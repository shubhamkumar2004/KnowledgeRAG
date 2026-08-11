from urllib.parse import urljoin, urlparse

import requests
from bs4 import BeautifulSoup

from app.scraper.filters import should_process

BASE_URL = "https://ektatrust.org.in"


def normalize_url(url: str) -> str:
    parsed = urlparse(url)

    path = parsed.path.rstrip("/")

    normalized = f"{parsed.scheme}://{parsed.netloc}{path}"

    if parsed.query:
        normalized += f"?{parsed.query}"

    return normalized


def get_internal_links(url: str) -> list[str]:
    """
    Download one page and return all valid internal links.
    """

    response = requests.get(url, timeout=15)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")

    links = {}

    base_domain = urlparse(BASE_URL).netloc

    for tag in soup.find_all("a", href=True):

        href = tag["href"]

        # Convert relative URL to absolute URL
        absolute_url = urljoin(BASE_URL, href)

        # Normalize URL
        absolute_url = normalize_url(absolute_url)

        parsed = urlparse(absolute_url)

        # Ignore external websites
        if parsed.netloc != base_domain:
            continue

        # Ignore unwanted URLs
        if not should_process(absolute_url):
            continue

        path = parsed.path.strip("/")

        if path.endswith(".aspx"):
            key = path[:-5]
        else:
            key = path

        if key not in links:
            links[key] = absolute_url

        elif absolute_url.endswith(".aspx"):
            links[key] = absolute_url

    return sorted(links.values())


if __name__ == "__main__":

    urls = get_internal_links(BASE_URL)

    print(f"\nFound {len(urls)} internal pages:\n")

    for url in urls:
        print(url)