from types import SimpleNamespace

import pytest

from utils.helpers import validate_origin


@pytest.mark.parametrize("candidate,allowed,expected", [
    ("https://example.com", ["https://example.com"], True),
    ("https://example.com.attacker.test", ["https://example.com"], False),
    ("https://example.com:444", ["https://example.com"], False),
    ("http://example.com", ["https://example.com"], False),
    ("https://example.com/path", ["https://example.com"], False),
    ("https://example.com", ["https://example.com/"], True),
    ("", ["https://example.com"], False),
])
def test_origin_validation_requires_exact_origin(candidate, allowed, expected):
    request = SimpleNamespace(headers={"Origin": candidate} if candidate else {})
    assert validate_origin(request, allowed) is expected


def test_invalid_origin_header_does_not_fall_back_to_valid_referer():
    request = SimpleNamespace(headers={
        "Origin": "https://example.com.attacker.test",
        "Referer": "https://example.com/page"
    })
    assert validate_origin(request, ["https://example.com"]) is False
