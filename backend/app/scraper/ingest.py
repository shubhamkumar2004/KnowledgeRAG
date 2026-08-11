from urllib.parse import urlparse, parse_qs

from app.scraper.crawler import get_internal_links
from app.scraper.filters import should_process
from app.scraper.parser import download_page
from app.scraper.cleaner import clean_page
from app.scraper.saver import save_page

BASE_URL = "https://ektatrust.org.in"

def filename_from_url(url: str) -> str:
    parsed = urlparse(url)

    path = parsed.path.strip("/")

    if not path:
        filename = "home"
    else:
        filename = path.replace("/", "_")

    query = parse_qs(parsed.query)

    if "ExamType" in query:
        filename += "_" + query["ExamType"][0]

    return filename + ".txt"
 
def ingest():
    """
    Crawl the website and save cleaned text from each valid page.
    """

    urls = get_internal_links(BASE_URL)

    print(f"\nFound {len(urls)} URLs\n")

    for url in urls:

        if not should_process(url):
            print(f"⏭️ Skipping: {url}")
            continue

        print(f"⬇️ Downloading: {url}")

        soup = download_page(url)

        text = clean_page(soup)

        filename = filename_from_url(url)

        save_page(filename, text)

        print(f"✅ Saved: {filename}")


if __name__ == "__main__":
    ingest()