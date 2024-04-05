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
    pass


class SourceAdmin(admin.ModelAdmin):
    pass


class QuoteAdmin(admin.ModelAdmin):
    pass


class SourceMarkovModelAdmin(admin.ModelAdmin):
    pass


class GroupMarkovModelAdmin(admin.ModelAdmin):
    pass


class GroupStatsAdmin(admin.ModelAdmin):
    pass


class SourceStatAdmin(admin.ModelAdmin):
    pass


class QuoteStatAdmin(admin.ModelAdmin):
    pass


admin.site.register(SourceGroup, SourceGroupAdmin)
admin.site.register(Source, SourceAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(GroupStats, GroupStatsAdmin)
admin.site.register(SourceStats, SourceStatAdmin)
admin.site.register(QuoteStats, QuoteStatAdmin)
