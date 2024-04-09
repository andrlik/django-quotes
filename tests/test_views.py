#
# test_views.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

import pytest
from django.core.exceptions import ObjectDoesNotExist
from django.urls import reverse
from django_quotes.models import Quote, Source, SourceGroup

from tests.factories.users import UserFactory

pytestmark = pytest.mark.django_db(transaction=True)

# FIXTURES


@pytest.fixture
def c_groups_user(user):
    """

    :param user: A user object from the user fixture
    :return: A list of created groups to use in tests
    """
    user2 = UserFactory()
    group_list = []
    group_list.append(SourceGroup.objects.create(name="Group1", owner=user))
    group_list.append(SourceGroup.objects.create(name="Group2", owner=user))
    group_list.append(SourceGroup.objects.create(name="Group3", owner=user2))
    c1 = Source.objects.create(name="Johnny Boy", group=group_list[0], owner=user)
    Source.objects.create(name="Mary", group=group_list[0], owner=user)
    c2 = Source.objects.create(name="Markus", group=group_list[1], owner=user)
    Quote.objects.create(quote="Up is down.", source=c1, owner=user)
    Quote.objects.create(quote="Down is up", source=c1, owner=user)
    Quote.objects.create(quote="Bananas are a growth industry", source=c2, owner=user)
    yield user  # The user with the two groups associated with them.
    for group in group_list:
        group.delete()
    user2.delete()


# SOURCE GROUP TESTS


def test_group_list_view(client, c_groups_user, django_assert_max_num_queries):
    """
    Tests for expected results for the group list view.
    :param c_groups_user: User from the fixture
    :return:
    """
    client.force_login(user=c_groups_user)
    url = reverse("quotes:group_list")
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 200
    assert len(response.context["groups"]) == 2


@pytest.mark.parametrize("view_name", ["quotes:group_list", "quotes:group_create"])
def test_group_requires_login(client, view_name):
    url = reverse(view_name)
    response = client.get(url)
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


def test_group_create(client, django_assert_max_num_queries, user):
    url = reverse("quotes:group_create")
    client.force_login(user)
    existing_groups = SourceGroup.objects.filter(owner=user).count()
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 200
    with django_assert_max_num_queries(50):
        response = client.post(url, data={"name": "John Snow", "description": "Knows nothing"})
    assert response.status_code == 302
    assert SourceGroup.objects.filter(owner=user).count() - existing_groups == 1


@pytest.mark.parametrize("view_name", ["quotes:group_detail", "quotes:group_update", "quotes:group_delete"])
def test_groups_single_object_view_requires_login(client, c_groups_user, view_name):
    group = SourceGroup.objects.filter(owner=c_groups_user)[0]
    url = reverse(view_name, kwargs={"group": group.slug})
    response = client.get(url)
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


def test_group_detail_view_for_owner(client, django_assert_max_num_queries, c_groups_user):
    group = SourceGroup.objects.filter(owner=c_groups_user)[0]
    url = reverse("quotes:group_detail", kwargs={"group": group.slug})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 200


def test_group_detail_for_other_user(client, django_assert_max_num_queries, c_groups_user):
    group = SourceGroup.objects.filter(owner=c_groups_user)[0]
    url = reverse("quotes:group_detail", kwargs={"group": group.slug})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 403


def test_group_update_access_restricted_to_owner(client, django_assert_max_num_queries, c_groups_user):
    group = SourceGroup.objects.filter(owner=c_groups_user)[0]
    url = reverse("quotes:group_update", kwargs={"group": group.slug})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 403
    with django_assert_max_num_queries(50):
        response = client.post(url, data={"name": "Doodle", "description": "I **hate** you"})
    assert response.status_code == 403
    group.refresh_from_db()
    assert group.description != "I **hate** you"


def test_group_update_by_owner(client, django_assert_max_num_queries, c_groups_user):
    group = SourceGroup.objects.filter(owner=c_groups_user)[0]
    url = reverse("quotes:group_update", kwargs={"group": group.slug})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 200
    with django_assert_max_num_queries(50):
        response = client.post(url, data={"name": "Jon Snow", "description": "Knows nothing"})
    assert response.status_code == 302
    group.refresh_from_db()
    assert group.description == "Knows nothing"


def test_group_delete_not_accessible_by_non_owner(client, django_assert_max_num_queries, c_groups_user):
    group = SourceGroup.objects.filter(owner=c_groups_user)[0]
    group_num = SourceGroup.objects.filter(owner=c_groups_user).count()
    url = reverse("quotes:group_delete", kwargs={"group": group.slug})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 403
    with django_assert_max_num_queries(50):
        response = client.post(url, data={})
    assert response.status_code == 403
    assert group_num == SourceGroup.objects.filter(owner=c_groups_user).count()


