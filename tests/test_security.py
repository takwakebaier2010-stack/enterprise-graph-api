
from strawberry.extensions import QueryDepthLimiter, MaxAliasesLimiter
from core.schema import schema


def test_query_depth_limiter_is_enabled():
    assert any(
        isinstance(extension, QueryDepthLimiter)
        for extension in schema.extensions
    )


def test_max_aliases_limiter_is_enabled():
    assert any(
        isinstance(extension, MaxAliasesLimiter)
        for extension in schema.extensions
    )
