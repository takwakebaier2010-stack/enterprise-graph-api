
import asyncio

import strawberry
from strawberry.extensions import QueryDepthLimiter
from core.schema import schema
from core.schema_optimized import schema_optimized


@strawberry.type
class Level4:
    value: str = "test"


@strawberry.type
class Level3:
    child: Level4


@strawberry.type
class Level2:
    child: Level3


@strawberry.type
class Level1:
    child: Level2


@strawberry.type
class SecurityQuery:
    level: Level1


def test_query_depth_limiter_blocks_deep_queries():
    test_schema = strawberry.Schema(
        query=SecurityQuery,
        extensions=[
            lambda: QueryDepthLimiter(max_depth=2)
        ],
    )

    query = """
    {
        level {
            child {
                child {
                    child {
                        value
                    }
                }
            }
        }
    }
    """

    result = test_schema.execute_sync(query)

    assert result.errors is not None
    assert "exceeds maximum operation depth" in result.errors[0].message


def test_max_aliases_limiter_blocks_too_many_aliases():
    query = """
    {
        a: __typename
        b: __typename
        c: __typename
        d: __typename
        e: __typename
        f: __typename
        g: __typename
        h: __typename
        i: __typename
        j: __typename
        k: __typename
    }
    """

    result = schema.execute_sync(query)
    assert result.errors is not None 
def test_normal_query_is_allowed():
    query = """
    {
        __typename
    }
    """

    result = schema.execute_sync(query)

    assert result.errors is None


def test_optimized_schema_blocks_queries_over_depth_limit():
    query = """
    {
        organizers {
            events {
                organizer {
                    events {
                        organizer {
                            events {
                                organizer { name }
                            }
                        }
                    }
                }
            }
        }
    }
    """

    result = asyncio.run(
        schema_optimized.execute(query, context_value={"loaders": {}})
    )

    assert result.errors is not None
    assert "exceeds maximum operation depth" in result.errors[0].message


def test_optimized_schema_blocks_more_than_ten_aliases():
    aliases = "\n".join(f"alias{i}: __typename" for i in range(11))
    result = asyncio.run(
        schema_optimized.execute(
            "{\n" + aliases + "\n}", context_value={"loaders": {}}
        )
    )

    assert result.errors is not None
    assert "aliases found. Allowed: 10" in result.errors[0].message
