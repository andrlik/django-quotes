# tasks.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

"""Utility tasks for use with distributed queues."""

from django.db.transaction import atomic
from django.utils import timezone

from django_markov.models import MarkovCombineError
from django_quotes.models import Quote, QuoteCorpusError


def update_models_on_quote_save(quote: Quote) -> bool:
    """Evaluate the quote to see if the source and group Markov models require updates
    and then execute those updates.

    Args:
        quote (Quote): A Quote instance

    Returns:
        bool: True if the source and group were updated, False otherwise, i.e. because update was not required.
    """
    if not quote.id or quote.modified < quote.source.text_model.modified or not quote.source.markov_ready:  # type: ignore
        return False  # We don't update based off of an unsaved quote, or if we pass an older quote.
    if quote.pub_date is not None and quote.pub_date > timezone.now():
        return False
    try:
        with atomic():
            quote.source.update_markov_model()
            quote.source.group.update_markov_model()
    except MarkovCombineError as mce:
        msg = f"Encountered an error when combining source models to the group model: {mce}"
        raise QuoteCorpusError(msg) from mce
    return True
