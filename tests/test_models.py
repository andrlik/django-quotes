# test_models.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from datetime import timedelta

import pytest
from django.contrib.auth import get_user_model
from django.db import IntegrityError
from django.utils import timezone
from django_quotes.models import Quote, QuoteCorpusError, Source, SourceGroup

from django_markov.text_models import POSifiedText

User = get_user_model()

pytestmark = pytest.mark.django_db(transaction=True)


def test_generate_group_slug(user: User) -> None:
    """
    Test the slug generation for source groups.
    :param user: The logged in user.
    :return:
    """
    group = SourceGroup.objects.create(name="Curious George", owner=user)
    assert group.slug == "curious-george"


def test_generate_source_slug(user: User) -> None:
    """
    Tests the slug generation for sources to ensure it's being set up correctly.

    :param user: The user who is currently logged in.
    :return:
    """
    group = SourceGroup.objects.create(name="Monkey", owner=user)
    source = Source.objects.create(name="John Smith", group=group, owner=user)
    assert source.slug == "monkey-john-smith"


def test_quote_rendered(property_group):
    source = property_group.source_set.first()
    quote = Quote.objects.create(quote="", source=source, owner=property_group.owner)
    assert quote.quote_rendered == ""


@pytest.mark.parametrize(
    "group1,group2,source_name,slug",
    [
        ("EW", "Explorers Wanted", "John Smith", "ew-john-smith"),
    ],
)
def test_reject_source_duplicate_slug(user: User, group1: str, group2: str, source_name: str, slug: str) -> None:
    """
    :param group1: Name of the first group
    :param group2: Name of the second group
    :param source_name: Name of the source.
    :param slug: Slug to override.
    :param user: The user who is currently logged in.
    :return:
    """
    group = SourceGroup.objects.create(name=group1, owner=user)
    Source.objects.create(name=source_name, group=group, owner=user)
    group2 = SourceGroup.objects.create(name=group2, owner=user)
    with pytest.raises(IntegrityError):
        Source.objects.create(name=source_name, group=group2, slug=slug, owner=user)


def test_group_properties_calculation(property_group: SourceGroup) -> None:
    assert property_group.total_sources == 10
    assert property_group.markov_sources == 5
    assert property_group.total_quotes == 200


@pytest.mark.asyncio
async def test_async_markov_ready(property_group) -> None:
    valid_source = await property_group.source_set.select_related("text_model").filter(allow_markov=True).afirst()
    valid_source_with_small_corpus = await Source.objects.acreate(
        group=property_group, owner=property_group.owner, name="Quiet", allow_markov=True
    )
    await Quote.objects.acreate(
        quote="Shh, I'm being sneaky.", source=valid_source_with_small_corpus, owner=property_group.owner
    )
    invalid_source = await property_group.source_set.select_related("text_model").filter(allow_markov=False).afirst()
    assert await valid_source._amarkov_ready()
    assert not await valid_source_with_small_corpus._amarkov_ready()
    assert not await invalid_source._amarkov_ready()


def test_refresh_from_db_also_updates_cached_properties(property_group: SourceGroup, user: User) -> None:
    assert property_group.total_sources == 10
    assert property_group.markov_sources == 5
    assert property_group.total_quotes == 200
    c = Source.objects.create(name="IamNew", group=property_group, allow_markov=True, owner=user)
    Quote.objects.create(source=c, quote="I'm a new quote", owner=user)
    assert property_group.total_sources == 10
    assert property_group.markov_sources == 5
    assert property_group.total_quotes == 200
    property_group.refresh_from_db()
    assert property_group.total_sources == 11
    assert property_group.markov_sources == 6
    assert property_group.total_quotes == 201


def test_retrieve_random_quote(property_group):
    noquote_source = Source.objects.create(group=property_group, name="No One", owner=property_group.owner)
    assert noquote_source.get_random_quote() is None
    noquote_source.delete()
    quoteable_source = Source.objects.filter(group=property_group)[0]
    assert type(quoteable_source.get_random_quote()) == Quote


def test_generate_markov_sentence(property_group):
    noquote_source = Source.objects.create(group=property_group, name="No One", owner=property_group.owner)
    assert noquote_source.get_markov_sentence() is None
    noquote_source.delete()
    quotable_source = Source.objects.filter(group=property_group, allow_markov=True)[0]
    sentence = quotable_source.get_markov_sentence(tries=50)
    print(sentence)
    assert isinstance(sentence, str)


def test_get_random_group_quote(property_group):
    noquote_group = SourceGroup.objects.create(name="I am no one.", owner=property_group.owner)
    assert noquote_group.get_random_quote() is None
    assert isinstance(property_group.get_random_quote(), Quote)


def test_group_generate_markov_sentence(property_group, corpus_sentences):
    no_quote_group = SourceGroup.objects.create(name="We are no one.", owner=property_group.owner)
    Source.objects.create(
        name="John Doe",
        group=no_quote_group,
        allow_markov=True,
        owner=property_group.owner,
    )
    quote_source = Source.objects.create(
        name="Jane Doe",
        group=no_quote_group,
        allow_markov=False,
        owner=property_group.owner,
    )
    for sentence in corpus_sentences:
        Quote.objects.create(source=quote_source, quote=sentence, owner=property_group.owner)
    for source in property_group.source_set.select_related("text_model").filter(allow_markov=True):
        if source.markov_ready:
            source.update_markov_model()
    assert no_quote_group.generate_markov_sentence() is None
    assert property_group.generate_markov_sentence(tries=50) is not None


