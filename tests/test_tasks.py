# test_tasks.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from datetime import timedelta

import pytest
from django.utils import timezone
from django_quotes.models import Quote, QuoteCorpusError, Source
from django_quotes.tasks import update_models_on_quote_save

from django_markov.text_models import POSifiedText

pytestmark = pytest.mark.django_db(transaction=True)


def test_models_do_not_update_for_markov_disabled_sources(property_group):
    source = property_group.source_set.filter(allow_markov=False).first()
    quote = Quote.objects.create(
        quote="The snozberries taste like snozberries.", source=source, owner=property_group.owner
    )
    assert not update_models_on_quote_save(quote=quote)


def test_models_do_not_update_for_quote_with_future_pub_date(property_group):
    source = property_group.source_set.filter(allow_markov=True).first()
    quote = Quote.objects.create(
        quote="The snozberries taste like snozberries.",
        source=source,
        owner=property_group.owner,
        pub_date=timezone.now() + timedelta(days=1),
    )
    assert not update_models_on_quote_save(quote=quote)


def test_models_do_not_update_with_non_saved_quote(property_group):
    source = property_group.source_set.filter(allow_markov=True).first()
    quote = Quote(quote="The snozberries taste like snozberries.", source=source, owner=property_group.owner)
    assert not update_models_on_quote_save(quote=quote)


def test_models_do_not_update_for_source_with_limited_corpus(property_group):
    source = Source.objects.create(
        group=property_group,
        name="New Here",
        description="The hot new thing in town.",
        owner=property_group.owner,
        allow_markov=True,
    )
    Quote.objects.create(source=source, owner=property_group.owner, quote="I'm the first quote for New Here.")
    quote = Quote.objects.create(
        source=source, quote="The snozberries taste like snozberries.", owner=property_group.owner
    )
    assert not update_models_on_quote_save(quote)


def test_models_rollback_if_combine_error(property_group):
    sources = property_group.source_set.select_related("text_model").filter(allow_markov=True)[:2]
    # Now we compile the model and resave to make combining impossible.
    source = sources[1]
    compiled_source = sources[0]
    compiled_source.update_markov_model()
    mmodel = POSifiedText.from_json(compiled_source.text_model.data)
    mmodel.compile(inplace=True)
    compiled_source.text_model.data = mmodel.to_json()
    compiled_source.text_model.save()
    pre_update_source = source.text_model.modified
    pre_update_group = property_group.text_model.modified
    quote = Quote.objects.create(
        quote="The snozberries taste like snozberries.", source=source, owner=property_group.owner
    )
    with pytest.raises(QuoteCorpusError):
        update_models_on_quote_save(quote=quote)
    source.text_model.refresh_from_db()
    property_group.text_model.refresh_from_db()
    assert source.text_model.modified == pre_update_source
    assert property_group.text_model.modified == pre_update_group


def test_models_update_correctly_one_valid_source_model(property_group):
    source = property_group.source_set.select_related("text_model").filter(allow_markov=True).first()
    pre_update_source = source.text_model.modified
    pre_update_group = property_group.text_model.modified
    quote = Quote.objects.create(
        quote="The snozberries taste like snozberries.", source=source, owner=property_group.owner
    )
    assert update_models_on_quote_save(quote)
    source.text_model.refresh_from_db()
    property_group.text_model.refresh_from_db()
    assert source.text_model.modified > pre_update_source
    assert property_group.text_model.modified > pre_update_group


def test_models_update_correctly_multiple_valid_source_models(property_group):
    for source in (
        property_group.source_set.select_related("text_model").prefetch_related("quote_set").filter(allow_markov=True)
    ):
        source.update_markov_model()
    source = property_group.source_set.select_related("text_model").filter(allow_markov=True).first()
    pre_update_source = source.text_model.modified
    pre_update_group = property_group.text_model.modified
    quote = Quote.objects.create(
        quote="The snozberries taste like snozberries.", source=source, owner=property_group.owner
    )
    assert update_models_on_quote_save(quote=quote)
    source.text_model.refresh_from_db()
    property_group.text_model.refresh_from_db()
    assert source.text_model.modified > pre_update_source
    assert property_group.text_model.modified > pre_update_group
