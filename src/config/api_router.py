from api.views import EloViewSet, GameViewSet
from core.chess.api.views import SlideViewSet
from core.files.views import ImageViewSet
from core.tournament.views import TimeControlTypeViewSet, DrawTypeViewSet
from core.tournament.views import tournament
from core.users.api.views import UserViewSet
from core.feedback.api.views import FeedbackViewSet
from django.conf import settings
from django.urls import path, include
from rest_framework.routers import DefaultRouter, SimpleRouter


if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()


router.register("users", UserViewSet)
router.register("game", GameViewSet)
router.register("elo", EloViewSet)
router.register("slides", SlideViewSet)
router.register("feedbacks", FeedbackViewSet)
router.register("images", ImageViewSet)
router.register("tournament-types", tournament.TournamentTypeViewSet)
router.register("draw-type", DrawTypeViewSet)
router.register("time-control-type", TimeControlTypeViewSet)

app_name = "api"
urlpatterns = [
    path("tournaments/", include('core.tournament.urls')),
    *router.urls
]