def test_pub_date_prevents_inclusion_in_source_random_quote(property_group):
    new_source = Source.objects.create(group=property_group, name="Future Man", owner=property_group.owner)
    q = Quote.objects.create(
        source=new_source,
        quote="This message is from the **future**!",
        pub_date=timezone.now() + timedelta(days=4),
        owner=property_group.owner,
    )
    assert Quote.objects.filter(source=new_source).count() == 1
    assert new_source.get_random_quote() is None
    q.pub_date = timezone.now() - timedelta(days=2)
    q.save()
    assert new_source.get_random_quote() == q


def test_pub_date_prevents_inclusion_in_group_random_quote(property_group):
    new_group = SourceGroup.objects.create(name="Future Group", owner=property_group.owner)
    new_source = Source.objects.create(group=new_group, owner=new_group.owner, name="Future Man")
    q = Quote.objects.create(
        source=new_source,
        quote="This message is from the **future**!",
        pub_date=timezone.now() + timedelta(days=4),
        owner=property_group.owner,
    )
    assert Quote.objects.filter(source__group=new_group).count() == 1
    assert new_group.get_random_quote() is None
    q.pub_date = timezone.now() - timedelta(days=2)
    q.save()
    assert new_group.get_random_quote() == q


def test_add_quote_to_model_compile_fail(property_group):
    sources = (
        property_group.source_set.select_related("text_model", "group", "group__text_model")
        .prefetch_related("quote_set")
        .filter(allow_markov=True)
    )
    for source in sources:
        source.update_markov_model()
    property_group.update_markov_model()
    source_one = sources.first()
    source_two = sources.exclude(pk=source_one.pk).last()
    # We grab a quote from another source to bypass any automated updates.
    quote = source_one.quote_set.first()
    # Now we go and compile source_two's models to ensure they won't be compatible.
    model_to_compile = POSifiedText.from_json(source_two.text_model.data)
    model_to_compile.compile(inplace=True)
    source_two.text_model.data = model_to_compile.to_json()
    source_two.text_model.save()
    old_source_modify = source_two.text_model.modified
    old_group_modify = property_group.text_model.modified
    with pytest.raises(QuoteCorpusError):
        source_two.add_new_quote_to_model(quote)
    source_two.text_model.refresh_from_db()
    property_group.text_model.refresh_from_db()
    assert source_two.text_model.modified == old_source_modify
    assert property_group.text_model.modified == old_group_modify


def test_add_quote_to_text_models_success(property_group):
    sources = (
        property_group.source_set.select_related("text_model", "group", "group__text_model")
        .prefetch_related("quote_set")
        .filter(allow_markov=True)
    )
    for source in sources:
        source.update_markov_model()
    property_group.update_markov_model()
    source_one = sources.first()
    source_two = sources.exclude(pk=source_one.pk).last()
    old_source_modify = source_two.text_model.modified
    old_group_modify = property_group.text_model.modified
    # We grab a quote from another source to bypass any automated updates.
    quote = source_one.quote_set.first()
    source_two.add_new_quote_to_model(quote)
    source_two.text_model.refresh_from_db()
    property_group.text_model.refresh_from_db()
    assert source_two.text_model.modified > old_source_modify
    assert property_group.text_model.modified > old_group_modify


def test_add_quote_to_too_small_corpus(property_group):
    other_source = (
        property_group.source_set.select_related("text_model", "group", "group__text_model")
        .prefetch_related("quote_set")
        .filter(allow_markov=True)
        .first()
    )
    source = Source.objects.create(
        group=property_group, name="Future Man", owner=property_group.owner, allow_markov=True
    )
    assert source.text_model is not None
    Quote.objects.create(quote="I love these snakes!", source=source, owner=source.owner)
    source.update_markov_model()
    old_source_modify = source.text_model.modified
    old_group_modify = property_group.text_model.modified
    new_quote = other_source.quote_set.first()
    source.add_new_quote_to_model(new_quote)
    source.text_model.refresh_from_db()
    source.group.text_model.refresh_from_db()
    assert old_source_modify == source.text_model.modified
    assert old_group_modify == property_group.text_model.modified


def test_add_quote_with_markov_disabled_fails(property_group):
    other_source = (
        property_group.source_set.select_related("text_model", "group", "group__text_model")
        .prefetch_related("quote_set")
        .filter(allow_markov=True)
        .first()
    )
    source = (
        property_group.source_set.select_related("text_model", "group", "group__text_model")
        .prefetch_related("quote_set")
        .filter(allow_markov=False)
        .first()
    )
    source.update_markov_model()
    source.text_model.refresh_from_db()
    old_source_modify = source.text_model.modified
    old_group_modify = property_group.text_model.modified
    quote = other_source.quote_set.first()
    source.add_new_quote_to_model(quote)
    source.text_model.refresh_from_db()
    source.group.text_model.refresh_from_db()
    assert source.text_model.modified == old_source_modify
    assert property_group.text_model.modified == old_group_modify


def test_add_quote_to_model_fallback_on_empty_model(property_group):
    other_source = (
        property_group.source_set.select_related("text_model", "group", "group__text_model")
        .prefetch_related("quote_set")
        .filter(allow_markov=True)
        .first()
    )
    source = (
        property_group.source_set.select_related("text_model", "group", "group__text_model")
        .prefetch_related("quote_set")
        .filter(allow_markov=True)
        .exclude(pk=other_source.pk)
        .first()
    )
    source.text_model.data = None
    source.text_model.save()
    source.text_model.refresh_from_db()
    old_source_modify = source.text_model.modified
    old_group_modify = property_group.text_model.modified
    new_quote = other_source.quote_set.first()
    source.add_new_quote_to_model(new_quote)
    source.text_model.refresh_from_db()
    property_group.text_model.refresh_from_db()
    assert source.text_model.modified > old_source_modify
    assert property_group.text_model.modified > old_group_modify
