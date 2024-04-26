# models.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from __future__ import annotations

import random
from typing import TYPE_CHECKING, Any

import markovify
import rules
from asgiref.sync import async_to_sync

if TYPE_CHECKING:
    from django.db.models.manager import RelatedManager
from django.conf import settings
from django.db import models
from django.db.models import Count
from django.utils import timezone
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from loguru import logger
from markdown import markdown
from rules.contrib.models import RulesModelBase, RulesModelMixin

from django_markov.models import MarkovTextModel
from django_markov.text_models import POSifiedText
from django_quotes.rules import (  # is_character_owner,; is_group_owner_and_authenticated,
    is_owner,
    is_owner_or_public,
)
from django_quotes.signals import quote_random_retrieved
from django_quotes.utils import generate_unique_slug_for_model

MAX_QUOTES_FOR_RANDOM_SET = 50
MAX_QUOTES_FOR_RANDOM_GROUP_SET = 50

if hasattr(settings, "MAX_QUOTES_FOR_RANDOM_SET"):  # pragma: nocover
    MAX_QUOTES_FOR_RANDOM_SET = settings.MAX_QUOTES_FOR_RANDOM_SET

if hasattr(settings, "MAX_QUOTES_FOR_RANDOM_GROUP_SET"):  # pragma: nocover
    MAX_QUOTES_FOR_RANDOM_GROUP_SET = settings.MAX_QUOTES_FOR_RANDOM_GROUP_SET


class QuoteCorpusError(Exception):
    """
    An exception raised when a quote corpus fails to generate.
    """

    pass


class AbstractOwnerModel(models.Model):
    """
    Abstract model for representing an entity owned by a user with toggles for either allowing submissions for it
    and public access. Defaults to completely private by default.

    Attributes:
        public (bool): is this object public to any authenticated user? Default: False
        allow_submissions (bool): allow other users to submit child objects? Default: False. Not implemented yet.
        owner (User): The user that created this object.
    """

    public = models.BooleanField(
        default=False,
        help_text=_("Is this a public source available for any user to view?"),
    )
    allow_submissions = models.BooleanField(default=False, help_text=_("Allow submissions from other users?"))
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        abstract = True


class TimeStampedModel(models.Model):
    """Automatically adds a created and modified field."""

    created = models.DateTimeField(auto_now_add=True, help_text=_("Created timestamp"))
    modified = models.DateTimeField(auto_now=True, help_text=_("Last modified time"))

    class Meta:
        abstract = True


