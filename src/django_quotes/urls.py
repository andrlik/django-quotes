#
# urls.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

"""Url patterns for application."""

from django.urls import path

from django_quotes.views import (
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
        "groups/<slug:group>/sources/",
        view=SourceListView.as_view(),
        name="source_list",
    ),
    path(
        "groups/<slug:group>/sources/add/",
        view=SourceCreateView.as_view(),
        name="source_create",
    ),
    path(
        "sources/<slug:source>/",
        view=SourceDetailView.as_view(),
        name="source_detail",
    ),
    path(
        "sources/<slug:source>/edit/",
        view=SourceUpdateView.as_view(),
        name="source_update",
    ),
    path(
        "sources/<slug:source>/delete/",
        view=SourceDeleteView.as_view(),
        name="source_delete",
    ),
    path(
        "sources/<slug:source>/quotes/",
        view=QuoteListView.as_view(),
        name="quote_list",
    ),
    path(
        "sources/<slug:source>/quotes/add/",
        view=QuoteCreateView.as_view(),
        name="quote_create",
    ),
    path("quotes/<int:quote>/", view=QuoteDetailView.as_view(), name="quote_detail"),
    path("quotes/<int:quote>/edit/", view=QuoteUpdateView.as_view(), name="quote_update"),
    path(
        "quotes/<int:quote>/delete/",
        view=QuoteDeleteView.as_view(),
        name="quote_delete",
    ),
]
