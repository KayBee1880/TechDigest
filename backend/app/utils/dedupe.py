import hashlib
from urllib.parse import parse_qsl, urlencode, urlsplit, urlunsplit

TRACKING_PARAM_PREFIXES = ("utm_",)


def canonicalize_url(url: str) -> str:
    parts = urlsplit(url)
    host = parts.netloc.lower()
    path = parts.path.rstrip("/")

    query_pairs = sorted(
        (key, value)
        for key, value in parse_qsl(parts.query)
        if not key.lower().startswith(TRACKING_PARAM_PREFIXES)
    )
    query = urlencode(query_pairs)

    return urlunsplit((parts.scheme, host, path, query, ""))


def hash_title(title: str) -> str:
    normalized = title.strip().lower()
    return hashlib.sha256(normalized.encode("utf-8")).hexdigest()