# Create your models here.
class SourceGroup(AbstractOwnerModel, RulesModelMixin, TimeStampedModel, metaclass=RulesModelBase):
    """
    An abstract group or source for a given set of quotes. Multiple sources, or Source objects, can belong to
    the same group. For example, a novel or series if you plan to quote the characters within individually.

    Attributes:
        id (int): Database primary key for the object.
        name (str): Human readable string to name the group. This will be converted to a slug prefix.
        description (str): A description of the group for convenience. Markdown can be used here for styling.
        owner (User): The user that created the group and therefore owns it.
        public (bool): Is this group public or private. Defaults to False.
        allow_submissions (bool): Allow other users to submit characters to this. Not yet implemented.
        slug (str): A unique slug to represent this group. Generated automatically from name.
        text_model (MarkovTextModel | None): The current text model.
        created (datetime): When this object was first created. Auto-generated.
        modified (datetime): Last time this object was modified. Auto-generated.

    """

    if TYPE_CHECKING:
        source_set: RelatedManager[Source]
        stats: GroupStats

    name = models.CharField(
        _("Source Name"),
        max_length=50,
        help_text=_("A source for individuals making the quotes. Use as an abstract grouping."),
        db_index=True,
    )
    description = models.TextField(
        help_text=_("Description for the source. You can style using Markdown."),
        null=True,
        blank=True,
    )
    slug = models.SlugField(
        unique=True,
        max_length=70,
        editable=False,
        blank=True,
        help_text=_("Unique slug for this group."),
    )
    text_model = models.OneToOneField(
        MarkovTextModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("The markov model for this group."),
    )

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "read": is_owner_or_public,
            "edit": is_owner,
            "delete": is_owner,
        }
        ordering = ["name"]

    def __str__(self):  # no cov
        return self.name

    def save(self, *args, **kwargs):
        """Save and create slug if missing."""
        if not self.slug:  # Once this slug is set, it does not change except through devil pacts
            logger.debug("Group is being saved and a slug was provided.")
            self.slug = generate_unique_slug_for_model(model_class=type(self), text=self.name)
        super().save(*args, **kwargs)

    def refresh_from_db(self, *args, **kwargs):
        """
        Also reset cached properties.
        """
        super().refresh_from_db(*args, **kwargs)
        cached_properties = ["total_sources", "markov_sources", "total_quotes"]
        for prop in cached_properties:
            try:
                del self.__dict__[prop]
            except KeyError:  # pragma: nocover
                pass

    @property
    def description_rendered(self) -> str:
        """Return the markdown rendered version of the description."""
        if self.description is None or self.description == "":
            return ""
        return markdown(self.description)

    @cached_property
    def total_sources(self) -> int:
        """Total number of sources for the group."""
        return Source.objects.filter(group=self).count()

    @cached_property
    def markov_sources(self) -> int:
        """Total number of Markov sources for the group."""
        return Source.objects.filter(group=self, allow_markov=True).count()

    @cached_property
    def total_quotes(self) -> int:
        """Total quotes for the group."""
        return Quote.objects.filter(source__in=Source.objects.filter(group=self)).count()

    @cached_property
    def markov_ready(self) -> bool:
        """Checks to see if there are Markov enabled sources and sufficient quotes."""
        if (
            self.markov_sources > 0
            and self.text_model is not None
            and Quote.objects.filter(source__in=self.source_set.filter(allow_markov=True)).count() > 10  # noqa:PLR2004
        ):
            return True
        return False

    async def aupdate_markov_model(self, additional_model: MarkovTextModel | None = None) -> None:
        """Updates the related MarkovTextModel.

        Args:
            additional_model (MarkovTextModel | None): An additional model to include in the combination. Useful for
                pre_save signals for a source that is newly enabling allow_markov.
        """
        if self.text_model is not None:
            sources = (
                self.source_set.select_related("text_model")
                .prefetch_related("quote_set")
                .filter(allow_markov=True, text_model__data__isnull=False)
            )
            markov_sources = sources.annotate(num_quotes=Count("quote")).filter(num_quotes__gt=10)
            models_to_combine = []
            if additional_model is not None:
                models_to_combine.append(additional_model)
            if await markov_sources.aexists():
                models_to_combine += [source.text_model async for source in markov_sources]
            if len(models_to_combine) > 0:
                if len(models_to_combine) > 1:
                    new_text_model, num_combined = await self.text_model.acombine_models(
                        models_to_combine, mode="strict", return_type="text_model"
                    )
                    if not isinstance(new_text_model, POSifiedText):  # no cov
                        msg = "Only an instance of POSifiedText is allowed when updating the SourceGroup text_model!"
                        raise TypeError(msg)
                    self.text_model.data = new_text_model.to_json()  # type: ignore
                else:
                    # There is a only a single source
                    source = models_to_combine[0]
                    self.text_model.data = source.data
                await self.text_model.asave()

    def update_markov_model(self, additional_model: MarkovTextModel | None = None) -> None:
        """Updates the related MarkovTextModel."""
        async_to_sync(self.aupdate_markov_model)(additional_model=additional_model)

    def generate_markov_sentence(self, max_characters: int = 280, tries: int = 20) -> str | None:
        """
        Generate a markov sentence based on quotes from markov enabled characters for the group.

        Args:
            max_characters (int): Maximum characters allowed in the resulting sentence.
            tries (int): Maximum number of tries django_markov should use to create the sentence.

        Returns:
            (str | None): The generated sentence or None if no sentence was possible for the number
                of tries.
        """
        if self.markov_ready and self.text_model is not None:
            logger.debug("Group is ready for markov sentences. Checking model...")
            mmodel = self.text_model
            if not mmodel.is_ready:
                logger.debug("Markov model for group is not generated yet! Generating...")
                self.update_markov_model()
                mmodel.refresh_from_db()
            logger.debug("Generating sentence...")
            sentence: str | None = mmodel.generate_sentence(char_limit=max_characters, tries=tries)
            if sentence is not None:
                logger.debug(f"Returning generated sentence: '{sentence}'")
                return sentence
        logger.debug("Group is not ready for markov requests yet!")
        return None

    def get_random_quote(self, max_quotes_to_process: int | None = MAX_QUOTES_FOR_RANDOM_GROUP_SET) -> Any:
        """
        Get a random quote object from any of the characters defined within the group.
        Prioritizes quotes that have been returned less often.

        Args:
            max_quotes_to_process (int | None): Maximum number of quotes to retrieve before
                selecting a random one.

        Returns:
             (Quote | None) Quote object or None if no quotes are found.
        """
        # TODO: Create Q object to filter for null datetimes or less than now.
        quotes = (
            Quote.objects.filter(source__in=self.source_set.all())
            .filter(models.Q(pub_date__isnull=True) | models.Q(pub_date__lte=timezone.now()))
            .select_related("stats")
            .order_by("stats__times_used")[:max_quotes_to_process]
        )
        if quotes.exists():
            quote = random.choice(list(quotes))  # noqa: S311
            quote_random_retrieved.send(type(quote.source), instance=quote.source, quote_retrieved=quote)
            return quote
        return None


