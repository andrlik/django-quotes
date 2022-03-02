from django.db import transaction
from django.db.models import F
from django.db.models.signals import post_save, pre_save
from django.dispatch import receiver
from markdown import markdown

from .models import (
    GroupMarkovModel,
    GroupStats,
    Quote,
    QuoteStats,
    Source,
    SourceGroup,
    SourceMarkovModel,
    SourceStats,
)
from .signals import markov_sentence_generated, quote_random_retrieved


@receiver(pre_save, sender=SourceGroup)
@receiver(pre_save, sender=Source)
def render_description(sender, instance, *args, **kwargs):
    """
    Automatically renders the description from markdown.
    """
    if instance.description:
        instance.description_rendered = markdown(instance.description)
    else:
        instance.description_rendered = None


@receiver(pre_save, sender=Quote)
def render_quote(sender, instance, *args, **kwargs):
    """
    Render the quote via markdown and save the results.
    """
    instance.quote_rendered = markdown(instance.quote)


@receiver(post_save, sender=SourceGroup)
def initialize_group_markov_object(sender, instance, created, *args, **kwargs):
    """
    Creates the one-to-one object for the group markov model.
    """
    if created:
        GroupMarkovModel.objects.create(group=instance)


@receiver(post_save, sender=Source)
def initialize_markov_object(sender, instance, created, *args, **kwargs):
    """
    Creates the one-to-one object to accompany the source object.
    """
    if created:
        SourceMarkovModel.objects.create(source=instance)


@receiver(post_save, sender=SourceGroup)
@receiver(post_save, sender=Source)
@receiver(post_save, sender=Quote)
def initialize_grouping_stat_object(sender, instance, created, *args, **kwargs):
    """
    Creates the initial stat objects in the database.
    """
    if created:
        if sender == SourceGroup:
            GroupStats.objects.create(group=instance)
        elif sender == Source:
            SourceStats.objects.create(source=instance)
        elif sender == Quote:
            QuoteStats.objects.create(quote=instance)


@receiver(quote_random_retrieved, sender=Source)
def update_stats_for_quote_character(
    sender, instance, quote_retrieved, *args, **kwargs
):
    """
    Update the stats for the source, source group, and quote for a random retrieval.
    :param sender: Usually a source or sourcegroup class.
    :param instance: The source this was generated for.
    :param quote_retrieved: The quote that was returned.
    :return: None
    """
    group_stats = instance.group.stats
    character_stats = instance.stats
    quote_stats = quote_retrieved.stats
    with transaction.atomic():
        group_stats.quotes_requested = F("quotes_requested") + 1
        group_stats.save()
        character_stats.quotes_requested = F("quotes_requested") + 1
        character_stats.save()
        quote_stats.times_used = F("times_used") + 1
        quote_stats.save()


@receiver(markov_sentence_generated, sender=Source)
def update_stats_for_markov(sender, instance, *args, **kwargs):
    """
    For a given source, update the stats on the Source and SourceGroup for markov requests.
    :param sender: The requesting class, usually Source.
    :param instance: The specific source requested.
    :return: None
    """
    group_stats = instance.group.stats
    source_stats = instance.stats
    with transaction.atomic():
        group_stats.quotes_generated = F("quotes_generated") + 1
        group_stats.save()
        source_stats.quotes_generated = F("quotes_generated") + 1
        source_stats.save()


# @receiver(post_save, sender=Quote)
# def update_markov_model_on_quote_change(sender, instance, created, *args, **kwargs):
#     if instance.character.allow_markov:
#         cmm = CharacterMarkovModel.objects.get(character=instance.character)
#         cmm.generate_model_from_corpus()


@receiver(pre_save, sender=Source)
def update_markov_model_for_character_enabling_markov(
    sender, instance, *args, **kwargs
):
    if instance.id and instance.allow_markov:
        old_version = Source.objects.get(id=instance.id)
        if not old_version.allow_markov:
            cmm = SourceMarkovModel.objects.get(source=instance)
            gmm = GroupMarkovModel.objects.get(group=instance.group)
            cmm.generate_model_from_corpus()
            gmm.generate_model_from_corpus()
