
import strawberry
import strawberry_django
from strawberry import auto
from strawberry.extensions import QueryDepthLimiter, MaxAliasesLimiter

from core import models


@strawberry_django.type(models.Organizer)
class OrganizerType:
    id: auto
    name: auto
    country: auto


@strawberry.type
class Query:
    organizers: list[OrganizerType] = strawberry_django.field()


schema = strawberry.Schema(
    query=Query,
    extensions=[
        lambda: QueryDepthLimiter(max_depth=5),
        lambda: MaxAliasesLimiter(max_alias_count=10),
    ],
)
