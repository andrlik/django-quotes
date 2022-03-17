import random
from typing import Any, Optional

import rules
from django.conf import settings
from django.db import models
from django.utils.functional import cached_property
from django.utils.translation import gettext_lazy as _
from loguru import logger
from model_utils.models import TimeStampedModel
from rules.contrib.models import RulesModelBase, RulesModelMixin
from slugify import slugify

from .markov_utils import MarkovPOSText
from .rules import (  # is_character_owner,; is_group_owner_and_authenticated,
    is_owner,
    is_owner_or_public,
)
from .signals import markov_sentence_generated, quote_random_retrieved

MAX_QUOTES_FOR_RANDOM_SET = 50
MAX_QUOTES_FOR_RANDOM_GROUP_SET = 50

if hasattr(settings, "MAX_QUOTES_FOR_RANDOM_SET"):  # pragma: nocover
    MAX_QUOTES_FOR_RANDOM_SET = settings.MAX_QUOTES_FOR_RANDOM_SET

if hasattr(settings, "MAX_QUOTES_FOR_RANDOM_GROUP_SET"):  # pragma: nocover
    MAX_QUOTES_FOR_RANDOM_GROUP_SET = settings.MAX_QUOTES_FOR_RANDOM_GROUP_SET


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
    allow_submissions = models.BooleanField(
        default=False, help_text=_("Allow submissions from other users?")
    )
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)

    class Meta:
        abstract = True


# Create your models here.
class SourceGroup(
    AbstractOwnerModel, RulesModelMixin, TimeStampedModel, metaclass=RulesModelBase
):
    """
    An abstract group or source for a given set of quotes. Multiple sources, or Source objects, can belong to
    the same group. For example, a novel or series if you plan to quote the characters within individually.

    Attributes:
        id (int): Database primary key for the object.
        name (str): Human readable string to name the group. This will be converted to a slug prefix.
        description (str): A description of the group for convenience. Markdown can be used here for styling.
        description_rendered (str): The HTML representation of the description string. Generated automatically.
        owner (User): The user that created the group and therefore owns it.
        public (bool): Is this group public or private. Defaults to False.
        allow_submissions (bool): Allow other users to submit characters to this. Not yet implemented.
        slug (str): A unique slug to represent this group. Generated automatically from name.
        created (datetime): When this object was first created. Auto-generated.
        modified (datetime): Last time this object was modified. Auto-generated.

    """

    name = models.CharField(
        _("Source Name"),
        max_length=50,
        help_text=_(
            "A source for individuals making the quotes. Use as an abstract grouping."
        ),
        unique=True,
        db_index=True,
    )
    description = models.TextField(
        help_text=_("Description for the source. You can style using Markdown."),
        null=True,
        blank=True,
    )
    description_rendered = models.TextField(
        help_text=_("Automatically generated from description"), null=True, blank=True
    )
    slug = models.SlugField(
        unique=True,
        max_length=70,
        blank=True,
        help_text=_("Unique slug for this group."),
    )

    @cached_property
    def total_sources(self) -> int:
        return Source.objects.filter(group=self).count()

    @cached_property
    def markov_sources(self) -> int:
        return Source.objects.filter(group=self, allow_markov=True).count()

    @cached_property
    def total_quotes(self) -> int:
        return Quote.objects.filter(
            source__in=Source.objects.filter(group=self)
        ).count()

    @cached_property
    def markov_ready(self) -> bool:
        if (
            self.markov_sources > 0
            and Quote.objects.filter(
                source__in=self.source_set.filter(allow_markov=True)
            ).count()
            > 10
        ):
            return True
        return False

    def generate_markov_sentence(
        self, max_characters: Optional[int] = 280
    ) -> Optional[str]:
        """
        Generate a markov sentence based on quotes from markov enabled characters for the group.

        :return: str or None
        """
        if self.markov_ready:
            logger.debug("Group is ready for markov sentences. Checking model...")
            mmodel = GroupMarkovModel.objects.get(group=self)
            if mmodel.data is None:
                logger.debug(
                    "Markov model for group is not generated yet! Generating..."
                )
                mmodel.generate_model_from_corpus()
            logger.debug("Loading text model...")
            text_model = MarkovPOSText.from_json(mmodel.data)
            logger.debug("Generating sentence...")
            sentence = text_model.make_short_sentence(max_chars=max_characters)
            if sentence is not None:
                logger.debug(f"Returning generated sentence: '{sentence}'")
                return sentence
        logger.debug("Group is not ready for markov requests yet!")
        return None

    def get_random_quote(
        self, max_quotes_to_process: Optional[int] = MAX_QUOTES_FOR_RANDOM_GROUP_SET
    ) -> Any:
        """
        Get a random quote object from any of the characters defined within the group.
        Prioritizes quotes that have been returned less often.

        :return: ``Quote`` object or None if no quotes are defined.
        """
        quotes = (
            Quote.objects.filter(source__in=self.source_set.all())
            .select_related("stats")
            .order_by("stats__times_used")[:max_quotes_to_process]
        )
        if quotes.exists():
            quote = random.choice(list(quotes))
            quote_random_retrieved.send(
                type(quote.source), instance=quote.source, quote_retrieved=quote
            )
            return quote
        return None

    def refresh_from_db(self, *args, **kwargs):
        super().refresh_from_db(*args, **kwargs)
        cached_properties = ["total_sources", "markov_sources", "total_quotes"]
        for prop in cached_properties:
            try:
                del self.__dict__[prop]
            except KeyError:  # pragma: nocover
                pass

    def save(self, *args, **kwargs):
        if (
            not self.slug
        ):  # Once this slug is set, it does not change except through devil pacts
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):  # pragma: nocover
        return self.name

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "read": is_owner_or_public,
            "edit": is_owner,
            "delete": is_owner,
        }
        ordering = ["name"]


