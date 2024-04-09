#
# test_api.py
#
# Copyright (c) 2024 Daniel Andrlik
# All rights reserved.
#
# SPDX-License-Identifier: BSD-3-Clause
#

import pytest
from django.test import RequestFactory
from django.urls import reverse
from django_quotes.api.serializers import SourceSerializer
from django_quotes.api.views import SourceGroupViewSet
from django_quotes.models import Source, SourceGroup
from rest_framework import status
from rest_framework.test import APIClient

from tests.factories.users import UserFactory

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def apiclient():
    return APIClient()


class TestGroupViewSet:
    def test_list_groups(self, property_group: SourceGroup, rf: RequestFactory) -> None:
        view = SourceGroupViewSet()
        request = rf.get("/ignorethisurl/")
        request.user = property_group.owner
        view.request = request
        assert property_group in view.get_queryset()

    def test_retrieve_group(self, apiclient, property_group):
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(
            reverse("api:group-detail", kwargs={"group": property_group.slug}),
            format="json",
        )
        assert response.status_code == status.HTTP_200_OK

    def test_empty_random_quote(self, apiclient):
        user = UserFactory()
        apiclient.force_authenticate(user=user)
        group = SourceGroup.objects.create(name="Nothing here", owner=user)
        response = apiclient.get(
            reverse("api:group-get-random-quote", kwargs={"group": group.slug}),
            format="json",
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_random_quote(self, apiclient, property_group):
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(
            reverse(
                "api:group-get-random-quote",
                kwargs={"group": property_group.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK

    def test_markov_group(self, apiclient, property_group):
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(reverse("api:group-generate-sentence", kwargs={"group": property_group.slug}))
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]

    def test_disallowed_markov_group(self, apiclient):
        user = UserFactory()
        group = SourceGroup.objects.create(name="Nothing here", owner=user)
        Source.objects.create(name="No Fun", group=group, owner=user, allow_markov=False)
        apiclient.force_authenticate(user=user)
        response = apiclient.get(reverse("api:group-generate-sentence", kwargs={"group": group.slug}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_empty_markov_group(self, apiclient):
        user = UserFactory()
        group = SourceGroup.objects.create(name="Nothing here", owner=user)
        Source.objects.create(name="No Fun", group=group, owner=user, allow_markov=True)
        apiclient.force_authenticate(user=user)
        response = apiclient.get(reverse("api:group-generate-sentence", kwargs={"group": group.slug}))
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestSourceViewSet:
    def test_list_sources(self, apiclient, property_group):
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(reverse("api:source-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_list_sources_by_group(self, apiclient, property_group):
        apiclient.force_authenticate(user=property_group.owner)
        extra_group = SourceGroup.objects.create(name="I'm extra", owner=property_group.owner)
        Source.objects.create(name="Bobble the Odd", group=extra_group, owner=property_group.owner)
        response = apiclient.get(reverse("api:source-list") + f"?group={property_group.slug}")
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == property_group.source_set.count()

    def test_filter_by_nonexistent_group(self, apiclient, property_group):
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(reverse("api:source-list") + "?group=sayonara")
        assert len(response.data) == 0
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_source(self, apiclient, property_group):
        char_to_retrieve = property_group.source_set.all()[0]
        serializer = SourceSerializer(char_to_retrieve)
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(reverse("api:source-detail", kwargs={"source": char_to_retrieve.slug}))
        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_source_random_quote(self, apiclient, property_group):
        char_to_retrieve = property_group.source_set.all()[0]
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(
            reverse(
                "api:source-get-random-quote",
                kwargs={"source": char_to_retrieve.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK

    def test_random_quote_empty_source(self, apiclient, property_group):
        apiclient.force_authenticate(user=property_group.owner)
        source = Source.objects.create(name="Bobble the Elder", group=property_group, owner=property_group.owner)
        response = apiclient.get(reverse("api:source-get-random-quote", kwargs={"source": source.slug}))
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_source_generate_sentence(self, apiclient, property_group):
        char_to_retrieve = property_group.source_set.filter(allow_markov=True)[0]
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(
            reverse(
                "api:source-generate-sentence",
                kwargs={"source": char_to_retrieve.slug},
            )
        )
        assert response.status_code in [status.HTTP_200_OK, status.HTTP_204_NO_CONTENT]
        if response.status_code == status.HTTP_200_OK:
            assert response.data["sentence"] is not None

    def test_disallowed_source_generate_sentence(self, apiclient, property_group):
        char_to_retrieve = property_group.source_set.filter(allow_markov=False)[0]
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(
            reverse(
                "api:source-generate-sentence",
                kwargs={"source": char_to_retrieve.slug},
            )
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_empty_source_generate_sentence(self, apiclient, property_group):
        char_to_retrieve = Source.objects.create(
            name="I say nothing",
            group=property_group,
            owner=property_group.owner,
            allow_markov=True,
        )
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(
            reverse(
                "api:source-generate-sentence",
                kwargs={"source": char_to_retrieve.slug},
            )
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
