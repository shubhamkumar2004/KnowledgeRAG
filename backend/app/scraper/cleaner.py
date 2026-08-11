from bs4 import BeautifulSoup


def clean_page(soup: BeautifulSoup) -> str:
    """
    Extract useful page-specific content and remove
    common Ekta Trust website boilerplate.
    """

    # Remove HTML elements that don't contain useful chatbot content
    for tag in soup([
        "script",
        "style",
        "noscript",
        "nav",
        "header",
        "footer"
    ]):
        tag.decompose()

    # Extract visible text
    text = soup.get_text(separator="\n")

    # Remove blank lines and extra spaces
    lines = [
        line.strip()
        for line in text.splitlines()
        if line.strip()
    ]

    # -------------------------------------------------
    # Remove common News / Contact section
    # -------------------------------------------------
    if "News and Updates" in lines:
        footer_start = lines.index("News and Updates")
        lines = lines[:footer_start]

    # -------------------------------------------------
    # Remove remaining unwanted individual lines
    # -------------------------------------------------
    unwanted_lines = {
        "Toggle navigation",
        "Navigation",
        "Login",
        "Dedicated for a Better Tomorrow",
        "Website Developed & Maintained By: -",
        "Kaspro Solutions Pvt Ltd",
        "Home | Ekta Trust",
        "×",
    }

    cleaned_lines = []

    for line in lines:

        if line in unwanted_lines:
            continue

        if line.startswith("Visitors:"):
            continue

        # Remove standalone visitor counter
        if line.isdigit() and len(line) >= 5:
            continue

        cleaned_lines.append(line)

    return "\n".join(cleaned_lines)