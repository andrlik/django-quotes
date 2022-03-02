from django.urls import path

from .views import (
    QuoteCreateView,
    QuoteDeleteView,
    QuoteDetailView,
    QuoteListView,
    QuoteUpdateView,
    SourceCreateView,
    SourceDeleteView,
    SourceDetailView,
    SourceGroupCreateView,
    SourceGroupDeleteView,
    SourceGroupDetailView,
    SourceGroupListView,
    SourceGroupUpdateView,
    SourceListView,
    SourceUpdateView,
)

app_name = "quotes"
urlpatterns = [
    path("groups/", view=SourceGroupListView.as_view(), name="group_list"),
    path("groups/create/", view=SourceGroupCreateView.as_view(), name="group_create"),
    path(
        "groups/<slug:group>/",
        view=SourceGroupDetailView.as_view(),
        name="group_detail",
    ),
    path(
        "groups/<slug:group>/edit/",
        view=SourceGroupUpdateView.as_view(),
        name="group_update",
    ),
    path(
        "groups/<slug:group>/delete/",
        view=SourceGroupDeleteView.as_view(),
        name="group_delete",
    ),
    path(
        "groups/<slug:group>/characters/",
        view=SourceListView.as_view(),
        name="character_list",
    ),
    path(
        "groups/<slug:group>/characters/add/",
        view=SourceCreateView.as_view(),
        name="character_create",
    ),
    path(
        "characters/<slug:character>/",
        view=SourceDetailView.as_view(),
        name="character_detail",
    ),
    path(
        "characters/<slug:character>/edit/",
        view=SourceUpdateView.as_view(),
        name="character_update",
    ),
    path(
        "characters/<slug:character>/delete/",
        view=SourceDeleteView.as_view(),
        name="character_delete",
    ),
    path(
        "characters/<slug:character>/quotes/",
        view=QuoteListView.as_view(),
        name="quote_list",
    ),
    path(
        "characters/<slug:character>/quotes/add/",
        view=QuoteCreateView.as_view(),
        name="quote_create",
    ),
    path("quotes/<int:quote>/", view=QuoteDetailView.as_view(), name="quote_detail"),
    path(
        "quotes/<int:quote>/edit/", view=QuoteUpdateView.as_view(), name="quote_update"
    ),
    path(
        "quotes/<int:quote>/delete/",
        view=QuoteDeleteView.as_view(),
        name="quote_delete",
    ),
]