class Source(AbstractOwnerModel, RulesModelMixin, TimeStampedModel, metaclass=RulesModelBase):
    """
    An individual source to attribute the quote to in the system, such as a character from a podcast/book, or a specific
    author. A user must be the owner of the related SourceGroup to add or delete a source.

    Attributes:
        id (int): Database primary key for the object.
        name (str): Unique name of a character within a ``CharacterGroup`` for this entity.
        group (SourceGroup): The parent ``SourceGroup``.
        slug (str): Slug made up of a generated version of the character name and the group slug prefix.
        description (str): Description for the character. Markdown can be used for styling.
        allow_markov (bool): Allow markov quotes to be requested from this character? Default False.
        owner (User): The user that created and owns this character.
        public (bool): Is the character public to other users? Defaults to False.
        allow_submissions (bool): Allow other users to submit quotes for this character? Defaults to False.
        text_model (MarkovTextModel | None): The current text_model.
        created (datetime): When this object was first created. Auto-generated.
        modified (datetime): Last time this object was modified. Auto-generated.

    """

    if TYPE_CHECKING:
        quote_set: RelatedManager[Quote]
        stats: SourceStats

    name = models.CharField(max_length=100, help_text=_("Name of the character"))
    slug = models.SlugField(
        max_length=250,
        help_text=_("Global slug of the character, will be auto generated from name and group if not overridden."),
        blank=True,
        editable=False,
        unique=True,
        db_index=True,
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text=_("Description of this character. You can style this with Markdown."),
    )
    allow_markov = models.BooleanField(default=False, help_text=_("Allow to be used in markov chains?"))
    group = models.ForeignKey(
        SourceGroup,
        on_delete=models.CASCADE,
        help_text=_("The group this character belongs to."),
    )
    text_model = models.OneToOneField(
        MarkovTextModel,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        help_text=_("The text model for this character."),
    )

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "read": is_owner_or_public,
            "edit": is_owner,
            "delete": is_owner,
        }

    def __str__(self):  # no cov
        return self.name

    def save(self, *args, **kwargs):
        """Save and create slug, if missing."""
        if not self.slug:
            self.slug = generate_unique_slug_for_model(type(self), text=f"{self.group.slug} {self.name}")
        super().save(*args, **kwargs)

    @property
    def description_rendered(self) -> str:
        """Return the markdown rendered version of the description."""
        if self.description is None or self.description == "":
            return ""
        return markdown(self.description)

    @property
    def markov_ready(self) -> bool:
        """
        Conducts sanity checks to see if requesting a markov chain is feasible. Markov must be enabled for a character
        and there must be a sufficient corpus to generate a sentence from. Currently set at a minimum of 10 quotes.

        Returns:
            (bool): If ready for markov requests.
        """
        if self.allow_markov and Quote.objects.filter(source=self).count() > 10:  # noqa:PLR2004
            return True
        return False

    async def _amarkov_ready(self) -> bool:
        """Async version of markov ready.

        Returns:
            (bool): If ready for markov
        """
        if self.allow_markov and await Quote.objects.filter(source=self).acount() > 10:  # noqa: PLR2004
            return True
        return False

    async def aupdate_markov_model(self) -> None:
        """
        Process all quotes into the associated model.
        """
        if await self._amarkov_ready():
            await self.text_model.aupdate_model_from_corpus(  # type: ignore
                corpus_entries=[quote.quote async for quote in self.quote_set.all()],
                char_limit=0,
                store_compiled=False,
            )

    def update_markov_model(self) -> None:
        """
        Sync wrapper around `aupdate_markov_model`.
        """
        async_to_sync(self.aupdate_markov_model)()

    async def aadd_new_quote_to_model(self, quote_to_add: Quote) -> None:
        """Allows adding a new quote to the source's (and group's) text model without parsing the whole corpus.
        Note that deleting or editing a quote will still require a full re-ingest of the corpus to remove old data.

        Args:
            quote_to_add (Quote): A quote to add to the source text model.
        """
        if self.allow_markov and await self.quote_set.acount() > 10 and self.text_model is not None:  # noqa: PLR2004
            if not self.text_model.data:
                await self.aupdate_markov_model()
                await self.group.aupdate_markov_model()
            else:
                if self.group.text_model is None:  # no cov
                    self.group.text_model = await MarkovTextModel.objects.acreate()
                source_model = POSifiedText.from_json(self.text_model.data)
                group_model = POSifiedText.from_json(self.group.text_model.data)
                quote_model = POSifiedText(quote_to_add.quote)
                try:
                    combined_source_model = markovify.combine([source_model, quote_model])
                    combined_group_model = markovify.combine([group_model, quote_model])
                except ValueError as ve:
                    msg = f"Unable to combine models: {ve}"
                    raise QuoteCorpusError(msg) from ve
                self.text_model.data = combined_source_model.to_json()  # type: ignore
                self.group.text_model.data = combined_group_model.to_json()  # type: ignore
                await self.text_model.asave()
                await self.group.text_model.asave()

    def add_new_quote_to_model(self, quote_to_add: Quote) -> None:
        """Sync wrapper for `aadd_new_quote_to_model`.
        Allows adding a new quote to the source's text model without parsing the whole corpus.
        Note that deleting or editing a quote will still require a full re-ingest of the corpus to remove old data.

        Args:
            quote_to_add (Quote): A quote to add to the source text model.
        """
        async_to_sync(self.aadd_new_quote_to_model)(quote_to_add)

    def get_markov_sentence(self, max_characters: int | None = 280, tries: int = 20) -> str | None:
        """
        If valid, generate a markov sentence. If not, return None.

        Args:
            max_characters (int | None): Maximum number of characters allowed in
                resulting sentence.
            tries (int): Number of times django_markov may try to generate sentence.

        Returns:
            (str | None): The resulting sentence or None if a sentence could not be formed.
        """
        if not max_characters:  # no cov
            max_characters = 280
        logger.debug("Checking to see if character is markov ready...")
        if self.markov_ready and self.text_model is not None:
            logger.debug("It IS ready. Fetching markov model.")
            markov_model = self.text_model
            if not markov_model.is_ready:
                logger.debug("No model defined yet, generating...")
                self.update_markov_model()
            logger.debug("Markov text model loaded. Generating sentence.")
            sentence: str | None = markov_model.generate_sentence(char_limit=max_characters, tries=tries)
            if sentence is not None:
                return sentence
        return None

    def get_random_quote(self, max_quotes_to_process: int | None = MAX_QUOTES_FOR_RANDOM_SET) -> Any | None:
        """
        This actually not all that random. It's going to grab the quotes
        ordered ordered by how infrequently they've been returned, and then grab a random one
        in the set. But for our purposes, it's fine. If there aren't any quotes, it will return None.

        Args:
            max_quotes_to_process (int | None): Maximum number of quotes to retrive before
                selecting at random.

        Returns:
            (Quote | None): The quote object or None if no quotes found.
        """
        quotes_to_pick = (
            Quote.objects.filter(source=self)
            .filter(models.Q(pub_date__isnull=True) | models.Q(pub_date__lte=timezone.now()))
            .select_related("stats")
            .order_by("stats__times_used")[:max_quotes_to_process]
        )
        if quotes_to_pick.exists():
            # Select a random index in the result set.
            quote_to_return = random.choice(list(quotes_to_pick))  # noqa: S311
            quote_random_retrieved.send(type(self), instance=self, quote_retrieved=quote_to_return)
            return quote_to_return
        return None


