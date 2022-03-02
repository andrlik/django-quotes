from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from django_quotes.api.views import CharacterGroupViewSet, CharacterViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("groups", CharacterGroupViewSet, basename="group")
router.register("characters", CharacterViewSet, basename="character")


app_name = "api"
urlpatterns = router.urls
