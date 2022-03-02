import pytest
from django.contrib.auth import get_user_model

from django_quotes.models import (
    Character,
    CharacterGroup,
    CharacterMarkovModel,
    CharacterStats,
    GroupMarkovModel,
    GroupStats,
    Quote,
    QuoteStats,
)
from django_quotes.signals import markov_sentence_generated, quote_random_retrieved

User = get_user_model()

pytestmark = pytest.mark.django_db(transaction=True)


def test_charactergroup_description_render(user: User) -> None:
    """
    Test that a description on character group triggers markdown generation.
    :param user: Logged in user.
    :return:
    """
    group = CharacterGroup.objects.create(name="Monkey", owner=user)
    assert group.description is None and group.description == group.description_rendered
    group.description = "A **dark** time for all."
    group.save()
    assert group.description_rendered == "<p>A <strong>dark</strong> time for all.</p>"
    group.description = None
    group.save()
    assert group.description_rendered is None


def test_character_description_render(user: User) -> None:
    """
    Test that a description on a character triggers markdown version.
    :param user:
    :return:
    """
    group = CharacterGroup.objects.create(name="Monkey", owner=user)
    character = Character.objects.create(name="Curious George", group=group, owner=user)
    assert (
        character.description is None
        and character.description_rendered == character.description
    )
    character.description = "A **dark** time for all."
    character.save()
    assert (
        character.description_rendered == "<p>A <strong>dark</strong> time for all.</p>"
    )
    character.description = None
    character.save()
    assert character.description_rendered is None


def test_quote_rendering(user: User) -> None:
    """
    Test that quotes get properly formatted as markdown.
    :param user: The logged in user
    :return:
    """
    group = CharacterGroup.objects.create(name="Monkey", owner=user)
    character = Character.objects.create(name="Curious George", group=group, owner=user)
    # Quotes can never be none so we just have to verify that the rendered version is getting created.
    quote = Quote.objects.create(
        character=character, owner=user, quote="A **dark** time for all."
    )
    assert quote.quote_rendered == "<p>A <strong>dark</strong> time for all.</p>"


def test_character_creation_allow_creates_markov_model_object(user: User) -> None:
    """
    Test that creating a character also creates it's related markov model with initially empty data.
    """
    group = CharacterGroup.objects.create(name="Monkey", owner=user)
    character = Character.objects.create(name="Curious George", group=group, owner=user)
    assert CharacterMarkovModel.objects.get(character=character)


def test_group_creation_creates_markov_model(user: User) -> None:
    """
    Ensure that creating a character group also creates a GroupMarkov instance.
    """
    group = CharacterGroup.objects.create(name="Monkey", owner=user)
    assert GroupMarkovModel.objects.get(group=group)


def test_character_group_creation_generates_stats_object(user: User) -> None:
    """
    Test that the creation of either a character group or character creates its related
    stats object.
    """
    group = CharacterGroup.objects.create(name="Monkey", owner=user)
    assert GroupStats.objects.get(group=group)
    character = Character.objects.create(name="Curious George", group=group, owner=user)
    assert CharacterStats.objects.get(character=character)
    quote = Quote.objects.create(
        quote="I'm all a twitter.", character=character, owner=user
    )
    assert QuoteStats.objects.get(quote=quote)


@pytest.fixture
def statable_character(user):
    """
    Create a character suitable for stat collection.
    :param user: A user who owns the record.
    :return: Character object
    """
    group = CharacterGroup.objects.create(name="Monkey", owner=user)
    character = Character.objects.create(name="Curious George", group=group, owner=user)
    Quote.objects.create(quote="Silly little monkey.", character=character, owner=user)
    Quote.objects.create(
        quote="I need bananas or else I get the shakes.",
        character=character,
        owner=user,
    )
    Quote.objects.create(
        quote="I'm going to take your thumbs first.", character=character, owner=user
    )
    yield character
    group.delete()


def test_quote_retrieve_stat_signal(statable_character):
    """
    Test that stat are updated correctly when the signal is fired.
    :param statable_character: An instance of Character with stat objects attached
    """
    char_quotes_requested = statable_character.stats.quotes_requested
    group_quotes_requested = statable_character.group.stats.quotes_requested
    quote = statable_character.quote_set.all()[0]
    quote_usage = quote.stats.times_used
    quote_random_retrieved.send(
        Character, instance=statable_character, quote_retrieved=quote
    )
    statable_character.refresh_from_db()
    quote.refresh_from_db()
    assert char_quotes_requested < statable_character.stats.quotes_requested
    assert group_quotes_requested < statable_character.group.stats.quotes_requested
    assert quote_usage < quote.stats.times_used


def test_markov_stat_signal(statable_character):
    char_quotes_generated = statable_character.stats.quotes_generated
    group_quotes_generated = statable_character.group.stats.quotes_generated
    markov_sentence_generated.send(Character, instance=statable_character)
    statable_character.refresh_from_db()
    assert char_quotes_generated < statable_character.stats.quotes_generated
    assert group_quotes_generated < statable_character.group.stats.quotes_generated


# def test_quote_create_edit_markov_generation_signal(property_group):
#     character = property_group.character_set.filter(allow_markov=True)[0]
#     cmodel_lastmodify = CharacterMarkovModel.objects.get(character=character).modified
#     gmodel_lastmodify = GroupMarkovModel.objects.get(group=property_group).modified
#     q = Quote.objects.create(
#         quote="I am a new quote, full of exciting things to think about.",
#         character=character,
#         owner=property_group.owner,
#         citation="Some episode",
#     )
#     assert (
#         cmodel_lastmodify
#         < CharacterMarkovModel.objects.get(character=character).modified
#     )
#     assert (
#         gmodel_lastmodify < GroupMarkovModel.objects.get(group=property_group).modified
#     )
#     cmodel_lastmodify = CharacterMarkovModel.objects.get(character=character).modified
#     gmodel_lastmodify = GroupMarkovModel.objects.get(group=property_group).modified
#     q.quote = "Let's change things up a bit with a new quote."
#     q.save()
#     assert (
#         cmodel_lastmodify
#         < CharacterMarkovModel.objects.get(character=character).modified
#     )
#     assert (
#         gmodel_lastmodify < GroupMarkovModel.objects.get(group=property_group).modified
#     )
#
#
def test_character_set_to_allow_markov_regenerates_models(property_group):
    character = property_group.character_set.filter(allow_markov=False)[0]
    cmodel_lastmodify = CharacterMarkovModel.objects.get(character=character).modified
    gmodel_lastmodify = GroupMarkovModel.objects.get(group=property_group).modified
    character.allow_markov = True
    character.save()
    assert (
        cmodel_lastmodify
        < CharacterMarkovModel.objects.get(character=character).modified
    )
    assert (
        gmodel_lastmodify < GroupMarkovModel.objects.get(group=property_group).modified
    )
