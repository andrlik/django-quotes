#
# views.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

from typing import TYPE_CHECKING

from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.http import HttpResponseRedirect
from django.shortcuts import get_object_or_404
from django.urls import reverse_lazy
from django.utils.translation import gettext_lazy as _
from django.views.generic import DetailView as GenericDetail
from django.views.generic import ListView as GenericList
from django.views.generic.edit import CreateView as GenericCreate
from django.views.generic.edit import DeleteView as GenericDelete
from django.views.generic.edit import UpdateView as GenericUpdate
from rules.contrib.views import PermissionRequiredMixin

from django_quotes.models import Quote, Source, SourceGroup

# Create your views here.


# SOURCE GROUPS


class SourceGroupListView(LoginRequiredMixin, GenericList):
    """
    Displays Source Groups owned by the user.
    TODO: For now, only user owned groups, we won't bother with public options.

    Available at /groups/
    """

    model = SourceGroup
    context_object_name = "groups"
    template_name = "quotes/group_list.html"
    paginate_by = 15
    allow_empty = True

    def get_queryset(self):
        return SourceGroup.objects.filter(owner=self.request.user)  # type: ignore


class SourceGroupDetailView(LoginRequiredMixin, PermissionRequiredMixin, GenericDetail):
    """
    Displays details for a source group.

    Available at /groups/[group_slug]/
    """

    model = SourceGroup
    context_object_name = "group"
    template_name = "quotes/group_detail.html"
    permission_required = "django_quotes.read_sourcegroup"
    slug_url_kwarg = "group"
    prefetch_related = ["source_set"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["source_sample"] = Source.objects.filter(group=context["group"])[:5]
        return context


class SourceGroupUpdateView(LoginRequiredMixin, PermissionRequiredMixin, GenericUpdate):
    """
    Update an existing source group

    Available at /groups/[group_slug]/edit/
    """

    if TYPE_CHECKING:
        object: SourceGroup

    model = SourceGroup
    context_object_name = "group"
    template_name = "quotes/group_update.html"
    permission_required = "django_quotes.edit_sourcegroup"
    fields = ["name", "description", "public"]
    slug_url_kwarg = "group"

    def get_success_url(self):
        messages.success(self.request, _(f"Successfully updated group {self.object.name}!"))
        return reverse_lazy("quotes:group_detail", kwargs={"group": self.object.slug})


class SourceGroupDeleteView(LoginRequiredMixin, PermissionRequiredMixin, GenericDelete):  # type: ignore
    """
    Delete and existing source group.

    Available at /groups/[group_slug]/delete/
    """

    model = SourceGroup
    context_object_name = "group"
    template_name = "quotes/group_delete.html"
    permission_required = "django_quotes.delete_sourcegroup"
    slug_url_kwarg = "group"
    success_url = reverse_lazy("quotes:group_list")


class SourceGroupCreateView(LoginRequiredMixin, GenericCreate):
    """
    Create a new source group.

    Available at /groups/create/
    """

    model = SourceGroup
    template_name = "quotes/group_create.html"
    fields = ["name", "description", "public"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        obj = form.save()
        messages.success(self.request, _(f"Successfully created group {obj.name}"))
        return HttpResponseRedirect(redirect_to=reverse_lazy("quotes:group_detail", kwargs={"group": obj.slug}))


# SOURCES


class SourceCreateView(LoginRequiredMixin, PermissionRequiredMixin, GenericCreate):
    """
    Create a new source and add them to a source group.

    Available at /groups/[group_slug]/sources/add/
    """

    model = Source
    template_name = "quotes/source_create.html"
    fields = ["name", "description", "allow_markov", "public"]
    permission_required = "django_quotes.edit_sourcegroup"
    group = None

    def dispatch(self, request, *args, **kwargs):
        group_slug = kwargs.pop("group")
        self.group = get_object_or_404(SourceGroup, slug=group_slug)
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self):
        return self.group

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self.group
        return context

    def form_valid(self, form):
        form.instance.owner = self.request.user
        form.instance.group = self.group
        obj = form.save()
        messages.success(self.request, _(f"Successfully created source {obj.name}!"))
        return HttpResponseRedirect(redirect_to=reverse_lazy("quotes:source_detail", kwargs={"source": obj.slug}))


class SourceDetailView(LoginRequiredMixin, PermissionRequiredMixin, GenericDetail):
    """
    Shows information about the specified source.

    Available at /groups/[group_slug]/sources/[source_slug]/
    """

    model = Source
    slug_url_kwarg = "source"
    slug_field = "slug"
    template_name = "quotes/source_detail.html"
    context_object_name = "source"
    permission_required = "django_quotes.read_source"
    prefetch_related = "quote_set"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["samp_quotes"] = context["source"].quote_set.all()[:5]
        return context


class SourceUpdateView(LoginRequiredMixin, PermissionRequiredMixin, GenericUpdate):
    """
    Allows editing and updating of a Source.

    Available at /groups/[group_slug]/sources/[source_slug]/edit/
    """

    model = Source
    slug_url_kwarg = "source"
    slug_field = "slug"
    template_name = "quotes/source_update.html"
    permission_required = "django_quotes.edit_source"
    fields = ["name", "description", "public", "allow_markov"]

    def get_success_url(self):
        messages.success(self.request, "Successfully updated source!")
        return reverse_lazy("quotes:source_detail", kwargs={"source": self.kwargs["source"]})


class SourceDeleteView(LoginRequiredMixin, PermissionRequiredMixin, GenericDelete):  # type: ignore
    """
    Used to delete a given Source

    Available at /groups/[group_slug]/sources/[source_slug]/delete/
    """

    model = Source
    slug_field = "slug"
    slug_url_kwarg = "source"
    template_name = "quotes/source_delete.html"
    permission_required = "django_quotes.delete_source"
    context_object_name = "source"

    def dispatch(self, request, *args, **kwargs):
        source_slug = kwargs.get("source")
        source = get_object_or_404(Source, slug=source_slug)  # type: ignore
        self.group = source.group
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("quotes:source_list", kwargs={"group": self.group.slug})


class SourceListView(LoginRequiredMixin, PermissionRequiredMixin, GenericList):
    """
    Display a list of sources for a given group.

    Available at /groups/[group_slug]/sources/
    """

    model = Source
    template_name = "quotes/source_list.html"
    permission_required = "django_quotes.read_sourcegroup"
    context_object_name = "sources"
    paginate_by = 15
    allow_empty = True
    group = None

    def dispatch(self, request, *args, **kwargs):
        group_slug = kwargs.pop("group")
        self.group = get_object_or_404(SourceGroup, slug=group_slug)
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self):
        return self.group

    def get_queryset(self):
        return (
            Source.objects.filter(group=self.group)
            .select_related("group", "owner")
            .prefetch_related("quote_set")
            .order_by("name")
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["group"] = self.group
        return context


# QUOTES


class QuoteListView(LoginRequiredMixin, PermissionRequiredMixin, GenericList):
    """
    View for viewing quotes from a specific source.

    Available at /groups/[group_slug]/sources/[source_slug]/quotes/
    """

    model = Quote
    context_object_name = "quotes"
    template_name = "quotes/quote_list.html"
    permission_required = "django_quotes.read_source"
    paginate_by = 15
    allow_empty = True
    source = None

    def dispatch(self, request, *args, **kwargs):
        source_slug = kwargs.pop("source")
        self.source = get_object_or_404(Source, slug=source_slug)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return Quote.objects.filter(source=self.source).select_related("source", "source__group").order_by("-created")

    def get_permission_object(self):
        return self.source

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["source"] = self.source
        return context


class QuoteCreateView(LoginRequiredMixin, PermissionRequiredMixin, GenericCreate):
    """
    View for adding a quote to a source.

    Available at /groups/[group_slug]/sources/[source_slug]/quotes/add/
    """

    model = Quote
    template_name = "quotes/quote_create.html"
    permission_required = "django_quotes.edit_source"
    fields = ["quote", "citation", "citation_url", "pub_date"]

    def dispatch(self, request, *args, **kwargs):
        source_slug = kwargs.pop("source")
        self.source = get_object_or_404(Source, slug=source_slug)  # type: ignore
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self):
        return self.source

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["source"] = self.source
        return context

    def form_valid(self, form):
        # Check to see if this exact quote is already here. This is imperfect, but better than nothing.
        if Quote.objects.filter(source=self.source, quote=form.instance.quote).exists():
            messages.error(
                self.request,
                _(f"This quote for source {self.source.name} already exists."),
            )
            return self.form_invalid(form)
        form.instance.source = self.source
        form.instance.owner = self.request.user
        form.save()
        messages.success(self.request, _("Successfully added quote!"))
        return HttpResponseRedirect(redirect_to=reverse_lazy("quotes:quote_list", kwargs={"source": self.source.slug}))


class QuoteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, GenericUpdate):
    """
    View for updating a quote.

    Available at /groups/[group_slug]/sources/[source_slug]/quotes/[quote_id]/edit/
    """

    model = Quote
    permission_required = "django_quotes.edit_quote"
    template_name = "quotes/quote_update.html"
    fields = ["quote", "citation", "citation_url", "pub_date"]
    pk_url_kwarg = "quote"

    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, _("Successfully updated quote!"))
        return HttpResponseRedirect(redirect_to=reverse_lazy("quotes:quote_detail", kwargs={"quote": obj.id}))


class QuoteDetailView(LoginRequiredMixin, PermissionRequiredMixin, GenericDetail):
    """
    A quote detail view for use in things like previewing render or viewing statistics.

    Available at /groups/[group_slug]/sources/[source_slug]/quotes/[quote_id]/
    """

    model = Quote
    pk_url_kwarg = "quote"
    context_object_name = "quote"
    permission_required = "django_quotes.read_quote"
    template_name = "quotes/quote_detail.html"
    select_related = ["source", "source__group", "owner"]


class QuoteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, GenericDelete):  # type: ignore
    """
    View to delete a quote.

    Available at /groups/[group_slug]/sources/[source_slug]/quotes/[quote_id]/delete/
    """

    model = Quote
    pk_url_kwarg = "quote"
    context_object_name = "quote"
    permission_required = "django_quotes.delete_quote"
    template_name = "quotes/quote_delete.html"

    def get_object(self, *args, **kwargs):
        object = super().get_object(*args, **kwargs)
        self.source = object.source  # type: ignore
        return object

    def get_success_url(self):
        return reverse_lazy("quotes:quote_list", kwargs={"source": self.source.slug})