class Quote(AbstractOwnerModel, RulesModelMixin, TimeStampedModel, metaclass=RulesModelBase):
    """
    A quote from a given source. A user must own the related source to add or delete a quote.

    Attributes:
        id (int): Database primary key for the object.
        quote (str): The quote text to use. You can use Markdown for styling. Must be <= 280 characters for tweets
        citation (str | None): Optional description of quote source, e.g. episode number or book title.
        citation_url (str | None): Optional accompanying URL for the citation.
        pub_date (datetime| None): Date and time when the quote was published.
        source (Source): The source of this quote.
        owner (User): The user that created and owns this quote.
        created (datetime): When this object was first created. Auto-generated.
        modified (datetime): Last time this object was modified. Auto-generated.

    """

    if TYPE_CHECKING:
        id: int

    quote = models.CharField(
        max_length=280,  # Keep the base limit to 280 so that quotes are 'tweetable'
        help_text="Plain text representation of quote. You can use Markdown here.",
    )
    source = models.ForeignKey(
        Source,
        on_delete=models.CASCADE,
        help_text=_("The source of this quote, i.e. name."),
    )
    citation = models.CharField(
        max_length=250,
        blank=True,
        null=True,
        help_text=_("Where is this quote from? Episode #, book?"),
    )
    citation_url = models.URLField(null=True, blank=True, help_text=_("URL for citation, if applicable."))
    pub_date = models.DateTimeField(
        null=True,
        blank=True,
        help_text=_("When is the earliest time this should appear in random results?"),
    )

    class Meta:
        rules_permissions = {
            # "add": is_character_owner,
            "read": is_owner_or_public,
            "edit": is_owner,
            "delete": is_owner,
        }

    def __str__(self):  # no cov
        return f"{self.source.name}: {self.quote}"

    @property
    def quote_rendered(self) -> str:
        """Return the markdown rendered version of the quote."""
        if self.quote is None or self.quote == "":
            return ""
        return markdown(self.quote)