class Source(
    AbstractOwnerModel, RulesModelMixin, TimeStampedModel, metaclass=RulesModelBase
):
    """
    An individual source to attribute the quote to in the system, such as a character from a podcast/book, or a specific
    author.

    Attributes:
        id (int): Database primary key for the object.
        name (str): Unique name of a character within a ``CharacterGroup`` for this entity.
        group (SourceGroup): The parent ``SourceGroup``.
        slug (str): Slug made up of a generated version of the character name and the group slug prefix.
        description (str): Description for the character. Markdown can be used for styling.
        description_rendered (str): HTML representation of the description for convenience. Automatically generated.
        allow_markov (bool): Allow markov quotes to be requested from this character? Default False.
        owner (User): The user that created and owns this character.
        public (bool): Is the character public to other users? Defaults to False.
        allow_submissions (bool): Allow other users to submit quotes for this character? Defaults to False.
        created (datetime): When this object was first created. Auto-generated.
        modified (datetime): Last time this object was modified. Auto-generated.

    """

    name = models.CharField(max_length=100, help_text=_("Name of the character"))
    slug = models.SlugField(
        max_length=250,
        help_text=_(
            "Global slug of the character, will be auto generated from name and group if not overridden."
        ),
        blank=True,
        unique=True,
        db_index=True,
    )
    description = models.TextField(
        null=True,
        blank=True,
        help_text=_("Description of this character. You can style this with Markdown."),
    )
    description_rendered = models.TextField(
        null=True, blank=True, help_text=_("Automatically generated from description.")
    )
    allow_markov = models.BooleanField(
        default=False, help_text=_("Allow to be used in markov chains?")
    )
    group = models.ForeignKey(
        SourceGroup,
        on_delete=models.CASCADE,
        help_text=_("The group this character belongs to."),
    )

    @property
    def markov_ready(self) -> bool:
        """
        Conducts sanity checks to see if requesting a markov chain is feasible. Markov must be enabled for a character
        and there must be a sufficient corpus to generate a sentence from. Currently set at a minimum of 10 quotes.

        :return: bool
        """
        if self.allow_markov and Quote.objects.filter(source=self).count() > 10:
            return True
        return False

    def get_markov_sentence(self, max_characters: Optional[int] = 280) -> Optional[str]:
        """
        If valid, generate a markov sentence. If not, return None.

        :param max_characters: Optional maximum limit of characters in the return set. Default: 280
        :return: str or None
        """
        logger.debug("Checking to see if character is markov ready...")
        if self.markov_ready:
            logger.debug("It IS ready. Fetching markov model.")
            markov_model = SourceMarkovModel.objects.get(source=self)
            if not markov_model.data:
                logger.debug("No model defined yet, generating...")
                markov_model.generate_model_from_corpus()
            text_model = MarkovPOSText.from_json(markov_model.data)
            logger.debug("Markov text model loaded. Generating sentence.")
            sentence = text_model.make_short_sentence(max_chars=max_characters)
            if sentence is not None:
                markov_sentence_generated.send(type(self), instance=self)
                return sentence
        return None

    def get_random_quote(
        self, max_quotes_to_process: Optional[int] = MAX_QUOTES_FOR_RANDOM_SET
    ) -> Optional[Any]:
        """
        This actually not all that random. It's going to grab the quotes
        ordered ordered by how infrequently they've been returned, and then grab a random one
        in the set. But for our purposes, it's fine. If there aren't any quotes, it will return None.

        :return: ``Quote`` object or None
        """
        quotes_to_pick = (
            Quote.objects.filter(source=self)
            .select_related("stats")
            .order_by("stats__times_used")[:max_quotes_to_process]
        )
        if quotes_to_pick.exists():
            # Select a random index in the result set.
            quote_to_return = random.choice(list(quotes_to_pick))
            quote_random_retrieved.send(
                type(self), instance=self, quote_retrieved=quote_to_return
            )
            return quote_to_return
        return None

    def __str__(self):  # pragma: nocover
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = f"{self.group.slug}-" + slugify(self.name)
        super().save(*args, **kwargs)

    class Meta:
        rules_permissions = {
            "add": rules.is_authenticated,
            "read": is_owner_or_public,
            "edit": is_owner,
            "delete": is_owner,
        }


