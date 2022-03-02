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

from .models import Character, CharacterGroup, Quote

# Create your views here.


# CHARACTER GROUPS


class CharacterGroupListView(LoginRequiredMixin, GenericList):
    """
    Displays Character Groups owned by the user.
    TODO: For now, only user owned groups, we won't bother with public options.
    """

    model = CharacterGroup
    context_object_name = "groups"
    template_name = "quotes/character_group_list.html"
    paginate_by = 15
    allow_empty = True

    def get_queryset(self):
        return CharacterGroup.objects.filter(owner=self.request.user)  # type: ignore


class CharacterGroupDetailView(
    LoginRequiredMixin, PermissionRequiredMixin, GenericDetail
):
    """
    Displays details for a character group.
    """

    model = CharacterGroup
    context_object_name = "group"
    template_name = "quotes/character_group_detail.html"
    permission_required = "django_quotes.read_charactergroup"
    slug_url_kwarg = "group"
    prefetch_related = ["character_set"]

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["char_sample"] = Character.objects.filter(group=context["group"])[:5]
        return context


class CharacterGroupUpdateView(
    LoginRequiredMixin, PermissionRequiredMixin, GenericUpdate
):
    """
    Update an existing character group
    """

    model = CharacterGroup
    context_object_name = "group"
    template_name = "quotes/character_group_update.html"
    permission_required = "django_quotes.edit_charactergroup"
    fields = ["name", "description", "public"]
    slug_url_kwarg = "group"

    def get_success_url(self):
        messages.success(
            self.request, _(f"Successfully updated group {self.object.name}!")
        )
        return reverse_lazy("quotes:group_detail", kwargs={"group": self.object.slug})


class CharacterGroupDeleteView(
    LoginRequiredMixin, PermissionRequiredMixin, GenericDelete
):
    """
    Delete and existing character group.
    """

    model = CharacterGroup
    context_object_name = "group"
    template_name = "quotes/character_group_delete.html"
    permission_required = "django_quotes.delete_charactergroup"
    slug_url_kwarg = "group"
    success_url = reverse_lazy("quotes:group_list")


class CharacterGroupCreateView(LoginRequiredMixin, GenericCreate):
    """
    Create a new character group.
    """

    model = CharacterGroup
    template_name = "quotes/character_group_create.html"
    fields = ["name", "description", "public"]

    def form_valid(self, form):
        form.instance.owner = self.request.user
        obj = form.save()
        messages.success(self.request, _(f"Successfully created group {obj.name}"))
        return HttpResponseRedirect(
            redirect_to=reverse_lazy("quotes:group_detail", kwargs={"group": obj.slug})
        )


# CHARACTERS


class CharacterCreateView(LoginRequiredMixin, PermissionRequiredMixin, GenericCreate):
    """
    Create a new character and add them to a character group.
    """

    model = Character
    template_name = "quotes/character_create.html"
    fields = ["name", "description", "allow_markov", "public"]
    permission_required = "django_quotes.edit_charactergroup"
    group = None

    def dispatch(self, request, *args, **kwargs):
        group_slug = kwargs.pop("group")
        self.group = get_object_or_404(CharacterGroup, slug=group_slug)
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
        messages.success(self.request, _(f"Successfully created character {obj.name}!"))
        return HttpResponseRedirect(
            redirect_to=reverse_lazy(
                "quotes:character_detail", kwargs={"character": obj.slug}
            )
        )


class CharacterDetailView(LoginRequiredMixin, PermissionRequiredMixin, GenericDetail):
    """
    Shows information about the specified character.
    """

    model = Character
    slug_url_kwarg = "character"
    slug_field = "slug"
    template_name = "quotes/character_detail.html"
    context_object_name = "character"
    permission_required = "django_quotes.read_character"
    prefetch_related = "quote_set"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["samp_quotes"] = context["character"].quote_set.all()[:5]
        return context


class CharacterUpdateView(LoginRequiredMixin, PermissionRequiredMixin, GenericUpdate):
    """
    Allows editing and updating of a Character.
    """

    model = Character
    slug_url_kwarg = "character"
    slug_field = "slug"
    template_name = "quotes/character_update.html"
    permission_required = "django_quotes.edit_character"
    fields = ["name", "description", "public", "allow_markov"]

    def get_success_url(self):
        messages.success(self.request, "Successfully updated character!")
        return reverse_lazy(
            "quotes:character_detail", kwargs={"character": self.kwargs["character"]}
        )


