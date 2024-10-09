# api_router.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from django.conf import settings
from rest_framework.routers import DefaultRouter, SimpleRouter

from django_quotes.api.views import SourceGroupViewSet, SourceViewSet

if settings.DEBUG:
    router = DefaultRouter()
else:
    router = SimpleRouter()

router.register("groups", SourceGroupViewSet, basename="group")
router.register("sources", SourceViewSet, basename="source")


app_name = "api"
urlpatterns = router.urls
