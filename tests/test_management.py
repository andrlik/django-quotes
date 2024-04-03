from io import StringIO

import pytest
from django.core.management import call_command
from django_quotes.models import GroupMarkovModel, SourceGroup, SourceMarkovModel

pytestmark = pytest.mark.django_db(transaction=True)


def test_markov_command(property_group):
    pgmm = GroupMarkovModel.objects.get(group=property_group)
    source = property_group.source_set.filter(allow_markov=True)[0]
    group_modify = pgmm.modified
    cmm = SourceMarkovModel.objects.get(source=source)
    char_modify = cmm.modified
    nochangegroup = SourceGroup.objects.create(name="So Alone", owner=property_group.owner)
    nochange_modify = GroupMarkovModel.objects.get(group=nochangegroup).modified
    out = StringIO()
    call_command("makemarkov", stdout=out, stderr=StringIO())
    assert nochange_modify == GroupMarkovModel.objects.get(group=nochangegroup).modified
    pgmm.refresh_from_db()
    cmm.refresh_from_db()
    assert group_modify < pgmm.modified
    assert char_modify < cmm.modified
    assert pgmm.data is not None
    assert cmm.data is not None
