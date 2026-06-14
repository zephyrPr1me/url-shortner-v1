from urllib.parse import urlparse


def check_url_length(url: str, max_length: int = 2048) -> bool:
    """Check if the URL length does not exceed max_length."""
    return len(url) <= max_length


def is_valid_url(url: str) -> bool:
    """
    Perform sanity checks on the URL structure.
    Pydantic's HttpUrl handles basic RFC validation, but we can verify
    additional constraints (e.g. hostname/netloc exists).
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except Exception:
        return False