class Quote(
    AbstractOwnerModel, RulesModelMixin, TimeStampedModel, metaclass=RulesModelBase
):
    """
    A quote from a given source.

    Attributes:
        id (int): Database primary key for the object.
        quote (str): The quote text to use. You can use Markdown for styling. Must be <= 280 characters for tweets
        quote_rendered (str): HTML rendered version of the quote field. Automatically generated.
        citation (str): Optional description of quote source, e.g. episode number or book title.
        citation_url (str): Optional accompanying URL for the citation.
        character (Source): The source of this quote.
        owner (User): The user that created and owns this quote.
        created (datetime): When this object was first created. Auto-generated.
        modified (datetime): Last time this object was modified. Auto-generated.

    """

    quote = models.CharField(
        max_length=280,  # Keep the base limit to 280 so that quotes are 'tweetable'
        help_text="Plain text representation of quote. You can use Markdown here.",
    )
    quote_rendered = models.TextField(
        null=True,
        blank=True,
        help_text=_("HTML rendered version of quote generated from quote plain text."),
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
    citation_url = models.URLField(
        null=True, blank=True, help_text=_("URL for citation, if applicable.")
    )

    def __str__(self):  # pragma: nocover
        return f"{self.source.name}: {self.quote}"

    class Meta:
        rules_permissions = {
            # "add": is_character_owner,
            "read": is_owner_or_public,
            "edit": is_owner,
            "delete": is_owner,
        }


class SourceMarkovModel(TimeStampedModel):
    """
    The cached markov model for a given source. The database object for this is automatically created
    whenever a new character object is saved.

    Attributes:
        id (int): Database primary key for the object.
        source (Source): The character who the model is sourced from.
        data (json): The JSON representation of the Markov model created by ``markovify``.
        created (datetime): When this object was first created. Auto-generated.
        modified (datetime): Last time this object was modified. Auto-generated.

    """

    source = models.OneToOneField(Source, on_delete=models.CASCADE)
    data = models.JSONField(null=True, blank=True)

    def generate_model_from_corpus(self):
        """
        Collect all quotes attributed to the related character. Then
        create, compile, and save the model.
        """
        logger.debug("Generating text model. Fetching quotes.")
        quotes = Quote.objects.filter(source=self.source)
        # Don't bother generating model if there isn't data.
        if not quotes.exists():  # pragma: nocover
            logger.debug("There are no quotes. Returning None.")
            return
        logger.debug("Quotes retrieved! Forming into corpus.")
        corpus = " ".join(quote.quote for quote in quotes)
        logger.debug("Building text model.")
        text_model = MarkovPOSText(corpus)
        logger.debug("Compiling text model.")
        text_model.compile(inplace=True)
        logger.debug("Saving model as JSON.")
        self.data = text_model.to_json()
        self.save()
        logger.debug("Markov model populated to database.")

    def __str__(self):  # pragma: nocover
        return self.source.name


class GroupMarkovModel(TimeStampedModel):
    """
    The cached markov model for the entire group. It is made up of every quote from every markov enabled
    character within the group.

    Attributes:
        id (int): The database id of this object.
        group (SourceGroup): The OneToOne relationship to ``SourceGroup``
        data (json): The cached markov model.
        created (datetime): When the object was created.
        modified (datetime): When the object was last modified.
    """

    group = models.OneToOneField(
        SourceGroup,
        on_delete=models.CASCADE,
        help_text=_("The character group this model belongs to."),
    )
    data = models.JSONField(
        null=True, blank=True, help_text=_("The cached markov model as JSON.")
    )

    def generate_model_from_corpus(self):
        """
        Collect all quotes from markov enabled characters in this group and then compile the model and save it.
        """
        logger.debug(f"Gathering corpus for character group: {self.group.name}")
        quotes = Quote.objects.filter(
            source__in=Source.objects.filter(group=self.group, allow_markov=True)
        )
        if quotes.exists():
            if quotes.count() >= 10:
                logger.debug("Found sufficient quotes for a model!")
                corpus = " ".join(quote.quote for quote in quotes)
                logger.debug("Forming text model...")
                text_model = MarkovPOSText(corpus)
                logger.debug("Compiling text model...")
                text_model.compile(inplace=True)
                logger.debug("Saving compiled model to JSON...")
                self.data = text_model.to_json()
                self.save()
                logger.debug(
                    f"Finished building and saving group markov model for {self.group.name}!"
                )


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
    times_used = models.PositiveIntegerField(
        default=0, help_text=_("Times used for random quotes, etc.")
    )

    def __str__(self):  # pragma: nocover
        return f"Stats for Quote {self.quote.id}"


class GroupStats(TimeStampedModel):
    """
    An object for using to track usage stats for ``CharacterGroup``.

    Attributes:
        group (SourceGroup): The group this is collecting stats for.
        quotes_requested (int): The number of times a quote from this object or its children has been requested.
        quotes_generated (int): The number of times a markov quote has been generated for this or it's children.
    """

    group = models.OneToOneField(
        SourceGroup, related_name="stats", on_delete=models.CASCADE
    )
    quotes_requested = models.PositiveIntegerField(
        default=0, help_text=_("Number of time child quotes have been requested.")
    )
    quotes_generated = models.PositiveIntegerField(
        default=0,
        help_text=_("Number of times markov generated quotes have been requested."),
    )


class SourceStats(TimeStampedModel):
    """
    An object for using to track usage stats for ``Character``.

    Attributes:
        source (Source): The source this is collecting stats for.
        quotes_requested (int): The number of times a quote from this object or its children has been requested.
        quotes_generated (int): The number of times a markov quote has been generated for this or it's children.
    """

    source = models.OneToOneField(
        Source, related_name="stats", on_delete=models.CASCADE
    )
    quotes_requested = models.PositiveIntegerField(
        default=0, help_text=_("Number of time child quotes have been requested.")
    )
    quotes_generated = models.PositiveIntegerField(
        default=0,
        help_text=_("Number of times markov generated quotes have been requested."),
    )
