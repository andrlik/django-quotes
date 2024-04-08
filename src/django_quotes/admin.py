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


class SourceGroupAdmin(admin.ModelAdmin):
    """Model admin for SourceGroup."""

    pass


class SourceAdmin(admin.ModelAdmin):
    """Model admin for Source."""

    pass


class QuoteAdmin(admin.ModelAdmin):
    """Model admin for Quote."""

    pass


class GroupStatsAdmin(admin.ModelAdmin):
    """Model admin for GroupStats"""

    pass


class SourceStatAdmin(admin.ModelAdmin):
    """Model admin for SourceStats"""

    pass


class QuoteStatAdmin(admin.ModelAdmin):
    """Model admin for QuoteStats"""

    pass


admin.site.register(SourceGroup, SourceGroupAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(GroupStats, GroupStatsAdmin)
admin.site.register(SourceStats, SourceStatAdmin)
admin.site.register(QuoteStats, QuoteStatAdmin)
