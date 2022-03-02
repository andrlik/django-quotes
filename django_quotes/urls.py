from django.urls import path

from .views import (
    CharacterCreateView,
    CharacterDeleteView,
    CharacterDetailView,
    CharacterGroupCreateView,
    CharacterGroupDeleteView,
    CharacterGroupDetailView,
    CharacterGroupListView,
    CharacterGroupUpdateView,
    CharacterListView,
    CharacterUpdateView,
    QuoteCreateView,
    QuoteDeleteView,
    QuoteDetailView,
    QuoteListView,
    QuoteUpdateView,
)

app_name = "quotes"
urlpatterns = [
    path("groups/", view=CharacterGroupListView.as_view(), name="group_list"),
    path(
        "groups/create/", view=CharacterGroupCreateView.as_view(), name="group_create"
    ),
    path(
        "groups/<slug:group>/",
        view=CharacterGroupDetailView.as_view(),
        name="group_detail",
    ),
    path(
        "groups/<slug:group>/edit/",
        view=CharacterGroupUpdateView.as_view(),
        name="group_update",
    ),
    path(
        "groups/<slug:group>/delete/",
        view=CharacterGroupDeleteView.as_view(),
        name="group_delete",
    ),
    path(
        "groups/<slug:group>/characters/",
        view=CharacterListView.as_view(),
        name="character_list",
    ),
    path(
        "groups/<slug:group>/characters/add/",
        view=CharacterCreateView.as_view(),
        name="character_create",
    ),
    path(
        "characters/<slug:character>/",
        view=CharacterDetailView.as_view(),
        name="character_detail",
    ),
    path(
        "characters/<slug:character>/edit/",
        view=CharacterUpdateView.as_view(),
        name="character_update",
    ),
    path(
        "characters/<slug:character>/delete/",
        view=CharacterDeleteView.as_view(),
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