def test_group_delete(client, django_assert_max_num_queries, c_groups_user):
    group = SourceGroup.objects.filter(owner=c_groups_user)[0]
    group_num = SourceGroup.objects.filter(owner=c_groups_user).count()
    url = reverse("quotes:group_delete", kwargs={"group": group.slug})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 200
    with django_assert_max_num_queries(50):
        response = client.post(url, data={})
    assert response.status_code == 302
    assert group_num - SourceGroup.objects.filter(owner=c_groups_user).count() == 1


# SOURCE TESTS


@pytest.mark.parametrize("view_name", ["quotes:source_list", "quotes:source_create"])
def test_source_list_requires_login(client, c_groups_user, view_name):
    group = SourceGroup.objects.get(name="Group1")
    url = reverse(view_name, kwargs={"group": group.slug})
    response = client.get(url)
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


@pytest.mark.parametrize("view_name", ["quotes:source_list", "quotes:source_create"])
def test_unauthorized_source_list_access(client, django_assert_max_num_queries, c_groups_user, view_name):
    group = SourceGroup.objects.get(name="Group1")
    url = reverse(view_name, kwargs={"group": group.slug})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 403


def test_authorized_source_list_access(client, django_assert_max_num_queries, c_groups_user):
    group = SourceGroup.objects.get(name="Group1")
    url = reverse("quotes:source_list", kwargs={"group": group.slug})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 200
    assert response.context["sources"].count() == 2


def test_unauthorized_source_create(client, django_assert_max_num_queries, c_groups_user):
    group = SourceGroup.objects.get(name="Group1")
    source_number = Source.objects.filter(group=group).count()
    url = reverse("quotes:source_create", kwargs={"group": group.slug})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.post(url, data={"name": "John Snow"})
    assert response.status_code == 403
    assert source_number == Source.objects.filter(group=group).count()


def test_authorized_source_create(client, django_assert_max_num_queries, c_groups_user):
    group = SourceGroup.objects.get(name="Group1")
    source_number = Source.objects.filter(group=group).count()
    url = reverse("quotes:source_create", kwargs={"group": group.slug})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 200
    with django_assert_max_num_queries(50):
        response = client.post(url, data={"name": "Peter Parker"})
    assert response.status_code == 302
    assert Source.objects.filter(group=group).count() - source_number == 1


@pytest.mark.parametrize(
    "view_name",
    ["quotes:source_detail", "quotes:source_update", "quotes:source_delete"],
)
def test_get_views_for_source_require_login(client, c_groups_user, view_name):
    url = reverse(view_name, kwargs={"source": "group1-johnny-boy"})
    response = client.get(url)
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


@pytest.mark.parametrize(
    "view_name",
    ["quotes:source_detail", "quotes:source_update", "quotes:source_delete"],
)
def test_get_views_for_source_unauthorized(client, django_assert_max_num_queries, c_groups_user, view_name):
    url = reverse(view_name, kwargs={"source": "group1-johnny-boy"})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.parametrize(
    "view_name",
    ["quotes:source_detail", "quotes:source_update", "quotes:source_delete"],
)
def test_get_views_source_authorized(client, django_assert_max_num_queries, c_groups_user, view_name):
    url = reverse(view_name, kwargs={"source": "group1-johnny-boy"})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 200


def test_edit_source_view_unauthorized(client, django_assert_max_num_queries, c_groups_user):
    url = reverse("quotes:source_update", kwargs={"source": "group1-johnny-boy"})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.post(url, data={"name": "Johnny Boy", "description": "Eats worms"})
    assert response.status_code == 403
    assert Source.objects.get(slug="group1-johnny-boy").description != "Eats worms"


def test_delete_source_unauthorized(client, django_assert_max_num_queries, c_groups_user):
    url = reverse("quotes:source_delete", kwargs={"source": "group1-johnny-boy"})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.post(url, data={})
    assert response.status_code == 403
    assert Source.objects.get(slug="group1-johnny-boy")


def test_authorized_source_edit(client, django_assert_max_num_queries, c_groups_user):
    url = reverse("quotes:source_update", kwargs={"source": "group1-johnny-boy"})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.post(url, data={"name": "Johnny Boy", "description": "Dances in the dark"})
    assert response.status_code == 302
    assert Source.objects.get(slug="group1-johnny-boy").description == "Dances in the dark"


def test_authorized_source_delete(client, django_assert_max_num_queries, c_groups_user):
    url = reverse("quotes:source_delete", kwargs={"source": "group1-johnny-boy"})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.post(url, data={})
    assert response.status_code == 302
    with pytest.raises(ObjectDoesNotExist):
        Source.objects.get(slug="group1-johnny-boy")


# QUOTES


@pytest.mark.parametrize("view_name", ["quotes:quote_list", "quotes:quote_create"])
def test_list_create_quotes_requires_login(client, c_groups_user, view_name):
    source = Source.objects.get(slug="group1-johnny-boy")
    url = reverse(view_name, kwargs={"source": source.slug})
    response = client.get(url)
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