class QuoteStats(TimeStampedModel):
    """
    A simple object used to track how often an individual quote is used.

    Attributes:
        id (int): The database primary key of this object.
        quote (Quote): The quote this stat relates to.
        times_used (int): The number of times this has been used by an service such as random quote.
        created (datetime): When this was created.
        modified (datetime): When this was last modified.
    """

    quote = models.OneToOneField(
        Quote,
        on_delete=models.CASCADE,
        related_name="stats",
        help_text=_("The Quote the stats related to."),
    )
    times_used = models.PositiveIntegerField(default=0, help_text=_("Times used for random quotes, etc."))

    def __str__(self):  # no cov
        return f"Stats for Quote {self.quote.id}"


class GroupStats(TimeStampedModel):
    """
    An object for using to track usage stats for ``CharacterGroup``.

    Attributes:
        group (SourceGroup): The group this is collecting stats for.
        quotes_requested (int): The number of times a quote from this object or its children has been requested.
        quotes_generated (int): The number of times a markov quote has been generated for this or it's children.
    """

    group = models.OneToOneField(SourceGroup, related_name="stats", on_delete=models.CASCADE)
    quotes_requested = models.PositiveIntegerField(
        default=0, help_text=_("Number of time child quotes have been requested.")
    )
    quotes_generated = models.PositiveIntegerField(
        default=0,
        help_text=_("Number of times markov generated quotes have been requested."),
    )

    def __str__(self):  # no cov
        return f"Stats for Group {self.group.name}"


class SourceStats(TimeStampedModel):
    """
    An object for using to track usage stats for ``Character``.

    Attributes:
        source (Source): The source this is collecting stats for.
        quotes_requested (int): The number of times a quote from this object or its children has been requested.
        quotes_generated (int): The number of times a markov quote has been generated for this or it's children.
    """

    source = models.OneToOneField(Source, related_name="stats", on_delete=models.CASCADE)
    quotes_requested = models.PositiveIntegerField(
        default=0, help_text=_("Number of time child quotes have been requested.")
    )
    quotes_generated = models.PositiveIntegerField(
        default=0,
        help_text=_("Number of times markov generated quotes have been requested."),
    )

    def __str__(self):  # no cov
        return f"Stats for Source {self.source.name}"
