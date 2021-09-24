from django.conf import settings
from django.urls import path
from rest_framework.routers import DefaultRouter, SimpleRouter

from core.tournament.views import tournament, tour, match


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


app_name = "tournaments"

router.register("matches", match.MatchViewSet, basename="matches")
router.register("tours", tour.TourViewSet, basename="tours")
router.register("", tournament.TournamentViewSet)

urlpatterns = [
    path("matches/<int:pk>/game/<uuid:game>/", match.MatchGameViewSet.as_view({"delete": "destroy"})),
    path("matches/<int:pk>/game/", match.MatchGameViewSet.as_view({"post": "create"})),
    *router.urls
]