@pytest.mark.parametrize("view_name", ["quotes:quote_list", "quotes:quote_create"])
def test_get_list_create_quotes_unauthorized(client, django_assert_max_num_queries, c_groups_user, view_name):
    source = Source.objects.get(slug="group1-johnny-boy")
    url = reverse(view_name, kwargs={"source": source.slug})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 403


def test_list_quote_authorized(client, django_assert_max_num_queries, c_groups_user):
    source = Source.objects.get(slug="group1-johnny-boy")
    url = reverse("quotes:quote_list", kwargs={"source": source.slug})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 200


def test_unauthorized_create_quote(client, django_assert_max_num_queries, c_groups_user):
    source = Source.objects.get(slug="group1-johnny-boy")
    quote_num = source.quote_set.count()
    url = reverse("quotes:quote_create", kwargs={"source": source.slug})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.post(url, data={"quote": "I want all the ham"})
    assert response.status_code == 403
    assert quote_num == Quote.objects.filter(source=source).count()


def test_authorized_create_quote(client, django_assert_max_num_queries, c_groups_user):
    source = Source.objects.get(slug="group1-johnny-boy")
    quote_num = source.quote_set.count()
    url = reverse("quotes:quote_create", kwargs={"source": source.slug})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 200
    with django_assert_max_num_queries(50):
        response = client.post(url, data={"quote": "I want all the ham"})
    assert response.status_code == 302
    assert Quote.objects.filter(source=source).count() - quote_num == 1


@pytest.mark.parametrize("view_name", ["quotes:quote_detail", "quotes:quote_update", "quotes:quote_delete"])
def test_get_views_quote_detail_require_login(client, c_groups_user, view_name):
    quote = Quote.objects.select_related("source").filter(source__slug="group1-johnny-boy")[0]
    url = reverse(view_name, kwargs={"quote": quote.id})
    response = client.get(url)
    assert response.status_code == 302
    assert "/accounts/login/" in response["Location"]


@pytest.mark.parametrize("view_name", ["quotes:quote_detail", "quotes:quote_update", "quotes:quote_delete"])
def test_get_views_quote_detail_unauthorized(client, django_assert_max_num_queries, c_groups_user, view_name):
    quote = Quote.objects.select_related("source").filter(source__slug="group1-johnny-boy")[0]
    url = reverse(view_name, kwargs={"quote": quote.id})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 403


@pytest.mark.parametrize("view_name", ["quotes:quote_detail", "quotes:quote_update", "quotes:quote_delete"])
def test_get_views_quote_detail_authorized(client, django_assert_max_num_queries, c_groups_user, view_name):
    quote = Quote.objects.select_related("source").filter(source__slug="group1-johnny-boy")[0]
    url = reverse(view_name, kwargs={"quote": quote.id})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.get(url)
    assert response.status_code == 200


def test_quote_edit_unauthorized(client, django_assert_max_num_queries, c_groups_user):
    quote = Quote.objects.select_related("source").filter(source__slug="group1-johnny-boy")[0]
    url = reverse("quotes:quote_update", kwargs={"quote": quote.id})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.post(url, data={"quote": "I ate too much pie"})
    assert response.status_code == 403
    quote.refresh_from_db()
    assert quote.quote != "I ate too much pie"


def test_quote_edit_authorized(client, django_assert_max_num_queries, c_groups_user):
    quote = Quote.objects.select_related("source").filter(source__slug="group1-johnny-boy")[0]
    url = reverse("quotes:quote_update", kwargs={"quote": quote.id})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.post(url, data={"quote": "I ate too much pie"})
    assert response.status_code == 302
    quote.refresh_from_db()
    assert quote.quote == "I ate too much pie"


def test_quote_delete_unauthorized(client, django_assert_max_num_queries, c_groups_user):
    quote = Quote.objects.select_related("source").filter(source__slug="group1-johnny-boy")[0]
    url = reverse("quotes:quote_delete", kwargs={"quote": quote.id})
    client.force_login(UserFactory())
    with django_assert_max_num_queries(50):
        response = client.post(url, data={})
    assert response.status_code == 403
    assert Quote.objects.get(id=quote.id)


def test_quote_delete_authorized(client, django_assert_max_num_queries, c_groups_user):
    quote = Quote.objects.select_related("source").filter(source__slug="group1-johnny-boy")[0]
    url = reverse("quotes:quote_delete", kwargs={"quote": quote.id})
    client.force_login(c_groups_user)
    with django_assert_max_num_queries(50):
        response = client.post(url, data={})
    assert response.status_code == 302
    with pytest.raises(ObjectDoesNotExist):
        Quote.objects.get(id=quote.id)
