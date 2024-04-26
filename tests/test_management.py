# test_management.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause

from io import StringIO

import pytest
from django.core.management import call_command
from django_quotes.models import SourceGroup

from django_markov.models import MarkovTextModel

pytestmark = pytest.mark.django_db(transaction=True)


def test_markov_command(property_group):
    pgmm = property_group.text_model
    source = property_group.source_set.select_related("text_model").filter(allow_markov=True)[0]
    group_modify = pgmm.modified
    cmm = source.text_model
    char_modify = cmm.modified
    nochangegroup = SourceGroup.objects.create(
        name="So Alone", owner=property_group.owner, text_model=MarkovTextModel.objects.create()
    )
    nochange_modify = nochangegroup.text_model.modified
    out = StringIO()
    call_command("makemarkov", stdout=out, stderr=StringIO())
    assert nochange_modify == MarkovTextModel.objects.get(pk=nochangegroup.text_model.pk).modified
    pgmm.refresh_from_db()
    cmm.refresh_from_db()
    assert group_modify < pgmm.modified
    assert char_modify < cmm.modified
    assert pgmm.data is not None
    assert cmm.data is not None
