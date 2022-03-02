import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError

from django_quotes.models import Character, CharacterGroup, Quote

User = get_user_model()

pytestmark = pytest.mark.django_db(transaction=True)


def test_generate_group_slug(user: User) -> None:
    """
    Test the slug generation for character groups.
    :param user: The logged in user.
    :return:
    """
    group = CharacterGroup.objects.create(name="Curious George", owner=user)
    assert group.slug == "curious-george"


def test_ensure_group_slug_unique(user: User) -> None:
    CharacterGroup.objects.create(name="EW", owner=user)
    with pytest.raises(IntegrityError):
        CharacterGroup.objects.create(name="Explorers Wanted", slug="ew", owner=user)


def test_generate_character_slug(user: User) -> None:
    """
    Tests the slug generation for characters to ensure it's being set up correctly.

    :param user: The user who is currently logged in.
    :return:
    """
    group = CharacterGroup.objects.create(name="Monkey", owner=user)
    character = Character.objects.create(name="John Smith", group=group, owner=user)
    assert character.slug == "monkey-john-smith"


@pytest.mark.parametrize(
    "group1,group2,character_name,slug",
    [
        ("EW", "Explorers Wanted", "John Smith", "ew-john-smith"),
    ],
)
def test_reject_character_duplicate_slug(
    user: User, group1: str, group2: str, character_name: str, slug: str
) -> None:
    """
    :param group1: Name of the first group
    :param group2: Name of the second group
    :param character_name: Name of the character.
    :param slug: Slug to override.
    :param user: The user who is currently logged in.
    :return:
    """
    group = CharacterGroup.objects.create(name=group1, owner=user)
    Character.objects.create(name=character_name, group=group, owner=user)
    group2 = CharacterGroup.objects.create(name=group2, owner=user)
    with pytest.raises(IntegrityError):
        Character.objects.create(
            name=character_name, group=group2, slug=slug, owner=user
        )


def test_group_properties_calculation(property_group: CharacterGroup) -> None:
    assert property_group.total_characters == 10
    assert property_group.markov_characters == 5
    assert property_group.total_quotes == 200


def test_refresh_from_db_also_updates_cached_properties(
    property_group: CharacterGroup, user: User
) -> None:
    assert property_group.total_characters == 10
    assert property_group.markov_characters == 5
    assert property_group.total_quotes == 200
    c = Character.objects.create(
        name="IamNew", group=property_group, allow_markov=True, owner=user
    )
    Quote.objects.create(character=c, quote="I'm a new quote", owner=user)
    assert property_group.total_characters == 10
    assert property_group.markov_characters == 5
    assert property_group.total_quotes == 200
    property_group.refresh_from_db()
    assert property_group.total_characters == 11
    assert property_group.markov_characters == 6
    assert property_group.total_quotes == 201


def test_retrieve_random_quote(property_group):
    noquote_character = Character.objects.create(
        group=property_group, name="No One", owner=property_group.owner
    )
    assert noquote_character.get_random_quote() is None
    noquote_character.delete()
    quoteable_character = Character.objects.filter(group=property_group)[0]
    assert type(quoteable_character.get_random_quote()) == Quote


def test_generate_markov_sentence(property_group):
    noquote_character = Character.objects.create(
        group=property_group, name="No One", owner=property_group.owner
    )
    assert noquote_character.get_markov_sentence() is None
    noquote_character.delete()
    quotable_character = Character.objects.filter(group=property_group)[0]
    sentence = quotable_character.get_markov_sentence()
    print(sentence)
    assert isinstance(sentence, str)


def test_get_random_group_quote(property_group):
    noquote_group = CharacterGroup.objects.create(
        name="I am no one.", owner=property_group.owner
    )
    assert noquote_group.get_random_quote() is None
    assert isinstance(property_group.get_random_quote(), Quote)


def test_group_generate_markov_sentence(property_group, corpus_sentences):
    no_quote_group = CharacterGroup.objects.create(
        name="We are no one.", owner=property_group.owner
    )
    Character.objects.create(
        name="John Doe",
        group=no_quote_group,
        allow_markov=True,
        owner=property_group.owner,
    )
    quote_character = Character.objects.create(
        name="Jane Doe",
        group=no_quote_group,
        allow_markov=False,
        owner=property_group.owner,
    )
    for sentence in corpus_sentences:
        Quote.objects.create(
            character=quote_character, quote=sentence, owner=property_group.owner
        )
    assert no_quote_group.generate_markov_sentence() is None
    assert property_group.generate_markov_sentence() is not None
