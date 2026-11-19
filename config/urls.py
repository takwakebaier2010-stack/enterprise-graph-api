from django.contrib import admin
from django.urls import path
from strawberry.django.views import GraphQLView

from core.schema import schema
from core.schema_optimized import schema_optimized
from core.views import OptimizedGraphQLView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("graphql/", GraphQLView.as_view(schema=schema)),
    path("graphql-optimized/", OptimizedGraphQLView.as_view(schema=schema_optimized)),
]