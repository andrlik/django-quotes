#
# admin.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

from django.contrib import admin

from django_quotes.models import (
    GroupStats,
    Quote,
    QuoteStats,
    Source,
    SourceGroup,
    SourceStats,
)

# Register your models here.


@admin.register(SourceGroup)
class SourceGroupAdmin(admin.ModelAdmin):
    """Model admin for SourceGroup."""

    pass


@admin.register(Source)
class SourceAdmin(admin.ModelAdmin):
    """Model admin for Source."""

    pass


@admin.register(Quote)
class QuoteAdmin(admin.ModelAdmin):
    """Model admin for Quote."""

    pass


@admin.register(GroupStats)
class GroupStatsAdmin(admin.ModelAdmin):
    """Model admin for GroupStats"""

    pass


@admin.register(SourceStats)
class SourceStatAdmin(admin.ModelAdmin):
    """Model admin for SourceStats"""

    pass


@admin.register(QuoteStats)
class QuoteStatAdmin(admin.ModelAdmin):
    """Model admin for QuoteStats"""

    pass
