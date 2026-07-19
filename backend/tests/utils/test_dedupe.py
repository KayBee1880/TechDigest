from app.utils.dedupe import canonicalize_url, hash_title


def test_canonicalize_url_lowercases_host():
    assert canonicalize_url("https://Example.COM/article") == "https://example.com/article"


def test_canonicalize_url_strips_utm_params():
    url = "https://example.com/article?utm_source=twitter&id=5"
    assert canonicalize_url(url) == "https://example.com/article?id=5"


def test_canonicalize_url_sorts_remaining_params():
    first = canonicalize_url("https://example.com/article?b=2&a=1")
    second = canonicalize_url("https://example.com/article?a=1&b=2")

    assert first == second


def test_canonicalize_url_strips_trailing_slash():
    assert canonicalize_url("https://example.com/article/") == "https://example.com/article"


def test_hash_title_ignores_case_and_whitespace():
    assert hash_title("  Some Title  ") == hash_title("some title")


def test_hash_title_differs_for_different_titles():
    assert hash_title("Title One") != hash_title("Title Two")


def test_hash_title_returns_sha256_hex_length():
    assert len(hash_title("Any title")) == 64