class CharacterDeleteView(LoginRequiredMixin, PermissionRequiredMixin, GenericDelete):
    """
    Used to delete a given Character
    """

    model = Character
    slug_field = "slug"
    slug_url_kwarg = "character"
    template_name = "quotes/character_delete.html"
    permission_required = "django_quotes.delete_character"
    context_object_name = "character"
    group = None

    def dispatch(self, request, *args, **kwargs):
        character_slug = kwargs.get("character")
        character = get_object_or_404(Character, slug=character_slug)
        self.group = character.group
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse_lazy("quotes:character_list", kwargs={"group": self.group.slug})


class CharacterListView(LoginRequiredMixin, PermissionRequiredMixin, GenericList):
    """
    Display a list of characters for a given group.
    """

    model = Character
    template_name = "quotes/character_list.html"
    permission_required = "django_quotes.read_charactergroup"
    context_object_name = "characters"
    paginate_by = 15
    allow_empty = True
    group = None

    def dispatch(self, request, *args, **kwargs):
        group_slug = kwargs.pop("group")
        self.group = get_object_or_404(CharacterGroup, slug=group_slug)
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self):
        return self.group

    def get_queryset(self):
        return (
            Character.objects.filter(group=self.group)
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
    View for viewing quotes from a specific character.
    """

    model = Quote
    context_object_name = "quotes"
    template_name = "quotes/quote_list.html"
    permission_required = "django_quotes.read_character"
    paginate_by = 15
    allow_empty = True
    character = None

    def dispatch(self, request, *args, **kwargs):
        character_slug = kwargs.pop("character")
        self.character = get_object_or_404(Character, slug=character_slug)
        return super().dispatch(request, *args, **kwargs)

    def get_queryset(self):
        return (
            Quote.objects.filter(character=self.character)
            .select_related("character", "character__group")
            .order_by("-created")
        )

    def get_permission_object(self):
        return self.character

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["character"] = self.character
        return context


class QuoteCreateView(LoginRequiredMixin, PermissionRequiredMixin, GenericCreate):
    """
    View for adding a quote to a character.
    """

    model = Quote
    template_name = "quotes/quote_create.html"
    permission_required = "django_quotes.edit_character"
    fields = ["quote", "citation", "citation_url"]
    character = None

    def dispatch(self, request, *args, **kwargs):
        character_slug = kwargs.pop("character")
        self.character = get_object_or_404(Character, slug=character_slug)
        return super().dispatch(request, *args, **kwargs)

    def get_permission_object(self):
        return self.character

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context["character"] = self.character
        return context

    def form_valid(self, form):
        # Check to see if this exact quote is already here. This is imperfect, but better than nothing.
        if Quote.objects.filter(
            character=self.character, quote=form.instance.quote
        ).exists():
            messages.error(
                self.request,
                _(f"This quote for character {self.character.name} already exists."),
            )
            return self.form_invalid(form)
        form.instance.character = self.character
        form.instance.owner = self.request.user
        form.save()
        messages.success(self.request, _("Successfully added quote!"))
        return HttpResponseRedirect(
            redirect_to=reverse_lazy(
                "quotes:quote_list", kwargs={"character": self.character.slug}
            )
        )


class QuoteUpdateView(LoginRequiredMixin, PermissionRequiredMixin, GenericUpdate):
    """
    View for updating a quote.
    """

    model = Quote
    permission_required = "django_quotes.edit_quote"
    template_name = "quotes/quote_update.html"
    fields = ["quote", "citation", "citation_url"]
    pk_url_kwarg = "quote"

    def form_valid(self, form):
        obj = form.save()
        messages.success(self.request, _("Successfully updated quote!"))
        return HttpResponseRedirect(
            redirect_to=reverse_lazy("quotes:quote_detail", kwargs={"quote": obj.id})
        )


class QuoteDetailView(LoginRequiredMixin, PermissionRequiredMixin, GenericDetail):
    """
    A quote detail view for use in things like previewing render or viewing statistics.
    """

    model = Quote
    pk_url_kwarg = "quote"
    context_object_name = "quote"
    permission_required = "django_quotes.read_quote"
    template_name = "quotes/quote_detail.html"
    select_related = ["character", "character__group", "owner"]


class QuoteDeleteView(LoginRequiredMixin, PermissionRequiredMixin, GenericDelete):
    """
    View to delete a quote.
    """

    model = Quote
    pk_url_kwarg = "quote"
    context_object_name = "quote"
    permission_required = "django_quotes.delete_quote"
    template_name = "quotes/quote_delete.html"

    def get_object(self, *args, **kwargs):
        object = super().get_object(*args, **kwargs)
        self.character = object.character
        return object

    def get_success_url(self):
        return reverse_lazy(
            "quotes:quote_list", kwargs={"character": self.character.slug}
        )
