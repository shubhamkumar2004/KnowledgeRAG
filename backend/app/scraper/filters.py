from urllib.parse import urlparse

SKIP_EXTENSIONS = {
    ".pdf",
    ".doc",
    ".docx",
    ".jpg",
    ".jpeg",
    ".png",
    ".gif",
    ".zip",
    ".rar",
}

SKIP_KEYWORDS = {
    "login",
    "logout",
    "admin",
}


def should_process(url: str) -> bool:
    """
    Return True if the URL should be processed.
    """

    parsed = urlparse(url)

    lower_url = url.lower()
    path = parsed.path.lower()

    # Skip email links
    if "@" in path:
        return False

    # Skip mailto, tel and javascript links
    if parsed.scheme in {"mailto", "tel", "javascript"}:
        return False

    # Skip anchors
    if parsed.fragment:
        return False

    # Skip unwanted keywords
    for keyword in SKIP_KEYWORDS:
        if keyword in lower_url:
            return False

    # Skip unwanted file extensions
    for ext in SKIP_EXTENSIONS:
        if path.endswith(ext):
            return False

    return True