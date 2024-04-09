#
# apps.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

from django.apps import AppConfig
from django.utils.translation import gettext_lazy as _


class QuotesConfig(AppConfig):
    """App configuration for django_quotes app.
    Notably loads the receivers so that signals will be processed.
    """

    default_auto_field = "django.db.models.BigAutoField"
    name = "django_quotes"
    verbose_name = _("Quotes")

    def ready(self):
        """Load the receivers."""
        try:
            import django_quotes.receivers  # noqa F401
        except ImportError:  # pragma: nocover
            pass
