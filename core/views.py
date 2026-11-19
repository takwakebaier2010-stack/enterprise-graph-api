from django.shortcuts import render
from strawberry.django.views import AsyncGraphQLView

from core.loaders import make_loaders


class OptimizedGraphQLView(AsyncGraphQLView):
    async def get_context(self, request, response):
        # Nouveaux loaders pour chaque requête HTTP
        return {"request": request, "response": response, "loaders": make_loaders()}
