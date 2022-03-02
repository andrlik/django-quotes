import pytest
from django.test import RequestFactory
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

from django_quotes.api.serializers import CharacterSerializer
from django_quotes.api.views import CharacterGroupViewSet
from django_quotes.models import Character, CharacterGroup
from tests.factories.users import UserFactory

pytestmark = pytest.mark.django_db(transaction=True)


@pytest.fixture
def apiclient():
    return APIClient()


class TestGroupViewSet:
    def test_list_groups(
        self, property_group: CharacterGroup, rf: RequestFactory
    ) -> None:
        view = CharacterGroupViewSet()
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
        group = CharacterGroup.objects.create(name="Nothing here", owner=user)
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
        response = apiclient.get(
            reverse(
                "api:group-generate-sentence", kwargs={"group": property_group.slug}
            )
        )
        assert response.status_code == status.HTTP_200_OK

    def test_disallowed_markov_group(self, apiclient):
        user = UserFactory()
        group = CharacterGroup.objects.create(name="Nothing here", owner=user)
        Character.objects.create(
            name="No Fun", group=group, owner=user, allow_markov=False
        )
        apiclient.force_authenticate(user=user)
        response = apiclient.get(
            reverse("api:group-generate-sentence", kwargs={"group": group.slug})
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_empty_markov_group(self, apiclient):
        user = UserFactory()
        group = CharacterGroup.objects.create(name="Nothing here", owner=user)
        Character.objects.create(
            name="No Fun", group=group, owner=user, allow_markov=True
        )
        apiclient.force_authenticate(user=user)
        response = apiclient.get(
            reverse("api:group-generate-sentence", kwargs={"group": group.slug})
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT


class TestCharacterViewSet:
    def test_list_characters(self, apiclient, property_group):
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(reverse("api:character-list"))
        assert response.status_code == status.HTTP_200_OK

    def test_list_characters_by_group(self, apiclient, property_group):
        apiclient.force_authenticate(user=property_group.owner)
        extra_group = CharacterGroup.objects.create(
            name="I'm extra", owner=property_group.owner
        )
        Character.objects.create(
            name="Bobble the Odd", group=extra_group, owner=property_group.owner
        )
        response = apiclient.get(
            reverse("api:character-list") + f"?group={property_group.slug}"
        )
        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == property_group.character_set.count()

    def test_filter_by_nonexistent_group(self, apiclient, property_group):
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(reverse("api:character-list") + "?group=sayonara")
        assert len(response.data) == 0
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_character(self, apiclient, property_group):
        char_to_retrieve = property_group.character_set.all()[0]
        serializer = CharacterSerializer(char_to_retrieve)
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(
            reverse("api:character-detail", kwargs={"character": char_to_retrieve.slug})
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data == serializer.data

    def test_character_random_quote(self, apiclient, property_group):
        char_to_retrieve = property_group.character_set.all()[0]
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(
            reverse(
                "api:character-get-random-quote",
                kwargs={"character": char_to_retrieve.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK

    def test_random_quote_empty_character(self, apiclient, property_group):
        apiclient.force_authenticate(user=property_group.owner)
        character = Character.objects.create(
            name="Bobble the Elder", group=property_group, owner=property_group.owner
        )
        response = apiclient.get(
            reverse(
                "api:character-get-random-quote", kwargs={"character": character.slug}
            )
        )
        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_character_generate_sentence(self, apiclient, property_group):
        char_to_retrieve = property_group.character_set.filter(allow_markov=True)[0]
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(
            reverse(
                "api:character-generate-sentence",
                kwargs={"character": char_to_retrieve.slug},
            )
        )
        assert response.status_code == status.HTTP_200_OK
        assert response.data["sentence"] is not None

    def test_disallowed_character_generate_sentence(self, apiclient, property_group):
        char_to_retrieve = property_group.character_set.filter(allow_markov=False)[0]
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(
            reverse(
                "api:character-generate-sentence",
                kwargs={"character": char_to_retrieve.slug},
            )
        )
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_empty_character_generate_sentence(self, apiclient, property_group):
        char_to_retrieve = Character.objects.create(
            name="I say nothing",
            group=property_group,
            owner=property_group.owner,
            allow_markov=True,
        )
        apiclient.force_authenticate(user=property_group.owner)
        response = apiclient.get(
            reverse(
                "api:character-generate-sentence",
                kwargs={"character": char_to_retrieve.slug},
            )
        )
        assert response.status_code == status.HTTP_204_NO_CONTENT
