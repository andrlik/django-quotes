import pytest
from django.contrib.auth import get_user_model

from django_quotes.models import (
    GroupMarkovModel,
    GroupStats,
    Quote,
    QuoteStats,
    Source,
    SourceGroup,
    SourceMarkovModel,
    SourceStats,
)
from django_quotes.signals import markov_sentence_generated, quote_random_retrieved

User = get_user_model()

pytestmark = pytest.mark.django_db(transaction=True)


def test_sourcegroup_description_render(user: User) -> None:
    """
    Test that a description on source group triggers markdown generation.
    :param user: Logged in user.
    :return:
    """
    group = SourceGroup.objects.create(name="Monkey", owner=user)
    assert group.description is None and group.description == group.description_rendered
    group.description = "A **dark** time for all."
    group.save()
    assert group.description_rendered == "<p>A <strong>dark</strong> time for all.</p>"
    group.description = None
    group.save()
    assert group.description_rendered is None


def test_source_description_render(user: User) -> None:
    """
    Test that a description on a source triggers markdown version.
    :param user:
    :return:
    """
    group = SourceGroup.objects.create(name="Monkey", owner=user)
    source = Source.objects.create(name="Curious George", group=group, owner=user)
    assert (
        source.description is None and source.description_rendered == source.description
    )
    source.description = "A **dark** time for all."
    source.save()
    assert source.description_rendered == "<p>A <strong>dark</strong> time for all.</p>"
    source.description = None
    source.save()
    assert source.description_rendered is None


def test_quote_rendering(user: User) -> None:
    """
    Test that quotes get properly formatted as markdown.
    :param user: The logged in user
    :return:
    """
    group = SourceGroup.objects.create(name="Monkey", owner=user)
    source = Source.objects.create(name="Curious George", group=group, owner=user)
    # Quotes can never be none so we just have to verify that the rendered version is getting created.
    quote = Quote.objects.create(
        source=source, owner=user, quote="A **dark** time for all."
    )
    assert quote.quote_rendered == "<p>A <strong>dark</strong> time for all.</p>"


def test_source_creation_allow_creates_markov_model_object(user: User) -> None:
    """
    Test that creating a source also creates it's related markov model with initially empty data.
    """
    group = SourceGroup.objects.create(name="Monkey", owner=user)
    source = Source.objects.create(name="Curious George", group=group, owner=user)
    assert SourceMarkovModel.objects.get(source=source)


def test_group_creation_creates_markov_model(user: User) -> None:
    """
    Ensure that creating a source group also creates a GroupMarkov instance.
    """
    group = SourceGroup.objects.create(name="Monkey", owner=user)
    assert GroupMarkovModel.objects.get(group=group)


def test_source_group_creation_generates_stats_object(user: User) -> None:
    """
    Test that the creation of either a source group or source creates its related
    stats object.
    """
    group = SourceGroup.objects.create(name="Monkey", owner=user)
    assert GroupStats.objects.get(group=group)
    source = Source.objects.create(name="Curious George", group=group, owner=user)
    assert SourceStats.objects.get(source=source)
    quote = Quote.objects.create(quote="I'm all a twitter.", source=source, owner=user)
    assert QuoteStats.objects.get(quote=quote)


@pytest.fixture
def statable_source(user):
    """
    Create a source suitable for stat collection.
    :param user: A user who owns the record.
    :return: Source object
    """
    group = SourceGroup.objects.create(name="Monkey", owner=user)
    source = Source.objects.create(name="Curious George", group=group, owner=user)
    Quote.objects.create(quote="Silly little monkey.", source=source, owner=user)
    Quote.objects.create(
        quote="I need bananas or else I get the shakes.",
        source=source,
        owner=user,
    )
    Quote.objects.create(
        quote="I'm going to take your thumbs first.", source=source, owner=user
    )
    yield source
    group.delete()


def test_quote_retrieve_stat_signal(statable_source):
    """
    Test that stat are updated correctly when the signal is fired.
    :param statable_source: An instance of Source with stat objects attached
    """
    char_quotes_requested = statable_source.stats.quotes_requested
    group_quotes_requested = statable_source.group.stats.quotes_requested
    quote = statable_source.quote_set.all()[0]
    quote_usage = quote.stats.times_used
    quote_random_retrieved.send(Source, instance=statable_source, quote_retrieved=quote)
    statable_source.refresh_from_db()
    quote.refresh_from_db()
    assert char_quotes_requested < statable_source.stats.quotes_requested
    assert group_quotes_requested < statable_source.group.stats.quotes_requested
    assert quote_usage < quote.stats.times_used


def test_markov_stat_signal(statable_source):
    char_quotes_generated = statable_source.stats.quotes_generated
    group_quotes_generated = statable_source.group.stats.quotes_generated
    markov_sentence_generated.send(Source, instance=statable_source)
    statable_source.refresh_from_db()
    assert char_quotes_generated < statable_source.stats.quotes_generated
    assert group_quotes_generated < statable_source.group.stats.quotes_generated


# def test_quote_create_edit_markov_generation_signal(property_group):
#     source = property_group.source_set.filter(allow_markov=True)[0]
#     cmodel_lastmodify = SourceMarkovModel.objects.get(source=source).modified
#     gmodel_lastmodify = GroupMarkovModel.objects.get(group=property_group).modified
#     q = Quote.objects.create(
#         quote="I am a new quote, full of exciting things to think about.",
#         source=source,
#         owner=property_group.owner,
#         citation="Some episode",
#     )
#     assert (
#         cmodel_lastmodify
#         < SourceMarkovModel.objects.get(source=source).modified
#     )
#     assert (
#         gmodel_lastmodify < GroupMarkovModel.objects.get(group=property_group).modified
#     )
#     cmodel_lastmodify = SourceMarkovModel.objects.get(source=source).modified
#     gmodel_lastmodify = GroupMarkovModel.objects.get(group=property_group).modified
#     q.quote = "Let's change things up a bit with a new quote."
#     q.save()
#     assert (
#         cmodel_lastmodify
#         < SourceMarkovModel.objects.get(source=source).modified
#     )
#     assert (
#         gmodel_lastmodify < GroupMarkovModel.objects.get(group=property_group).modified
#     )
#
#
def test_source_set_to_allow_markov_regenerates_models(property_group):
    source = property_group.source_set.filter(allow_markov=False)[0]
    cmodel_lastmodify = SourceMarkovModel.objects.get(source=source).modified
    gmodel_lastmodify = GroupMarkovModel.objects.get(group=property_group).modified
    source.allow_markov = True
    source.save()
    assert cmodel_lastmodify < SourceMarkovModel.objects.get(source=source).modified
    assert (
        gmodel_lastmodify < GroupMarkovModel.objects.get(group=property_group).modified
    )
