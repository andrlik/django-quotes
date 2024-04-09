#
# test_utils.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

from __future__ import annotations

import re

import pytest
from django.contrib.auth import get_user_model
from django_quotes.models import SourceGroup
from django_quotes.utils import generate_unique_slug_for_model

pytestmark = pytest.mark.django_db(transaction=True)

User = get_user_model()


def test_unique_generate_unique_slug(user: User):
    sg = SourceGroup.objects.create(name="Explorers Wanted", slug="ew", owner=user)  # Would have a slug of `ew`
    result = generate_unique_slug_for_model(SourceGroup, "EW")
    assert result != sg.slug


@pytest.mark.parametrize(
    "max_length,int_like,slug_truncated",
    [
        (17, True, True),
        (18, False, False),
    ],
)
def test_unique_slug_conforms_to_specified_length(
    user: User, max_length: int | None, int_like: bool, slug_truncated: bool
):
    ends_in_number = re.compile(r"\d+$")
    podcast_title: str = "I'm a podcast with a following"
    control_sample_slug: str = "i-m-a-podcast-wit"
    SourceGroup.objects.create(name=podcast_title, slug=control_sample_slug, owner=user)
    result = generate_unique_slug_for_model(SourceGroup, podcast_title, max_length_override=max_length)
    assert len(result) <= max_length
    if int_like:
        assert ends_in_number.search(result)
    if slug_truncated:
        assert control_sample_slug not in result
