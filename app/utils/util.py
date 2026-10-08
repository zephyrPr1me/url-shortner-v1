import secrets
import string
from urllib.parse import urlparse


def check_url_length(url: str, max_length: int = 2048) -> bool:
    """Check if the URL length does not exceed max_length."""
    return len(url) <= max_length


def is_valid_url(url: str) -> bool:
    """
    Perform sanity checks on the URL structure.
    Pydantic's HttpUrl handles basic RFC validation, but we also verify
    that netloc (hostname) is present.
    """
    try:
        parsed = urlparse(url)
        return bool(parsed.scheme in ("http", "https") and parsed.netloc)
    except (TypeError, ValueError):
        return False


def check_self_shortening(url: str, base_url: str) -> bool:
    """
    Returns True if the target URL points to the same host as this service.
    Used to prevent redirect loops (self-shortening attacks).

    Example:
        check_self_shortening("https://shrt.io/abc", "https://shrt.io") -> True
        check_self_shortening("https://google.com", "https://shrt.io") -> False
    """
    try:
        target_host = urlparse(url).hostname or ""
        service_host = urlparse(base_url).hostname or ""
        return target_host == service_host
    except (TypeError, ValueError):
        return False


def generate_short_id(length: int = 6):
    chars = string.ascii_letters + string.digits
    return "".join(secrets.choice(chars) for _ in range(length))
