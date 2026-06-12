from urllib.parse import urlparse


def check_url_format(url: str) -> bool:
    if not url.startswith(("http://", "https://")):
        return False
    return True


def check_url_length(url: str, max_length: int = 2048) -> bool:
    return len(url) <= max_length


def check_url_domain_zone(url: str, allowed_domains_zone: list[str]) -> bool:
    domain = urlparse(url).hostname
    if domain is None:
        return False
    return any(domain.endswith(allowed) for allowed in allowed_domains_zone)
