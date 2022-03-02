from django.contrib import admin

from .models import (
    Character,
    CharacterGroup,
    CharacterMarkovModel,
    CharacterStats,
    GroupMarkovModel,
    GroupStats,
    Quote,
    QuoteStats,
)

# Register your models here.


class CharacterGroupAdmin(admin.ModelAdmin):
    pass


class CharacterAdmin(admin.ModelAdmin):
    pass


class QuoteAdmin(admin.ModelAdmin):
    pass


class CharacterMarkovModelAdmin(admin.ModelAdmin):
    pass


class GroupMarkovModelAdmin(admin.ModelAdmin):
    pass


class GroupStatsAdmin(admin.ModelAdmin):
    pass


class CharacterStatAdmin(admin.ModelAdmin):
    pass


class QuoteStatAdmin(admin.ModelAdmin):
    pass


admin.site.register(CharacterGroup, CharacterGroupAdmin)
admin.site.register(Character, CharacterAdmin)
admin.site.register(Quote, QuoteAdmin)
admin.site.register(CharacterMarkovModel, CharacterMarkovModelAdmin)
admin.site.register(GroupMarkovModel, GroupMarkovModelAdmin)
admin.site.register(GroupStats, GroupStatsAdmin)
admin.site.register(CharacterStats, CharacterStatAdmin)
admin.site.register(QuoteStats, QuoteStatAdmin)
